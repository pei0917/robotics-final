// Function to update the active tasks count
function updateActiveTasksCount(count) {
    document.getElementById('activeTasks').textContent = count;
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
            <button onclick="handlePopupOption(1)" class="w-full bg-blue-500 text-white py-2 rounded hover:bg-blue-600">
                Create New Navigation Task
            </button>
            <button onclick="handleRestockOption('${targetArea}', '${targetProduct}')" class="w-full bg-green-500 text-white py-2 rounded hover:bg-green-600">
                Restock Products
            </button>
            <button onclick="handlePopupOption(3)" class="w-full bg-yellow-500 text-white py-2 rounded hover:bg-yellow-600">
                Ask Clerk Questions
            </button>
            <button onclick="handlePopupOption(4)" class="w-full bg-gray-500 text-white py-2 rounded hover:bg-gray-600">
                I'm Fine Now
            </button>
        </div>
    `;
    document.body.appendChild(popup);
}

// Handle restock option selection
async function handleRestockOption(targetArea, targetProduct) {

    const overlay = document.getElementById('overlay');
    const popup = document.getElementById('completionPopup');
    
    if (overlay) document.body.removeChild(overlay);
    if (popup) document.body.removeChild(popup);

    alert('We have announced the clerk to restock. You can go around and come back after 5 minutes.');
    try {
        const data = {
            target_area: targetArea,
            target_product: targetProduct
        };
        const response = await fetch(`/api/restock`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            window.location.href = "/restock";
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

// Handle popup option selection
function handlePopupOption(option) {
    const overlay = document.getElementById('overlay');
    const popup = document.getElementById('completionPopup');
    
    if (overlay) document.body.removeChild(overlay);
    if (popup) document.body.removeChild(popup);

    switch(option) {
        case 1:
            break;
        case 3:
            alert('We have announced the clerk. Please wait.');
            break;
        case 4:
            window.location.href = "/";
            return;
    }
    window.location.reload();
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