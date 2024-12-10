import requests
def check_task_completion(task_id, target_area, target_product):
    # When robot arrives at destination
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

# print(check_task_completion(1, 'Lamp Area', 'Lamp_1'))
print(restock_prdouct('Lamp Area', 'Lamp_1'))