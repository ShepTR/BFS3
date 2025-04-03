// Global variables
let selectedUnits = [];
let totalPoints = 0;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    // Populate unit select dropdown
    populateUnitSelect();
    
    // Add event listeners
    document.getElementById('addUnit').addEventListener('click', addUnitToForce);
    document.getElementById('printForce').addEventListener('click', printForce);
    document.getElementById('unitSelect').addEventListener('change', updateCardPreview);
    document.getElementById('maxPoints').addEventListener('input', updateForceDisplay);
});

// Populate the unit select dropdown
function populateUnitSelect() {
    const select = document.getElementById('unitSelect');
    select.innerHTML = '<option value="">Choose a unit...</option>';
    
    unitData.forEach(unit => {
        const option = document.createElement('option');
        option.value = unit.Name;
        option.textContent = `${unit.Name} (PV: ${unit.RegPV}/${unit.VetPV})`;
        select.appendChild(option);
    });
}

// Update the card preview when a unit is selected
function updateCardPreview() {
    const unitName = document.getElementById('unitSelect').value;
    const previewContainer = document.getElementById('cardPreview');
    const previewImage = document.getElementById('previewCard');
    
    if (unitName) {
        previewImage.src = `Cards/${unitName}.gif`;
        previewImage.alt = unitName;
        previewContainer.style.display = 'block';
        
        // Add error handling for missing images
        previewImage.onerror = function() {
            this.src = 'images/missing-card.gif';
            this.alt = `${unitName} (Card not found)`;
        };
    } else {
        previewContainer.style.display = 'none';
    }
}

// Add a unit to the force
function addUnitToForce() {
    const unitName = document.getElementById('unitSelect').value;
    if (!unitName) return;

    const isVeteran = document.getElementById('veteran').checked;
    const unit = unitData.find(u => u.Name === unitName);
    
    if (unit) {
        const points = isVeteran ? unit.VetPV : unit.RegPV;
        const unitEntry = {
            name: unitName,
            points: points,
            isVeteran: isVeteran,
            cardPath: `Cards/${unitName}.gif`
        };
        
        selectedUnits.push(unitEntry);
        totalPoints += points;
        
        updateForceDisplay();
        loadUnitCard(unitName);
    }
}

// Update the force list display
function updateForceDisplay() {
    const forceList = document.getElementById('forceList');
    const totalPointsElement = document.getElementById('totalPoints');
    const totalPointsBadge = document.getElementById('totalPointsBadge');
    const maxPoints = parseInt(document.getElementById('maxPoints').value) || 0;
    
    forceList.innerHTML = '';
    totalPointsElement.textContent = totalPoints;
    
    // Update the badge based on points limit
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
    
    selectedUnits.forEach((unit, index) => {
        const unitElement = document.createElement('div');
        unitElement.className = 'force-list-item';
        unitElement.innerHTML = `
            <span>${unit.name} (${unit.isVeteran ? 'Veteran' : 'Regular'}) - ${unit.points} PV</span>
            <button class="btn btn-danger btn-sm" onclick="removeUnit(${index})">Remove</button>
        `;
        forceList.appendChild(unitElement);
    });
}

// Remove a unit from the force
function removeUnit(index) {
    const unit = selectedUnits[index];
    totalPoints -= unit.points;
    selectedUnits.splice(index, 1);
    updateForceDisplay();
    updateCardsDisplay();
}

// Load a unit card
function loadUnitCard(unitName) {
    const cardsContainer = document.getElementById('unitCards');
    const cardElement = document.createElement('div');
    cardElement.className = 'col-md-4 unit-card';
    
    // Create image element
    const img = document.createElement('img');
    img.src = `Cards/${unitName}.gif`;
    img.alt = unitName;
    img.className = 'img-fluid';
    
    // Add error handling for missing images
    img.onerror = function() {
        this.src = 'images/missing-card.gif';
        this.alt = `${unitName} (Card not found)`;
    };
    
    cardElement.appendChild(img);
    cardsContainer.appendChild(cardElement);
}

// Update the cards display
function updateCardsDisplay() {
    const cardsContainer = document.getElementById('unitCards');
    cardsContainer.innerHTML = '';
    
    selectedUnits.forEach(unit => {
        loadUnitCard(unit.name);
    });
}

// Print the force
function printForce() {
    const printWindow = window.open('', '_blank');
    printWindow.document.write(`
        <html>
        <head>
            <title>BattleTech Force Printout</title>
            <style>
                body { font-family: Arial, sans-serif; }
                .print-card { page-break-inside: avoid; margin-bottom: 1rem; }
                .force-summary { margin-bottom: 2rem; }
            </style>
        </head>
        <body>
            <div class="force-summary">
                <h1>BattleTech Force</h1>
                <p>Total Points: ${totalPoints}</p>
                <h2>Units:</h2>
                <ul>
                    ${selectedUnits.map(unit => 
                        `<li>${unit.name} (${unit.isVeteran ? 'Veteran' : 'Regular'}) - ${unit.points} PV</li>`
                    ).join('')}
                </ul>
            </div>
            <div id="cards">
                ${selectedUnits.map(unit => 
                    `<div class="print-card"><img src="${unit.cardPath}" alt="${unit.name}" style="max-width: 100%;"></div>`
                ).join('')}
            </div>
        </body>
        </html>
    `);
    printWindow.document.close();
    printWindow.print();
} 