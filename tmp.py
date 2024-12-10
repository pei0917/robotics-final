from selenium import webdriver
import time
from selenium.webdriver.common.by import By
# Initialize the Selenium WebDriver
driver = webdriver.Chrome()

# Load your HTML page
driver.get("http://127.0.0.1:5000/navigation")

# # # Optionally inject the JavaScript file dynamically (if not linked in the HTML)
# # with open("./static/js/functions.js", "r") as js_file:
# #     js_code = js_file.read()
# #     driver.execute_script(js_code)

# # Call the JavaScript function
# driver.execute_script("showCompletionPopup()")

# # Pause to see the popup (optional)
# while True:
#     time.sleep(5)
driver.find_element(By.ID, "target_area").send_keys("Entrance")
driver.find_element(By.ID, "target_product").send_keys("None")

# Trigger form submission
driver.execute_script("""
    document.getElementById('taskForm').dispatchEvent(new Event('submit', { bubbles: true }));
""")

# Wait to observe the results (if needed)
time.sleep(5)

# Close the browser
driver.quit()
# # Close the browser
# driver.quit()

