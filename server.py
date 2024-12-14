import queue
from flask import Flask, request, jsonify
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from shared import Vision, coordinate_dict
import threading

class ServerService:
    def __init__(self, ui_port=5000, nav_port=5001, server_port=5003):
        super().__init__()
        self.app = Flask(__name__)
        self.UI_ENDPOINT = f"http://127.0.0.1:{ui_port}"
        self.NAV_ENDPOINT = f"http://127.0.0.1:{nav_port}"
        self.server_port = server_port
        self.id = None
        self.target_area = None
        self.target_product = None
        self.task = queue.Queue()
        self.vision = Vision()
        self._setup_routes()
    
    def _setup_routes(self):
        print("Setting up routes...")
        self.app.route('/api/set_product', methods=['POST'])(self.set_product)
        self.app.route('/navigate2product_end', methods=['POST'])(self.navigate2product_end)
    
    def run(self):
        threading.Thread(target=self.vision.run, daemon=True).start()
        self.app.run(port=self.server_port, debug=True, use_reloader=False)
    
    def set_product(self):
        data = request.json
        target_area = data['target_area']
        id = data['id']
        task_type = data['task_type']
        target_product = data['target_product']
        self.task.put((target_area, id, task_type, target_product))
        print(target_area, coordinate_dict.get(target_area))
        try:
            response = requests.post(f"{self.NAV_ENDPOINT}/navigate2product", 
                                    json={"c_product": coordinate_dict.get(target_area)})
            return response.json()
        except Exception as e :
            print(f"Set product error: {str(e)}")
            return {"error": f"set product error: {str(e)}"}
    
    def call_ui(self):
        try:
            response = requests.post(f'{self.UI_ENDPOINT}/api/robot/arrived',
                                        json={'id': self.id, 'target_area': self.target_area, 'target_product': self.target_product})
            print("Successfully informed UI that robot arrived.")
            return response.json()
        except Exception as e:
            print(f"Error notifying UI: {e}")
            return {"error": str(e)}

    def call_vision(self):
        try:
            product = self.vision.check_product(self.target_product)
            if product != "None":
                requests.post(f'{self.UI_ENDPOINT}/api/append_restock_deque', json={'product': self.target_product})
                print(f"Successfully call the append restock deque api to append {self.target_product}")
                return {"status": "restock", "product": self.target_product}
            else:
                print("No need to restock after scanning.")
                return {"status": "no_restock"}
        except Exception as e:
            return {"error": str(e)}

    def execute_ui_and_vision(self):
        tasks = {
            "UI": self.call_ui,
            "Vision": self.call_vision
        }

        results = {}

        with ThreadPoolExecutor(max_workers=len(tasks)) as executor:
            future_to_task = {executor.submit(task): name for name, task in tasks.items()}

            for future in as_completed(future_to_task):
                task_name = future_to_task[future]
                try:
                    results[task_name] = future.result()
                except Exception as e:
                    results[task_name] = {"error": f"Error occurred in {task_name}: {str(e)}"}

        return results

    def navigate2product_end(self):
        data = request.json
        state = data.get("state")
        if not state:
            print("Navigate to product fail")
            return
        else:
            print("Navigation to product successed.")
        
        target_area, id, task_type, target_product = self.task.get()
        print(f"Navigate state: {target_area}, {id}, {task_type}, {target_product}")
        self.id = id
        self.target_area = target_area
        self.target_product = target_product
        
        if task_type == "restock":
            results = self.call_ui()
            return ({"status": "success", "ui_result": results}), 200
        else:
            results = self.execute_ui_and_vision()
            return ({"status": "success", "combined_result": results}), 200

if __name__ == '__main__':
    ServerService().run()