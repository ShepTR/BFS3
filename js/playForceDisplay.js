// Damage scale constant - easily searchable for future modifications
const damScaleConstant = 5;

// Destroy check base value - easily searchable for future modifications
const destroyCheckBase = 4;

// Unit identifier mapping
const unitIdentifiers = {
    'A': 'Alpha', 'B': 'Bravo', 'C': 'Charlie', 'D': 'Delta', 'E': 'Echo',
    'F': 'Foxtrot', 'G': 'Golf', 'H': 'Hotel', 'I': 'India', 'J': 'Juliet',
    'K': 'Kilo', 'L': 'Lima', 'M': 'Mike', 'N': 'November', 'O': 'Oscar',
    'P': 'Papa', 'Q': 'Quebec', 'R': 'Romeo', 'S': 'Sierra', 'T': 'Tango',
    'U': 'Uniform', 'V': 'Victor', 'W': 'Whiskey', 'X': 'X-ray', 'Y': 'Yankee',
    'Z': 'Zulu'
};

// Get the current force from the URL parameters
function getCurrentForce() {
    const urlParams = new URLSearchParams(window.location.search);
    console.log('URL search params:', window.location.search);
    
    const forceParam = urlParams.get('force');
    console.log('Force parameter:', forceParam);
    
    if (forceParam) {
        try {
            const decodedForce = decodeURIComponent(forceParam);
            console.log('Decoded force:', decodedForce);
            
            const parsedForce = JSON.parse(decodedForce);
            console.log('Parsed force:', parsedForce);
            
            return parsedForce;
        } catch (e) {
            console.error('Error parsing force data:', e);
            return [];
        }
    }
    return [];
}

// Store unit data for reference
let unitsData = [];

// Function to calculate destroy check threshold
function calculateDestroyCheckThreshold(health) {
    const threshold = Math.min(Math.ceil(health / damScaleConstant) + destroyCheckBase, 12);
    return threshold;
}

// Function to check if destroy check should be displayed
function shouldShowDestroyCheck(unit) {
    const threshold = unit.Structure * damScaleConstant;
    return unit.Health < threshold;
}

// Function to calculate remaining armor
function calculateRemainingArmor(unit) {
    const threshold = unit.Structure * damScaleConstant;
    return Math.max(0, unit.Health - threshold);
}

// Function to calculate initial health
function calculateInitialHealth(unit) {
    console.log('Health is', unit.Name, 'to', unit.Armor, "--", unit.Structure, "DSC:", damScaleConstant);
    return (unit.Armor + unit.Structure) * damScaleConstant;
}

// Function to update health counter
function updateHealth(unitId, newValue) {
    console.log('Updating health for unit:', unitId, 'to value:', newValue);
    
    const unit = unitsData.find(u => u.Id === unitId || u.FullName === unitId);
    if (!unit) {
        console.error('Unit not found:', unitId);
        return;
    }
    
    // Update health value
    unit.Health = Math.max(0, newValue);
    console.log('New health value:', unit.Health);
    
    // Update display
    const unitElement = document.querySelector(`[data-unit-id="${unitId}"]`);
    if (!unitElement) {
        console.error('Unit element not found:', unitId);
        return;
    }
    
    const healthValue = unitElement.querySelector('.health-value');
    const destroyedOverlay = unitElement.querySelector('.destroyed-overlay');
    const destroyCheck = unitElement.querySelector('.destroy-check');
    const incrementBtn = unitElement.querySelector('.health-counter button:last-child');
    
    if (healthValue) {
        healthValue.textContent = unit.Health;
    }
    
    // Disable increment button if health is at or above initial value
    if (incrementBtn) {
        const initialHealth = calculateInitialHealth(unit);
        incrementBtn.disabled = unit.Health >= initialHealth;
    }
    
    // Handle destroyed state
    if (unit.Health === 0) {
        if (destroyedOverlay) {
            destroyedOverlay.style.display = 'flex';
        }
        if (destroyCheck) {
            destroyCheck.style.display = 'block';
            destroyCheck.style.backgroundColor = 'transparent';
            destroyCheck.style.color = '#dc3545'; // Red color for destroyed
            destroyCheck.textContent = 'DESTROYED';
            console.log('Setting destroy check text to DESTROYED');
        }
    } else {
        if (destroyedOverlay) {
            destroyedOverlay.style.display = 'none';
        }
        if (destroyCheck) {
            // Show destroy check only when health is below threshold
            const showCheck = shouldShowDestroyCheck(unit);
            destroyCheck.style.display = 'block';
            
            if (showCheck) {
                destroyCheck.style.backgroundColor = 'transparent';
                destroyCheck.style.color = '#dc3545'; // Red color for destroy check
                const threshold = calculateDestroyCheckThreshold(unit.Health);
                destroyCheck.textContent = `Destroy Check! Roll ${threshold} or higher to destroy`;
                console.log('Setting destroy check text to Destroy Check! Roll', threshold, 'or higher to destroy');
            } else {
                destroyCheck.style.backgroundColor = '#e6ffe6'; // Pale green
                destroyCheck.style.color = '#333'; // Dark text for armor remaining
                const remainingArmor = calculateRemainingArmor(unit);
                destroyCheck.textContent = `Armor remaining: ${remainingArmor}`;
                console.log('Setting destroy check text to Armor remaining:', remainingArmor);
            }
        }
    }
}

// Function to create play force display
function createPlayForce(units) {
    console.log('Creating play force display with units:', units);
    
    const container = document.getElementById('playForceUnits');
    if (!container) {
        console.error('Play force units container not found');
        return;
    }
    
    container.innerHTML = '';
    
    // Group units by name only
    const unitGroups = {};
    const unitIdentifierGroups = {};
    units.forEach(unit => {
        if (!unitGroups[unit.Name]) {
            unitGroups[unit.Name] = [];
        }
        unitIdentifierGroups[unit.Name] = 0;
        unitGroups[unit.Name].push(unit);
    });
    
    console.log('Unit groups:', unitGroups);
    
    // Create displays for each unit
    const identifiers = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'];
    
    Object.values(unitGroups).flat().forEach(unit => {
        console.log('Creating display for unit:', unit);
        
        // Initialize health if not set
        if (typeof unit.Health === 'undefined') {
            unit.Health = calculateInitialHealth(unit);
            console.log('Initialized health for', unit.Name, 'to', unit.Health);
        }
        
        const unitDiv = document.createElement('div');
        unitDiv.className = 'play-force-unit';
        unitDiv.setAttribute('data-unit-id', unit.Id || unit.FullName); // Use FullName as fallback
        
        // Create unit label container
        const labelContainer = document.createElement('div');
        labelContainer.className = 'unit-label-container';
        
        // Create identifier (left-aligned)
        const identifier = document.createElement('div');
        identifier.className = 'unit-identifier';
        identifier.textContent = unitIdentifiers[identifiers[unitIdentifierGroups[unit.Name]++ % identifiers.length]];
        console.log('Initialized health for', unit.Name, 'to', unit.Health)
        
        // Create unit name (right-aligned)
        const unitName = document.createElement('div');
        unitName.className = 'unit-identifier-name';
        unitName.textContent = unit.Name + ' (' + (unit.isVeteran ? 'V' : 'R') + ')';
        
        // Add identifier and name to label container
        labelContainer.appendChild(unitName);
        labelContainer.appendChild(identifier);
        
        
        // Create card container
        const cardContainer = document.createElement('div');
        cardContainer.className = 'card-container';
        
        // Create card image
        const cardImage = document.createElement('img');
        cardImage.src = 'Cards/' + unit.FullName.replace(/\//g, '-') + '.gif';
        cardImage.alt = unit.Name;
        
        // Create destroyed overlay
        const destroyedOverlay = document.createElement('div');
        destroyedOverlay.className = 'destroyed-overlay';
        destroyedOverlay.textContent = 'DESTROYED';
        destroyedOverlay.style.display = unit.Health === 0 ? 'flex' : 'none';
        
        // Add image and overlay to card container
        cardContainer.appendChild(cardImage);
        cardContainer.appendChild(destroyedOverlay);
        
        // Create health counter
        const healthCounter = document.createElement('div');
        healthCounter.className = 'health-counter';
        
        const decrementBtn = document.createElement('button');
        decrementBtn.textContent = '-';
        decrementBtn.onclick = () => updateHealth(unit.Id || unit.FullName, Math.max(0, unit.Health - 1));
        
        const healthValue = document.createElement('span');
        healthValue.className = 'health-value';
        healthValue.textContent = unit.Health;
        
        const incrementBtn = document.createElement('button');
        incrementBtn.textContent = '+';
        incrementBtn.onclick = () => updateHealth(unit.Id || unit.FullName, unit.Health + 1);
        
        // Disable increment button if health is at or above initial value
        const initialHealth = calculateInitialHealth(unit);
        incrementBtn.disabled = unit.Health >= initialHealth;
        
        healthCounter.appendChild(decrementBtn);
        healthCounter.appendChild(healthValue);
        healthCounter.appendChild(incrementBtn);
        
        // Create destroy check label
        const destroyCheck = document.createElement('div');
        destroyCheck.className = 'destroy-check';
        
        // Show destroy check only when health is below threshold
        const showCheck = shouldShowDestroyCheck(unit);
        destroyCheck.style.display = 'block'; // Always display the element to maintain space
        
        if (showCheck) {
            destroyCheck.style.backgroundColor = 'transparent';
            destroyCheck.style.color = '#dc3545'; // Red color for destroy check
            const threshold = calculateDestroyCheckThreshold(unit.Health);
            destroyCheck.textContent = `Destroy Check! Roll ${threshold} or higher to destroy`;
            console.log('Initial destroy check text: Destroy Check! Roll', threshold, 'or higher to destroy');
        } else {
            destroyCheck.style.backgroundColor = '#e6ffe6'; // Pale green
            destroyCheck.style.color = '#333'; // Dark text for armor remaining
            const remainingArmor = calculateRemainingArmor(unit);
            destroyCheck.textContent = `Armor remaining: ${remainingArmor}`;
            console.log('Initial destroy check text: Armor remaining:', remainingArmor);
        }
        
        // Assemble the unit display
        unitDiv.appendChild(labelContainer);
        unitDiv.appendChild(cardContainer);
        unitDiv.appendChild(healthCounter);
        unitDiv.appendChild(destroyCheck);
        
        container.appendChild(unitDiv);
    });
}

// Initialize when the window is ready
window.onload = function() {
    console.log('Play force display page loaded');
    
    // Get the current force from the URL parameters
    unitsData = getCurrentForce();
    console.log('Retrieved force data:', unitsData);
    
    // Create the play force display
    createPlayForce(unitsData);
    
    // Log for debugging
    console.log('Play force initialized with', unitsData.length, 'units');
}; 