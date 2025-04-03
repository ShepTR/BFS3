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
    
    // Initialize version
    updateVersion();
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
    
    // Update total points display
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
    
    // Group units by name and experience level
    const groupedUnits = {};
    selectedUnits.forEach((unit, index) => {
        const key = `${unit.name}-${unit.isVeteran}`;
        if (!groupedUnits[key]) {
            groupedUnits[key] = {
                name: unit.name,
                isVeteran: unit.isVeteran,
                points: unit.points,
                count: 1,
                indices: [index]
            };
        } else {
            groupedUnits[key].count++;
            groupedUnits[key].indices.push(index);
        }
    });
    
    // Add each group to the force list
    Object.values(groupedUnits).forEach(group => {
        const unitElement = document.createElement('div');
        unitElement.className = 'force-list-item d-flex justify-content-between align-items-center mb-2 p-2 border rounded';
        unitElement.innerHTML = `
            <span>${group.name} (${group.isVeteran ? 'Veteran' : 'Regular'}) - ${group.points} PV x${group.count}</span>
            <button class="btn btn-danger btn-sm" onclick="removeUnit(${group.indices[0]})">Remove</button>
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
    printWindow.document.write(`
        <html>
        <head>
            <title>BattleTech Force Printout</title>
            <style>
                @page {
                    size: letter portrait;
                    margin: 0.5in;
                }
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    width: 7.5in; /* 8.5in - 0.5in margins on each side */
                }
                .force-summary {
                    margin-bottom: 0.5in;
                }
                .force-summary h1 {
                    text-align: center;
                    margin-bottom: 0.25in;
                    font-size: 18pt;
                }
                .force-summary table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 0.25in;
                    font-size: 10pt;
                }
                .force-summary th, .force-summary td {
                    border: 1px solid #000;
                    padding: 4px 8px;
                    text-align: left;
                }
                .force-summary th {
                    background-color: #f2f2f2;
                }
                .cards-page {
                    page-break-before: always;
                    display: grid;
                    grid-template-columns: repeat(3, 2.5in);
                    grid-template-rows: repeat(3, 3.5in);
                    gap: 0;
                    width: 7.5in;
                    height: 10.5in;
                }
                .card-container {
                    width: 2.5in;
                    height: 3.5in;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    overflow: hidden;
                }
                .card-container img {
                    width: 2.5in;
                    height: 3.5in;
                    object-fit: contain;
                }
                @media print {
                    body {
                        width: 7.5in;
                    }
                    .cards-page {
                        width: 7.5in;
                        height: 10.5in;
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
                            <th style="width: 50%">Unit</th>
                            <th style="width: 25%">Experience</th>
                            <th style="width: 25%">Points</th>
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

// Update version number
function updateVersion() {
    const versionElement = document.querySelector('.version');
    if (versionElement) {
        const currentVersion = parseFloat(versionElement.textContent.replace('Version ', ''));
        versionElement.textContent = `Version ${(currentVersion + 0.01).toFixed(2)}`;
    }
} 