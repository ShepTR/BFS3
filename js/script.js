// Global variables
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
let currentScale = 1;
let maxPoints = 32;

// Initialize global force array
window.currentForce = [];

// Initialize
function init() {
    console.log('Initializing application...');
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

    console.log('DOM elements initialized');

    // Add event listeners
    unitTypeSelect.addEventListener('change', updateUnitList);
    unitSelect.addEventListener('change', updateCardPreview);
    addUnitButton.addEventListener('click', addUnitToForce);
    deleteForceButton.addEventListener('click', deleteForce);
    printForceButton.addEventListener('click', printForce);
    maxPointsInput.addEventListener('change', updateMaxPoints);

    console.log('Event listeners added');

    // Initialize play force functionality
    initPlayForce();
    console.log('Play force functionality initialized');

    // Scale buttons
    document.getElementById('scale1').addEventListener('click', () => {
        currentScale = 1;
        document.getElementById('scale1').classList.add('active');
        document.getElementById('scale2').classList.remove('active');
        document.getElementById('scale3').classList.remove('active');
        maxPoints = 32;
        maxPointsInput.value = maxPoints;
        updateTotalPoints();
        updateForceList();
    });

    document.getElementById('scale2').addEventListener('click', () => {
        currentScale = 2;
        document.getElementById('scale1').classList.remove('active');
        document.getElementById('scale2').classList.add('active');
        document.getElementById('scale3').classList.remove('active');
        maxPoints = 64;
        maxPointsInput.value = maxPoints;
        updateTotalPoints();
        updateForceList();
    });

    document.getElementById('scale3').addEventListener('click', () => {
        currentScale = 3;
        document.getElementById('scale1').classList.remove('active');
        document.getElementById('scale2').classList.remove('active');
        document.getElementById('scale3').classList.add('active');
        maxPoints = 96;
        maxPointsInput.value = maxPoints;
        updateTotalPoints();
        updateForceList();
    });

    console.log('Scale buttons initialized');

    // Set initial unit type to common and load units
    unitTypeSelect.value = "common";
    updateUnitList();
    
    console.log('Initial unit list updated');
    
    // Select the first unit in the list
    if (unitSelect.options.length > 0) { // Check if there are units available
        unitSelect.selectedIndex = 0; // Select the first unit
        updateCardPreview(); // Update the card preview
        console.log('First unit selected and preview updated');
    }
    
    // Set initial max points based on scale
    maxPoints = currentScale * 32;
    maxPointsInput.value = maxPoints;
    
    // Update total points
    updateTotalPoints();
    
    console.log('Initialization complete');
}

// Wait for the page to load and units data to be available
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM Content Loaded');
    // Check if units data is available
    if (typeof units === 'undefined') {
        console.error('Units data not loaded!');
        return;
    }
    console.log('Units data loaded:', units.length, 'units available');
    
    // Initialize the application
    init();
});

// Update unit list based on selected type
function updateUnitList() {
    const selectedType = unitTypeSelect.value;
    console.log('Selected unit type:', selectedType);
    
    // Clear current options
    unitSelect.innerHTML = '';
    
    // Filter units by type and sort by name
    const filteredUnits = units.filter(unit => {
        if (selectedType === 'common') {
            return unit.Common === '!';
        }
        // Convert both to lowercase for comparison
        const unitType = unit.UnitType.toLowerCase();
        const selectedTypeLower = selectedType.toLowerCase();
        console.log('Comparing unit type:', unitType, 'with selected type:', selectedTypeLower);
        return unitType === selectedTypeLower;
    }).sort((a, b) => a.Name.localeCompare(b.Name));
    
    console.log('Filtered units:', filteredUnits.length);
    
    // Add filtered units to select
    filteredUnits.forEach(unit => {
        const option = document.createElement('option');
        option.value = unit.FullName;
        const displayName = selectedType === 'battlearmor' ? unit.FullName : unit.Name;
        option.textContent = `${displayName} (${unit.RegPV}/${unit.VetPV})`;
        unitSelect.appendChild(option);
    });
    
    // Select first unit if available
    if (unitSelect.options.length > 0) {
        unitSelect.selectedIndex = 0;
        updateCardPreview();
    }
}

// Update card preview
function updateCardPreview() {
    const selectedUnit = unitSelect.value;
    const cardPreviewContainer = document.getElementById('cardPreview');
    const previewCardImg = document.getElementById('previewCard');
    
    console.log('Updating preview for unit:', selectedUnit);
    
    if (!selectedUnit) {
        cardPreviewContainer.style.display = 'none';
        return;
    }
    
    const unit = units.find(u => u.FullName === selectedUnit);
    if (unit) {
        const imagePath = 'Cards/' + unit.FullName.replace(/\//g, '-') + '.gif';
        console.log('Loading card image:', imagePath);
        
        previewCardImg.src = imagePath;
        cardPreviewContainer.style.display = 'block';
        
        previewCardImg.onerror = function() {
            console.error('Failed to load card image:', imagePath);
            cardPreviewContainer.style.display = 'none';
        };
    }
}

// Add unit to force
function addUnitToForce() {
    const selectedUnit = unitSelect.value;
    if (!selectedUnit) {
        alert('Please select a unit first.');
        return;
    }
    
    const unit = units.find(u => u.FullName === selectedUnit);
    if (unit) {
        const isVeteran = veteranRadio.checked;
        currentForce.push({
            ...unit,
            isVeteran: isVeteran
        });
        
        updateForceList();
        updateTotalPoints();
    }
}

// Update force list display
function updateForceList() {
    forceList.innerHTML = '';
    forceListItems.innerHTML = '';
    
    // Group units by type
    const groupedUnits = {};
    currentForce.forEach(unit => {
        if (!groupedUnits[unit.UnitType]) {
            groupedUnits[unit.UnitType] = [];
        }
        groupedUnits[unit.UnitType].push(unit);
    });
    
    // Create list items for each group
    Object.entries(groupedUnits).forEach(([type, units]) => {
        // Create section for this unit type
        const typeSection = document.createElement('div');
        typeSection.className = 'unit-type-section';
        
        // Add type header
        const typeHeader = document.createElement('h5');
        typeHeader.textContent = type;
        typeSection.appendChild(typeHeader);
        
        // Create card container for this type
        const cardContainer = document.createElement('div');
        cardContainer.className = 'card-container';
        
        // Add units of this type
        units.forEach(unit => {
            // Create card display
            const cardDiv = document.createElement('div');
            cardDiv.className = 'unit-card';
            
            const imgContainer = document.createElement('div');
            imgContainer.style.flex = '1';
            imgContainer.style.display = 'flex';
            imgContainer.style.alignItems = 'center';
            imgContainer.style.justifyContent = 'center';
            
            const img = document.createElement('img');
            img.src = 'Cards/' + unit.FullName.replace(/\//g, '-') + '.gif';
            img.alt = unit.Name;
            
            const pointValue = unit.isVeteran ? unit.VetPV : unit.RegPV;
            const cardInfo = document.createElement('div');
            cardInfo.className = 'card-info';
            cardInfo.innerHTML = `
                <strong>${unit.Name}</strong>
                <div style="margin-top: 5px;">
                    <span class="badge ${unit.isVeteran ? 'bg-warning' : 'bg-info'}">${unit.isVeteran ? 'Veteran' : 'Regular'}</span>
                    <span class="badge bg-primary">${pointValue} PV</span>
                </div>
            `;
            
            const deleteButton = document.createElement('button');
            deleteButton.className = 'btn btn-danger btn-sm position-absolute top-0 end-0 m-2';
            deleteButton.innerHTML = '&times;';
            deleteButton.onclick = () => {
                const index = currentForce.indexOf(unit);
                if (index > -1) {
                    currentForce.splice(index, 1);
                    updateForceList();
                    updateTotalPoints();
                }
            };
            
            imgContainer.appendChild(img);
            cardDiv.appendChild(imgContainer);
            cardDiv.appendChild(cardInfo);
            cardDiv.appendChild(deleteButton);
            cardContainer.appendChild(cardDiv);
            
            // Create list item
            const listItem = document.createElement('li');
            listItem.className = 'list-group-item d-flex justify-content-between align-items-center';
            listItem.innerHTML = `
                <div>
                    <strong>${unit.Name}</strong>
                    <span class="badge ${unit.isVeteran ? 'bg-warning' : 'bg-info'}">${unit.isVeteran ? 'Veteran' : 'Regular'}</span>
                    <span class="badge bg-primary">${pointValue} PV</span>
                </div>
            `;
            
            const listDeleteButton = document.createElement('button');
            listDeleteButton.className = 'btn btn-danger btn-sm';
            listDeleteButton.textContent = 'Remove';
            listDeleteButton.onclick = () => {
                const index = currentForce.indexOf(unit);
                if (index > -1) {
                    currentForce.splice(index, 1);
                    updateForceList();
                    updateTotalPoints();
                }
            };
            
            listItem.appendChild(listDeleteButton);
            forceListItems.appendChild(listItem);
        });
        
        typeSection.appendChild(cardContainer);
        forceList.appendChild(typeSection);
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
    const total = currentForce.reduce((sum, unit) => {
        const pointValue = unit.isVeteran ? unit.VetPV : unit.RegPV;
        return sum + pointValue;
    }, 0);
    
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

    // Calculate total points
    const total = currentForce.reduce((sum, unit) => {
        const pointValue = unit.isVeteran ? unit.VetPV : unit.RegPV;
        return sum + pointValue;
    }, 0);

    // Create the print page HTML
    const printContent = `
        <!DOCTYPE html>
        <html>
        <head>
            <title>BattleTech Force - Print View</title>
            <style>
                @page {
                    size: landscape;
                    margin: 0.2in;
                }
                body {
                    margin: 0;
                    padding: 0;
                    background: white;
                }
                .card-container {
                    position: relative;
                    width: 10.5in;  /* 3 cards wide */
                    height: 7.5in;  /* 3 cards high */
                    margin: 0;
                    padding: 0;
                    page-break-after: always;
                }
                .unit-card {
                    position: absolute;
                    width: 3.5in;
                    height: 2.5in;
                    padding: 0.1in;
                    margin: 0;
                    text-align: center;
                    page-break-inside: avoid;
                }
                .unit-card img {
                    width: 100%;
                    height: 100%;
                    object-fit: contain;
                }
                .force-list {
                    padding: 0.5in;
                    page-break-before: always;
                }
                .force-list h3 {
                    margin-bottom: 0.2in;
                }
                .force-list .points-info {
                    margin-bottom: 0.5in;
                    font-size: 1.2em;
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
                .points-exceeded {
                    color: red;
                }
            </style>
        </head>
        <body>
            <div id="cardPages"></div>
            <div class="force-list">
                <h3>Force List</h3>
                <div class="points-info">
                    <div>Max Points: ${maxPoints}</div>
                    <div class="${total > maxPoints ? 'points-exceeded' : ''}">
                        Total Points: ${total}
                        ${total > maxPoints ? ` (${total - maxPoints} over limit)` : ''}
                    </div>
                </div>
                <ul id="forceListItems"></ul>
            </div>
            <script>
                // Function to create and load images
                function loadImages() {
                    const cardPages = document.getElementById('cardPages');
                    const forceListItems = document.getElementById('forceListItems');
                    const units = ${JSON.stringify(currentForce)};
                    
                    // Create card pages (9 cards per page)
                    for (let pageIndex = 0; pageIndex < Math.ceil(units.length / 9); pageIndex++) {
                        const cardContainer = document.createElement('div');
                        cardContainer.className = 'card-container';
                        
                        // Get units for this page
                        const pageUnits = units.slice(pageIndex * 9, (pageIndex + 1) * 9);
                        
                        // Create cards in a 3x3 grid
                        pageUnits.forEach((unit, index) => {
                            const row = Math.floor(index / 3);
                            const col = index % 3;
                            
                            const cardDiv = document.createElement('div');
                            cardDiv.className = 'unit-card';
                            cardDiv.style.left = (col * 3.5) + 'in';
                            cardDiv.style.top = (row * 2.5) + 'in';
                            
                            const img = document.createElement('img');
                            img.src = 'Cards/' + unit.FullName.replace(/\\//g, '-') + '.gif';
                            img.alt = unit.FullName;
                            
                            cardDiv.appendChild(img);
                            cardContainer.appendChild(cardDiv);
                        });
                        
                        cardPages.appendChild(cardContainer);
                    }
                    
                    // Create force list
                    units.forEach(unit => {
                        const pointValue = unit.isVeteran ? unit.VetPV : unit.RegPV;
                        const listItem = document.createElement('li');
                        listItem.innerHTML = \`
                            <div>
                                <strong>\${unit.Name}</strong>
                                <span class="badge \${unit.isVeteran ? 'bg-warning' : 'bg-info'}">\${unit.isVeteran ? 'Veteran' : 'Regular'}</span>
                                <span class="badge bg-primary">\${pointValue} PV</span>
                            </div>
                        \`;
                        forceListItems.appendChild(listItem);
                    });
                    
                    // Wait for all images to load
                    const images = document.querySelectorAll('.unit-card img');
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