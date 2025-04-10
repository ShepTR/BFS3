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

// Initialize play force functionality
function initPlayForce() {
    const playForceButton = document.getElementById('playForce');
    
    if (!playForceButton) {
        console.error('Play force button not found');
        return;
    }
    
    playForceButton.addEventListener('click', () => {
        // Get the current force from the global variable
        const currentForce = window.currentForce || [];
        
        // Log for debugging
        console.log('Current force:', currentForce);
        console.log('Opening play force with', currentForce.length, 'units');
        console.log('Force data:', JSON.stringify(currentForce));
        
        // Create a new window with the play force page
        const url = 'playForce.html?force=' + encodeURIComponent(JSON.stringify(currentForce));
        console.log('Opening URL:', url);
        
        const playWindow = window.open(url, '_blank');
        if (!playWindow) {
            alert('Please allow popups for this site to open the play force view.');
            return;
        }
    });
    
    console.log('Play force functionality initialized');
}

// Export functions for use in other files
window.initPlayForce = initPlayForce;

// Initialize when the DOM is loaded
document.addEventListener('DOMContentLoaded', initPlayForce); 