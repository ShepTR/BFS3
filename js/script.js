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
    
    // Add scale button event listeners
    document.getElementById('scale1').addEventListener('click', () => setMaxPoints(32));
    document.getElementById('scale2').addEventListener('click', () => setMaxPoints(64));
    document.getElementById('scale3').addEventListener('click', () => setMaxPoints(96));
    
    // Set initial scale to 1
    setMaxPoints(32);
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
                @page {
                    size: letter;
                    margin: 0.5in;
                }
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                }
                .force-summary {
                    margin-bottom: 1in;
                }
                .force-summary h1 {
                    text-align: center;
                    margin-bottom: 0.5in;
                }
                .force-summary table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 0.5in;
                }
                .force-summary th, .force-summary td {
                    border: 1px solid #000;
                    padding: 8px;
                    text-align: left;
                }
                .force-summary th {
                    background-color: #f2f2f2;
                }
                .cards-page {
                    page-break-before: always;
                    display: grid;
                    grid-template-columns: repeat(3, 3.5in);
                    grid-template-rows: repeat(3, 2.5in);
                    gap: 0.25in;
                    justify-content: center;
                    align-items: center;
                }
                .card-container {
                    width: 3.5in;
                    height: 2.5in;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    transform: rotate(-90deg);
                    transform-origin: center;
                }
                .card-container img {
                    max-width: 100%;
                    max-height: 100%;
                    object-fit: contain;
                }
                @media print {
                    .no-print {
                        display: none;
                    }
                }
            </style>
        </head>
        <body>
            <div class="force-summary">
                <h1>BattleTech Force</h1>
                <table>
                    <thead>
                        <tr>
                            <th>Unit</th>
                            <th>Experience</th>
                            <th>Points</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${selectedUnits.map(unit => `
                            <tr>
                                <td>${unit.name}</td>
                                <td>${unit.isVeteran ? 'Veteran' : 'Regular'}</td>
                                <td>${unit.points}</td>
                            </tr>
                        `).join('')}
                        <tr>
                            <td colspan="2"><strong>Total Points:</strong></td>
                            <td><strong>${totalPoints}</strong></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            ${(() => {
                let html = '';
                for (let i = 0; i < selectedUnits.length; i += 9) {
                    html += '<div class="cards-page">';
                    for (let j = i; j < Math.min(i + 9, selectedUnits.length); j++) {
                        html += `
                            <div class="card-container">
                                <img src="${selectedUnits[j].cardPath}" alt="${selectedUnits[j].name}">
                            </div>
                        `;
                    }
                    html += '</div>';
                }
                return html;
            })()}
        </body>
        </html>
    `);
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