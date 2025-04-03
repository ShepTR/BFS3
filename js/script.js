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
    
    // Filter units based on type
    const filteredUnits = unitData.filter(unit => {
        switch(unitType) {
            case 'vehicle':
                return unit.Type === 'Vehicle';
            case 'protomech':
                return unit.Type === 'Protomech';
            case 'battlearmor':
                return unit.Type === 'BattleArmor';
            case 'infantry':
                return unit.Type === 'Infantry';
            default:
                return false;
        }
    });
    
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
        // Update the card path based on unit type
        const cardPath = `Cards/${unitType}/${unitName}.gif`;
        previewImage.src = cardPath;
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
            cardPath: `Cards/${unitType}/${unitName}.gif`
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
    const cardsContainer = document.getElementById('unitCards');
    cardsContainer.innerHTML = '';
    
    selectedUnits.forEach(unit => {
        const cardElement = document.createElement('div');
        cardElement.className = 'col-md-4 unit-card mb-3';
        
        const img = document.createElement('img');
        img.src = unit.cardPath;
        img.alt = unit.name;
        img.className = 'img-fluid';
        
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
    const printWindow = window.open('', '_blank');
    const content = `
        <!DOCTYPE html>
        <html>
        <head>
            <title>Force Summary</title>
            <style>
                @media print {
                    @page {
                        size: letter;
                        margin: 0.25in;
                    }
                }
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    width: 8in;
                }
                .summary {
                    margin-bottom: 20px;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    font-size: 10pt;
                }
                th, td {
                    border: 1px solid black;
                    padding: 4px;
                }
                .card-grid {
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 0;
                    page-break-before: always;
                }
                .card {
                    width: 2.5in;
                    height: 3.5in;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    transform: rotate(90deg);
                    transform-origin: center;
                    position: relative;
                }
                .card img {
                    width: 2.5in;
                    height: 3.5in;
                    object-fit: contain;
                }
            </style>
        </head>
        <body>
            <div class="summary">
                <table>
                    <tr>
                        <th>Unit</th>
                        <th>Experience</th>
                        <th>Points</th>
                        <th>Count</th>
                    </tr>
                    ${(() => {
                        const grouped = {};
                        selectedUnits.forEach(unit => {
                            const key = unit.name + (unit.isVeteran ? '-vet' : '-reg');
                            if (!grouped[key]) {
                                grouped[key] = {
                                    name: unit.name,
                                    isVeteran: unit.isVeteran,
                                    points: unit.points,
                                    count: 1
                                };
                            } else {
                                grouped[key].count++;
                            }
                        });
                        return Object.values(grouped)
                            .map(unit => `
                                <tr>
                                    <td>${unit.name}</td>
                                    <td>${unit.isVeteran ? 'Veteran' : 'Regular'}</td>
                                    <td>${unit.points}</td>
                                    <td>${unit.count}</td>
                                </tr>
                            `)
                            .join('');
                    })()}
                    <tr>
                        <td colspan="2"><strong>Total Points:</strong></td>
                        <td colspan="2"><strong>${totalPoints}</strong></td>
                    </tr>
                </table>
            </div>
            ${(() => {
                const cards = [];
                for (let i = 0; i < selectedUnits.length; i += 9) {
                    cards.push('<div class="card-grid">');
                    for (let j = i; j < Math.min(i + 9, selectedUnits.length); j++) {
                        cards.push(`
                            <div class="card">
                                <img src="${selectedUnits[j].cardPath}" alt="${selectedUnits[j].name}">
                            </div>
                        `);
                    }
                    cards.push('</div>');
                }
                return cards.join('');
            })()}
        </body>
        </html>
    `;
    printWindow.document.write(content);
    printWindow.document.close();
    printWindow.print();
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