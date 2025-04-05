// Global variables
let currentForce = [];
let currentScale = 1;
let maxPoints = 32;

// DOM Elements
let unitTypeSelect;
let unitSelect;
let regularRadio;
let veteranRadio;
let addUnitButton;
let forceList;
let forceListItems;
let previewCard;
let cardPreview;
let totalPointsBadge;
let totalPointsSpan;
let deleteForceButton;
let printForceButton;
let maxPointsInput;

// Initialize
function init() {
    // Get DOM elements
    unitTypeSelect = document.getElementById('unitType');
    unitSelect = document.getElementById('unitSelect');
    regularRadio = document.getElementById('regular');
    veteranRadio = document.getElementById('veteran');
    addUnitButton = document.getElementById('addUnit');
    forceList = document.getElementById('forceList');
    forceListItems = document.getElementById('forceListItems');
    previewCard = document.getElementById('previewCard');
    cardPreview = document.getElementById('cardPreview');
    totalPointsBadge = document.getElementById('totalPointsBadge');
    totalPointsSpan = document.getElementById('totalPoints');
    deleteForceButton = document.getElementById('deleteForce');
    printForceButton = document.getElementById('printForce');
    maxPointsInput = document.getElementById('maxPoints');

    // Add event listeners
    unitTypeSelect.addEventListener('change', updateUnitList);
    unitSelect.addEventListener('change', updateCardPreview);
    addUnitButton.addEventListener('click', addUnitToForce);
    deleteForceButton.addEventListener('click', deleteForce);
    printForceButton.addEventListener('click', printForce);
    maxPointsInput.addEventListener('change', updateMaxPoints);

    // Scale buttons
    document.getElementById('scale1').addEventListener('click', () => setScale(1));
    document.getElementById('scale2').addEventListener('click', () => setScale(2));
    document.getElementById('scale3').addEventListener('click', () => setScale(3));

    // Set initial unit type to vehicle and load units
    unitTypeSelect.value = "vehicle";
    updateUnitList();
    
    // Select the first unit in the list
    if (unitSelect.options.length > 1) { // Check if there are units available
        unitSelect.selectedIndex = 1; // Select the first unit (index 0 is the placeholder)
        updateCardPreview(); // Update the card preview
    }
    
    // Update total points
    updateTotalPoints();
}

// Update unit list based on selected type
function updateUnitList() {
    const selectedType = unitTypeSelect.value;
    unitSelect.innerHTML = '<option value="">Choose a unit...</option>';
    
    // Map the select value to the correct Type value
    const typeMapping = {
        'vehicle': ['Vehicle', 'VEHICLE', 'vehicle'],
        'protomech': ['Protomech', 'PROTOMECH', 'protomech', 'ProtoMech', 'Proto-Mech'],
        'battlearmor': ['BattleArmor', 'BATTLEARMOR', 'battlearmor', 'Battle Armor'],
        'infantry': ['Infantry', 'INFANTRY', 'infantry']
    };
    
    const correctType = typeMapping[selectedType];
    
    // Filter units based on type
    const filteredUnits = unitData.filter(unit => {
        return unit.UnitType && correctType.some(type => 
            unit.UnitType.toLowerCase() === type.toLowerCase()
        );
    });
    
    // Sort units by name
    filteredUnits.sort((a, b) => a.Name.localeCompare(b.Name));
    
    filteredUnits.forEach(unit => {
        const option = document.createElement('option');
        option.value = unit.FullName;
        option.textContent = `${unit.Name} (PV: ${unit.RegPV}/${unit.VetPV})`;
        unitSelect.appendChild(option);
    });
    
    cardPreview.style.display = 'none';
    previewCard.src = '';
}

// Update card preview
function updateCardPreview() {
    const selectedUnit = unitSelect.value;
    if (selectedUnit) {
        const unitType = unitTypeSelect.value;
        const unit = unitData.find(u => u.FullName === selectedUnit);
        if (unit) {
            const cardPath = `Cards/${unit.FullName.replace(/\//g, '-')}.gif`;
            previewCard.src = cardPath;
            cardPreview.style.display = 'block';
        }
    } else {
        cardPreview.style.display = 'none';
        previewCard.src = '';
    }
}

// Add unit to force
function addUnitToForce() {
    const selectedUnit = unitSelect.value;
    if (!selectedUnit) return;
    
    const unitType = unitTypeSelect.value;
    const unit = unitData.find(u => u.FullName === selectedUnit);
    if (!unit) return;
    
    const isVeteran = veteranRadio.checked;
    const pv = isVeteran ? unit.VetPV : unit.RegPV;
    
    const forceUnit = {
        ...unit,
        PV: pv,
        isVeteran
    };
    
    currentForce.push(forceUnit);
    updateForceList();
    updateTotalPoints();
    
    // Keep the unit selected and preview visible
    // Don't reset the selection
}

// Update force list display
function updateForceList() {
    // Update the card display
    forceList.innerHTML = '';
    
    currentForce.forEach((unit, index) => {
        const cardDiv = document.createElement('div');
        cardDiv.className = 'unit-card';
        
        const img = document.createElement('img');
        img.src = `Cards/${unit.FullName.replace(/\//g, '-')}.gif`;
        img.alt = unit.FullName;
        
        const removeButton = document.createElement('button');
        removeButton.className = 'btn btn-danger btn-sm position-absolute top-0 end-0 m-2';
        removeButton.innerHTML = '&times;';
        removeButton.onclick = () => removeUnit(index);
        
        cardDiv.appendChild(img);
        cardDiv.appendChild(removeButton);
        forceList.appendChild(cardDiv);
    });
    
    // Update the force list items
    forceListItems.innerHTML = '';
    
    currentForce.forEach((unit, index) => {
        const listItem = document.createElement('li');
        listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
        
        const unitInfo = document.createElement('div');
        unitInfo.innerHTML = `
            <strong>${unit.Name}</strong>
            <span class="badge ${unit.isVeteran ? 'bg-warning' : 'bg-info'} ms-2">${unit.isVeteran ? 'Veteran' : 'Regular'}</span>
            <span class="badge bg-primary ms-2">${unit.PV} PV</span>
        `;
        
        const removeButton = document.createElement('button');
        removeButton.className = 'btn btn-danger btn-sm';
        removeButton.innerHTML = '&times;';
        removeButton.onclick = () => removeUnit(index);
        
        listItem.appendChild(unitInfo);
        listItem.appendChild(removeButton);
        forceListItems.appendChild(listItem);
    });
}

// Remove unit from force
function removeUnit(index) {
    currentForce.splice(index, 1);
    updateForceList();
    updateTotalPoints();
}

// Update total points
function updateTotalPoints() {
    const total = currentForce.reduce((sum, unit) => sum + unit.PV, 0);
    totalPointsSpan.textContent = total;
    
    // Update badge color and text based on points
    if (total > maxPoints) {
        totalPointsBadge.classList.remove('bg-primary');
        totalPointsBadge.classList.add('bg-danger');
        totalPointsBadge.textContent = `Total Points Exceeded! (${total - maxPoints} over limit)`;
    } else {
        totalPointsBadge.classList.remove('bg-danger');
        totalPointsBadge.classList.add('bg-primary');
        totalPointsBadge.textContent = `Total Points: ${total}`;
    }
}

// Set scale
function setScale(scale) {
    currentScale = scale;
    document.querySelectorAll('.unit-card').forEach(card => {
        card.style.transform = `scale(${scale})`;
    });
}

// Update max points
function updateMaxPoints() {
    maxPoints = parseInt(maxPointsInput.value) || 32;
    updateTotalPoints();
}

// Delete force
function deleteForce() {
    if (confirm('Are you sure you want to delete the entire force?')) {
        currentForce = [];
        updateForceList();
        updateTotalPoints();
    }
}

// Print force
function printForce() {
    // Create a new window
    const printWindow = window.open('', '_blank');
    if (!printWindow) {
        alert('Please allow popups for this site to print your force.');
        return;
    }

    // Create the print page HTML
    const printContent = `
        <!DOCTYPE html>
        <html>
        <head>
            <title>BattleTech Force - Print View</title>
            <style>
                @page {
                    margin: 0;
                    padding: 0;
                }
                body {
                    margin: 0;
                    padding: 0;
                    background: white;
                }
                .card-container {
                    display: grid;
                    grid-template-columns: repeat(3, 3.5in);
                    grid-template-rows: repeat(3, 2.5in);
                    gap: 0.1in;
                    justify-content: center;
                    padding: 0.5in;
                    margin: 0;
                }
                .unit-card {
                    width: 3.5in;
                    height: 2.5in;
                    border: 1px solid #ccc;
                    padding: 0;
                    margin: 0;
                    text-align: center;
                    page-break-inside: avoid;
                    transform: rotate(90deg);
                    transform-origin: top left;
                    position: relative;
                    left: 0;
                    margin-left: 2.5in;
                }
                .unit-card img {
                    width: 100%;
                    height: 100%;
                    object-fit: contain;
                }
                .force-list {
                    margin-top: 2.5in;
                    padding: 0.5in;
                    page-break-before: always;
                }
                .force-list h3 {
                    margin-bottom: 0.5in;
                }
                .force-list ul {
                    list-style: none;
                    padding: 0;
                    margin: 0;
                }
                .force-list li {
                    margin-bottom: 0.2in;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                .force-list .badge {
                    margin-left: 0.2in;
                }
                @media print {
                    body {
                        padding: 0;
                        margin: 0;
                    }
                    .card-container {
                        padding: 0.5in;
                        margin: 0;
                    }
                }
            </style>
        </head>
        <body>
            <div class="card-container" id="cardContainer"></div>
            <div class="force-list">
                <h3>Force List</h3>
                <ul id="forceListItems"></ul>
            </div>
            <script>
                // Function to create and load images
                function loadImages() {
                    const container = document.getElementById('cardContainer');
                    const forceListItems = document.getElementById('forceListItems');
                    const units = ${JSON.stringify(currentForce)};
                    
                    // Create cards
                    units.forEach(unit => {
                        const cardDiv = document.createElement('div');
                        cardDiv.className = 'unit-card';
                        
                        const img = document.createElement('img');
                        img.src = 'Cards/' + unit.FullName.replace(/\\//g, '-') + '.gif';
                        img.alt = unit.FullName;
                        
                        cardDiv.appendChild(img);
                        container.appendChild(cardDiv);
                    });
                    
                    // Create force list
                    units.forEach(unit => {
                        const listItem = document.createElement('li');
                        listItem.innerHTML = \`
                            <div>
                                <strong>\${unit.Name}</strong>
                                <span class="badge \${unit.isVeteran ? 'bg-warning' : 'bg-info'}">\${unit.isVeteran ? 'Veteran' : 'Regular'}</span>
                                <span class="badge bg-primary">\${unit.PV} PV</span>
                            </div>
                        \`;
                        forceListItems.appendChild(listItem);
                    });
                    
                    // Wait for all images to load
                    const images = document.querySelectorAll('#cardContainer .unit-card img');
                    let loadedImages = 0;
                    
                    function checkAllLoaded() {
                        loadedImages++;
                        if (loadedImages === images.length) {
                            // All images loaded, print after a short delay
                            setTimeout(() => {
                                window.print();
                                // Close the window after printing
                                setTimeout(() => window.close(), 1000);
                            }, 500);
                        }
                    }
                    
                    images.forEach(img => {
                        if (img.complete) {
                            checkAllLoaded();
                        } else {
                            img.onload = checkAllLoaded;
                            img.onerror = () => {
                                console.error('Failed to load image: ' + img.src);
                                checkAllLoaded();
                            };
                        }
                    });
                    
                    // Fallback in case some images don't trigger onload
                    setTimeout(() => {
                        window.print();
                        setTimeout(() => window.close(), 1000);
                    }, 15000);
                }
                
                // Start loading images when the window is ready
                window.onload = loadImages;
            </script>
        </body>
        </html>
    `;

    // Write the content to the new window
    printWindow.document.write(printContent);
    printWindow.document.close();
}

// Initialize on load
document.addEventListener('DOMContentLoaded', init); 