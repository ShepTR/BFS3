// Global variables
let currentForce = [];
let currentScale = 1;
let maxPoints = 32;

// DOM Elements
const unitTypeSelect = document.getElementById('unitType');
const unitSelect = document.getElementById('unitSelect');
const veteranCheckbox = document.getElementById('veteran');
const addUnitButton = document.getElementById('addUnit');
const forceList = document.getElementById('forceList');
const previewCard = document.getElementById('previewCard');
const cardPreview = document.getElementById('cardPreview');
const totalPointsBadge = document.getElementById('totalPointsBadge');
const totalPointsSpan = document.getElementById('totalPoints');
const deleteForceButton = document.getElementById('deleteForce');
const printForceButton = document.getElementById('printForce');
const maxPointsInput = document.getElementById('maxPoints');

// Event Listeners
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

// Initialize
function init() {
    updateUnitList();
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
            const cardPath = `Cards/${unit.FullName}.gif`;
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
    
    const isVeteran = veteranCheckbox.checked;
    const pv = isVeteran ? Math.ceil(unit.VetPV) : unit.RegPV;
    
    const forceUnit = {
        ...unit,
        PV: pv,
        isVeteran
    };
    
    currentForce.push(forceUnit);
    updateForceList();
    updateTotalPoints();
    
    // Reset selection
    unitSelect.value = '';
    cardPreview.style.display = 'none';
    previewCard.src = '';
}

// Update force list display
function updateForceList() {
    forceList.innerHTML = '';
    
    currentForce.forEach((unit, index) => {
        const cardDiv = document.createElement('div');
        cardDiv.className = 'unit-card';
        
        const img = document.createElement('img');
        img.src = `Cards/${unit.FullName}.gif`;
        img.alt = unit.FullName;
        
        const removeButton = document.createElement('button');
        removeButton.className = 'btn btn-danger btn-sm position-absolute top-0 end-0 m-2';
        removeButton.innerHTML = '&times;';
        removeButton.onclick = () => removeUnit(index);
        
        cardDiv.appendChild(img);
        cardDiv.appendChild(removeButton);
        forceList.appendChild(cardDiv);
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
    
    if (total > maxPoints) {
        totalPointsBadge.classList.remove('bg-primary');
        totalPointsBadge.classList.add('bg-danger');
    } else {
        totalPointsBadge.classList.remove('bg-danger');
        totalPointsBadge.classList.add('bg-primary');
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
    // Show loading indicator
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'position-fixed top-50 start-50 translate-middle bg-white p-3 rounded shadow';
    loadingDiv.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary mb-2" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
            <div>Preparing print layout...</div>
        </div>
    `;
    document.body.appendChild(loadingDiv);
    
    // Wait for all images to load
    const images = document.querySelectorAll('.unit-card img');
    let loadedImages = 0;
    
    if (images.length === 0) {
        window.print();
        loadingDiv.remove();
        return;
    }
    
    images.forEach(img => {
        if (img.complete) {
            loadedImages++;
            if (loadedImages === images.length) {
                window.print();
                loadingDiv.remove();
            }
        } else {
            img.onload = () => {
                loadedImages++;
                if (loadedImages === images.length) {
                    window.print();
                    loadingDiv.remove();
                }
            };
            img.onerror = () => {
                loadedImages++;
                if (loadedImages === images.length) {
                    window.print();
                    loadingDiv.remove();
                }
            };
        }
    });
    
    // Fallback in case some images don't trigger onload
    setTimeout(() => {
        window.print();
        loadingDiv.remove();
    }, 10000);
}

// Initialize on load
document.addEventListener('DOMContentLoaded', init); 