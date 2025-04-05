// Global variables
let selectedUnits = [];
let totalPoints = 0;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Add event listener for unit type change
    document.getElementById('unitType').addEventListener('change', function() {
        const unitType = this.value;
        populateUnitSelect(unitType);
        // Clear the card preview when type changes
        document.getElementById('cardPreview').style.display = 'none';
    });
    
    // Initialize with vehicles
    populateUnitSelect('vehicle');
    
    // Add event listeners
    document.getElementById('addUnit').addEventListener('click', addUnitToForce);
    document.getElementById('printForce').addEventListener('click', printForce);
    document.getElementById('unitSelect').addEventListener('change', updateCardPreview);
    document.getElementById('maxPoints').addEventListener('input', updateForceDisplay);
    
    // Add scale button event listeners
    document.getElementById('scale1').addEventListener('click', () => setMaxPoints(32));
    document.getElementById('scale2').addEventListener('click', () => setMaxPoints(64));
    document.getElementById('scale3').addEventListener('click', () => setMaxPoints(96));
    
    // Set initial scale to 1
    setMaxPoints(32);
    
    // Initialize version
    updateVersion();
});

// Populate the unit select dropdown based on unit type
function populateUnitSelect(unitType) {
    const select = document.getElementById('unitSelect');
    select.innerHTML = '<option value="">Choose a unit...</option>';
    
    // Map the select value to the correct Type value
    const typeMapping = {
        'vehicle': ['Vehicle', 'VEHICLE', 'vehicle'],
        'protomech': ['Protomech', 'PROTOMECH', 'protomech', 'ProtoMech', 'Proto-Mech'],
        'battlearmor': ['BattleArmor', 'BATTLEARMOR', 'battlearmor', 'Battle Armor'],
        'infantry': ['Infantry', 'INFANTRY', 'infantry']
    };
    
    const correctType = typeMapping[unitType];
    console.log('Unit type selected:', unitType);
    console.log('Type mapping:', typeMapping);
    console.log('Correct type array:', correctType);
    console.log('First unit in data:', unitData[0]);
    console.log('First unit type:', unitData[0].UnitType);
    console.log('Total units in data:', unitData.length);
    
    // Filter units based on type
    const filteredUnits = unitData.filter(unit => {
        const matches = unit.UnitType && correctType.some(type => unit.UnitType.toLowerCase() === type.toLowerCase());
        console.log('Checking unit:', unit.Name, 'Type:', unit.UnitType, 'Matches:', matches);
        return matches;
    });
    
    console.log('Filtered units count:', filteredUnits.length);
    
    filteredUnits.forEach(unit => {
        const option = document.createElement('option');
        option.value = unit.Name;
        option.textContent = `${unit.Name} (PV: ${unit.RegPV}/${unit.VetPV})`;
        select.appendChild(option);
    });
}

// Update the card preview when a unit is selected
function updateCardPreview() {
    const unitName = document.getElementById('unitSelect').value;
    const unitType = document.getElementById('unitType').value;
    const previewContainer = document.getElementById('cardPreview');
    const previewImage = document.getElementById('previewCard');
    
    if (unitName) {
        // Find the unit in unitData to get its exact type and full name
        const unit = unitData.find(u => u.Name === unitName);
        console.log('Selected unit:', unit);
        
        // Update the card path using FullName
        const cardPath = `Cards/${unit.FullName}.gif`;
        console.log('Attempting to load card from:', cardPath);
        
        previewImage.src = cardPath;
        previewImage.alt = unitName;
        previewContainer.style.display = 'block';
        
        // Add error handling for missing images
        previewImage.onerror = function() {
            console.log('Failed to load card image:', cardPath);
            this.src = 'images/missing-card.gif';
            this.alt = `${unitName} (Card not found)`;
        };
        
        // Add success handler
        previewImage.onload = function() {
            console.log('Successfully loaded card image:', cardPath);
        };
    } else {
        previewContainer.style.display = 'none';
    }
}

// Add a unit to the force
function addUnitToForce() {
    const unitName = document.getElementById('unitSelect').value;
    const unitType = document.getElementById('unitType').value;
    if (!unitName) return;

    const isVeteran = document.getElementById('veteran').checked;
    const unit = unitData.find(u => u.Name === unitName);
    
    if (unit) {
        const points = isVeteran ? unit.VetPV : unit.RegPV;
        const unitEntry = {
            name: unitName,
            points: points,
            isVeteran: isVeteran,
            type: unitType,
            cardPath: `Cards/${unit.FullName}.gif`
        };
        
        selectedUnits.push(unitEntry);
        totalPoints += points;
        
        updateForceDisplay();
        updateCardsDisplay();
    }
}

// Update the force list display
function updateForceDisplay() {
    const forceList = document.getElementById('forceList');
    const totalPointsElement = document.getElementById('totalPoints');
    const totalPointsBadge = document.getElementById('totalPointsBadge');
    const maxPoints = parseInt(document.getElementById('maxPoints').value) || 0;
    
    if (!forceList) return; // Guard against missing element
    
    // Clear the force list
    forceList.innerHTML = '';
    
    // Add each unit individually
    selectedUnits.forEach((unit, index) => {
        const unitElement = document.createElement('div');
        unitElement.className = 'force-list-item d-flex justify-content-between align-items-center mb-2 p-2 border rounded';
        
        const nameSpan = document.createElement('span');
        nameSpan.textContent = `${unit.name} (${unit.isVeteran ? 'Veteran' : 'Regular'}) - ${unit.points} PV`;
        
        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'd-flex gap-2';
        
        const removeButton = document.createElement('button');
        removeButton.className = 'btn btn-danger btn-sm';
        removeButton.textContent = 'Remove';
        removeButton.onclick = () => {
            selectedUnits.splice(index, 1);
            updateForceDisplay();
            updateCardsDisplay();
        };
        
        buttonContainer.appendChild(removeButton);
        unitElement.appendChild(nameSpan);
        unitElement.appendChild(buttonContainer);
        forceList.appendChild(unitElement);
    });
    
    // Update total points display
    totalPoints = selectedUnits.reduce((sum, unit) => sum + unit.points, 0);
    if (totalPointsElement) {
        totalPointsElement.textContent = totalPoints;
    }
    
    // Update the badge based on points limit
    if (totalPointsBadge) {
        if (maxPoints > 0) {
            if (totalPoints > maxPoints) {
                const pointsOver = totalPoints - maxPoints;
                totalPointsBadge.className = 'badge bg-danger';
                totalPointsBadge.innerHTML = `BFS Total Exceeded! (${pointsOver} over)`;
            } else {
                totalPointsBadge.className = 'badge bg-primary';
                totalPointsBadge.innerHTML = `BFS Total: <span id="totalPoints">${totalPoints}</span>`;
            }
        } else {
            totalPointsBadge.className = 'badge bg-primary';
            totalPointsBadge.innerHTML = `BFS Total: <span id="totalPoints">${totalPoints}</span>`;
        }
    }
}

// Remove a unit from the force
function removeUnit(index) {
    const unit = selectedUnits[index];
    totalPoints -= unit.points;
    selectedUnits.splice(index, 1);
    updateForceDisplay();
    updateCardsDisplay();
}

// Update the cards display
function updateCardsDisplay() {
    const cardsContainer = document.getElementById('forceList');
    if (!cardsContainer) return; // Guard against missing element
    
    cardsContainer.innerHTML = '';
    
    selectedUnits.forEach(unit => {
        const cardElement = document.createElement('div');
        cardElement.className = 'card';
        
        const img = document.createElement('img');
        img.src = unit.cardPath;
        img.alt = unit.name;
        
        // Add error handling for missing images
        img.onerror = function() {
            this.src = 'images/missing-card.gif';
            this.alt = `${unit.name} (Card not found)`;
        };
        
        cardElement.appendChild(img);
        cardsContainer.appendChild(cardElement);
    });
}

// Print the force
function printForce() {
    // Wait for any pending image loads
    const images = document.querySelectorAll('.card img');
    let loadedImages = 0;
    let totalImages = images.length;
    
    console.log(`Waiting for ${totalImages} images to load before printing`);
    
    if (totalImages === 0) {
        console.log('No images to load, printing immediately');
        setTimeout(() => window.print(), 500);
        return;
    }
    
    // Create a loading indicator
    const loadingIndicator = document.createElement('div');
    loadingIndicator.id = 'printLoadingIndicator';
    loadingIndicator.style.position = 'fixed';
    loadingIndicator.style.top = '50%';
    loadingIndicator.style.left = '50%';
    loadingIndicator.style.transform = 'translate(-50%, -50%)';
    loadingIndicator.style.padding = '20px';
    loadingIndicator.style.background = 'rgba(255, 255, 255, 0.8)';
    loadingIndicator.style.borderRadius = '5px';
    loadingIndicator.style.boxShadow = '0 0 10px rgba(0,0,0,0.2)';
    loadingIndicator.style.zIndex = '9999';
    loadingIndicator.innerHTML = `<div class="text-center"><h4>Preparing print layout...</h4><p>Loading images: <span id="loadingProgress">0/${totalImages}</span></p></div>`;
    document.body.appendChild(loadingIndicator);
    
    // Function to update loading progress
    const updateProgress = () => {
        const progressElement = document.getElementById('loadingProgress');
        if (progressElement) {
            progressElement.textContent = `${loadedImages}/${totalImages}`;
        }
    };
    
    // Function to handle printing
    const handlePrint = () => {
        console.log('All images loaded, printing now');
        document.body.removeChild(loadingIndicator);
        setTimeout(() => window.print(), 500);
    };
    
    // Check each image
    images.forEach(img => {
        if (img.complete) {
            loadedImages++;
            updateProgress();
            if (loadedImages === totalImages) {
                handlePrint();
            }
        } else {
            img.onload = () => {
                loadedImages++;
                updateProgress();
                if (loadedImages === totalImages) {
                    handlePrint();
                }
            };
            img.onerror = () => {
                console.log(`Error loading image: ${img.src}`);
                loadedImages++;
                updateProgress();
                if (loadedImages === totalImages) {
                    handlePrint();
                }
            };
        }
    });
    
    // Fallback in case some images don't trigger onload
    setTimeout(() => {
        if (document.body.contains(loadingIndicator)) {
            console.log('Timeout reached, printing anyway');
            handlePrint();
        }
    }, 10000); // 10 second timeout
}

// Set maximum points and update button states
function setMaxPoints(points) {
    const maxPointsInput = document.getElementById('maxPoints');
    maxPointsInput.value = points;
    
    // Update button states
    document.getElementById('scale1').classList.remove('active');
    document.getElementById('scale2').classList.remove('active');
    document.getElementById('scale3').classList.remove('active');
    
    if (points === 32) {
        document.getElementById('scale1').classList.add('active');
    } else if (points === 64) {
        document.getElementById('scale2').classList.add('active');
    } else if (points === 96) {
        document.getElementById('scale3').classList.add('active');
    }
    
    updateForceDisplay();
}

// Update version number
function updateVersion() {
    const versionElement = document.querySelector('.version');
    if (versionElement) {
        const currentVersion = parseFloat(versionElement.textContent.replace('Version ', ''));
        versionElement.textContent = `Version ${(currentVersion + 0.01).toFixed(2)}`;
    }
}

document.getElementById('deleteForce').addEventListener('click', function() {
    if (confirm('Are you sure you want to delete the entire force?')) {
        selectedUnits = [];
        updateForceDisplay();
        updateTotalPoints();
        // Clear the preview cards
        const forceList = document.getElementById('forceList');
        forceList.innerHTML = '';
    }
}); 