// Function to update the active tasks count
function updateActiveTasksCount(count) {
    document.getElementById('activeTasks').textContent = count;
}

// Handle form submission
document.getElementById('taskForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const taskType = e.target.dataset.type;
    const data = Object.fromEntries(formData.entries());

    try {
        const response = await fetch(`/api/${taskType}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            const responseData = await response.json();
            updateActiveTasksCount(responseData.active_tasks);
            window.location.reload();
        }
    } catch (error) {
        console.error('Error:', error);
    }
});

// Filter between area and products
document.addEventListener('DOMContentLoaded', () => {
    const locationSelect = document.getElementById('target_area');
    const itemSelect = document.getElementById('target_product');
    const clearButton = document.getElementById('clear-button');

    const allOptions = Array.from(itemSelect.options);

    locationSelect.addEventListener('change', () => {
        const selectedLocation = locationSelect.value;

        const filteredOptions = allOptions.filter(option => {
            return option.dataset.location === selectedLocation || option.value === "";
        });

        itemSelect.innerHTML = ""; 
        filteredOptions.forEach(option => itemSelect.appendChild(option)); 
    });

    itemSelect.addEventListener('change', () => {
        const selectedItem = itemSelect.selectedOptions[0]; 
        const correspondingLocation = selectedItem.dataset.location; 

        if (!locationSelect.value && correspondingLocation) {
            locationSelect.value = correspondingLocation;
            locationSelect.dispatchEvent(new Event('change'));
        }
    });

    clearButton.addEventListener('click', () => {
        locationSelect.value = ""; 
        itemSelect.value = ""; 
        allOptions.forEach(option => itemSelect.appendChild(option)); 
    });
});