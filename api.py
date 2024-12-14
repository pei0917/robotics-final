import requests
import time
import re
from collections import deque

coordinate_dict = {
    'Entrance': 1,
    'Vase Area': 2,
    'Keyboard Area': 3,
    'Bottle Area': 4,
    'Cup Area': 5,
    'Stock': 6
}

restock_deque = deque()

def robot_arrived(task_id, target_area, target_product):
    try:
        response = requests.post(f'http://127.0.0.1:5000/api/robot/arrived',
                                    json={'task_id': task_id, 'target_area': target_area, 'target_product': target_product})
        return response.json()
    except Exception as e:
        print(f"Error notifying server: {e}")
def restock_prdouct(targer_area, target_product):
    try:
        response = requests.post(f'http://127.0.0.1:5000/api/restock',
                                    json={'target_area': targer_area, 'target_product': target_product})
        return response.json()
    except Exception as e:
        print(f"Error notifying server: {e}")
def append_restock_deque(target_product): 
    if target_product != "None":
        requests.post(f'http://127.0.0.1:5000/api/append_restock_deque', json={'product': target_product})
        print(f"Successfully call the append restock deque api to append {target_product}")
        return {"status": "restock", "product": target_product}
    else:
        print("No need to restock after scanning.")
        return {"status": "no_restock"}
def check_product(target_product):
    time.sleep(3)
    target_product = re.sub(r'_\d+', '', target_product).lower()
    return target_product
