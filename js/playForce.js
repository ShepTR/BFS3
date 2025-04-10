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
    const playForceBtn = document.getElementById('playForce');
    if (playForceBtn) {
        playForceBtn.addEventListener('click', () => {
            console.log('Play Force button clicked. Current force length:', currentForce.length);
            
            // Store the force data in localStorage instead of passing it in the URL
            localStorage.setItem('playForceData', JSON.stringify(currentForce));
            
            // Open the play force page in a new tab
            window.open('playForce.html', '_blank');
        });
    } else {
        console.error('Play Force button not found');
    }
}

// Export functions for use in other files
window.initPlayForce = initPlayForce;

// Initialize when the DOM is loaded
document.addEventListener('DOMContentLoaded', initPlayForce); 