import queue
from flask import Flask, request, jsonify
import requests
import os
from concurrent.futures import ThreadPoolExecutor
# from vision import check_product
from tmp import check_product
class ServerService:
    def __init__(self, ui_port=5000, nav_port=5001, server_port=5003):
        super().__init__()
        self.app = Flask(__name__)
        self.UI_ENDPOINT = f"http://127.0.0.1:{ui_port}"
        self.NAV_ENDPOINT = f"http://127.0.0.1:{nav_port}"
        self.server_port = server_port
        self.task = queue.Queue()

        self.coordinate_dict = {
            'Entrance': 1,
            'Vase Area': 2,
            'Keyboard Area': 3,
            'Bottle Area': 4,
            'Cup Area': 5,
            'Stock': 6
        }   

        self._setup_routes()
    
    def _setup_routes(self):
        print("Setting up routes...")
        self.app.route('/api/set_product', methods=['POST'])(self.set_product)
        self.app.route('/navigate2product_end', methods=['POST'])(self.navigate2product_end)
        self.app.route('/navigate2stock', methods=['POST'])(self.navigate2stock)
    
    def run(self):
        self.app.run(port=self.server_port, debug=True, use_reloader=False)
    
    def set_product(self):
        data = request.json
        target_area = data['target_area']
        id = data['id']
        task_type = data['task_type']
        target_product = data['target_product']
        self.task.put((target_area, id, task_type, target_product))
        try:
            response = requests.post(f"{self.NAV_ENDPOINT}/navigate2product", 
                                    json={"c_product": self.coordinate_dict.get(target_area)})
            return response.json()
        except Exception as e :
            print(f"Set product error: {str(e)}")
            return {"error": f"set product error: {str(e)}"}
    
    def navigate2product_end(self):
        data = request.json
        state = data.get("state")
        if not state:
            print("Navigate state fail")
            return
        else:
            print("Navigation task successed.")
        
        target_area, id, task_type, target_product = self.task.get()
        print(f"Navigate state: {target_area}, {id}, {task_type}, {target_product}")

        def call_ui():
            try:
                response = requests.post(f'{self.UI_ENDPOINT}/api/robot/arrived',
                                            json={'id': id, 'target_area': target_area, 'target_product': target_product})
                print("Successfully informed UI that robot arrived.")
                return response.json()  # Return the JSON content
            except Exception as e:
                print(f"Error notifying UI: {e}")
                return {"error": str(e)}

        def call_vision():
            try:
                product = check_product(target_product)
                if product != "None":
                    requests.post(f'{self.UI_ENDPOINT}/api/append_restock_deque', json={'product': target_product})
                    print(f"Successfully call the append restock deque api to append {target_product}")
                    return {"status": "restock", "product": target_product}
                else:
                    print("No need to restock after scanning.")
                    return {"status": "no_restock"}
            except Exception as e:
                return {"error": str(e)}
        
        if task_type == "restock":
            ui_result = call_ui()
            return ({"status": "success", "ui_result": ui_result}), 200
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(call_ui): "UI",
                executor.submit(call_vision): "vision"
            }
            results = {}
            for future in futures:
                try:
                    results[futures[future]] = future.result()
                except Exception as e:
                    results[futures[future]] = {"error": f"UI or Vision error occurred: {str(e)}"}

        return ({"status": "success","results": results}), 200

    def navigate2stock(self):
        print("Start navigate to stock")
        try:
            response = requests.post(f"{self.NAV_ENDPOINT}/navigate2stock", json={"c_stock": self.coordinate_dict.get("Stock")})
            print("Navigate request success")
            return response.json(), 200
        except Exception as e:
            print(f"Navigation request fail: {str(e)}")
            return {"error": f"product restock error: {str(e)}"}, 500

if __name__ == '__main__':
    ServerService().run()