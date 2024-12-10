import requests
def check_task_completion(task_id):
    # When robot arrives at destination
    try:
        response = requests.post(f'http://127.0.0.1:5000/api/robot/arrived',
                                    json={'task_id': task_id})
        return response.json()
    except Exception as e:
        print(f"Error notifying server: {e}")
print(check_task_completion(1))