// Function to update the active tasks count
function updateActiveTasksCount(count) {
    document.getElementById('activeTasks').textContent = count;
}

// Close the pop up window
function closePopup() {
    const overlay = document.getElementById('overlay');
    const popup = document.getElementById('completionPopup');
    if (overlay) document.body.removeChild(overlay);
    if (popup) document.body.removeChild(popup);
}

// Function to show completion popup
function showCompletionPopup(targetArea, targetProduct) {
    // Create overlay
    const overlay = document.createElement('div');
    overlay.id = 'overlay';
    document.body.appendChild(overlay);

    // Create popup
    const popup = document.createElement('div');
    popup.id = 'completionPopup';
    popup.className = 'p-6 text-center w-96';
    popup.innerHTML = `
        <h2 class="text-xl font-bold mb-4">We Are Arrived!</h2>
        <p class="mb-4">What would you like to do next?</p>
        <div class="space-y-2">
            <button onclick="window.location.reload()" class="w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600">
                Create New Navigation Task
            </button>
            <button onclick="handleRestockOption('${targetArea}', '${targetProduct}')" class="w-full bg-green-500 text-white py-2 rounded hover:bg-green-600">
                Restock Products
            </button>
            <button onclick="showPopupAndWait('We have announced the clerk. Please wait.')" class="w-full bg-yellow-500 text-white py-2 rounded hover:bg-yellow-600">
                Ask Clerk Questions
            </button>
            <button onclick="window.location.href = '/'" class="w-full bg-gray-500 text-white py-2 rounded hover:bg-gray-600">
                I'm Fine Now
            </button>
        </div>
    `;
    document.body.appendChild(popup);
}

// Modify the pop up window text
function showPopupAndWait(message) {
    return new Promise((resolve) => {
        const popup = document.getElementById('completionPopup');
        popup.innerHTML = `
            <div class="flex justify-center mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-yellow-400 mr-1" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/>
                </svg>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-yellow-400 mr-1" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/>
                </svg>
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-yellow-400" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"/>
                </svg>
            </div>
            <p class="mb-4 text-center text-gray-700">${message}</p>
            <button id="popupOkButton" class="w-full bg-blue-600 text-white py-2 rounded-lg transition duration-300 ease-in-out transform hover:bg-blue-700 hover:scale-105 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50">
                OK
            </button>
        `;
        const okButton = document.getElementById('popupOkButton');
        okButton.addEventListener('click', () => {
            closePopup();
            window.location.reload();
            resolve();
        });
    });
}

// Handle restock option selection
async function handleRestockOption(targetArea, targetProduct) {
    await showPopupAndWait('We have announced the clerk to restock. You can go around and come back after 5 minutes.');
    const data = {
        target_area: targetArea,
        target_product: targetProduct
    };
    fetch(`/api/restock`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    }).catch(error => {
        console.error('Error:', error);
    });
    window.location.href = '/restock';
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