import pandas as pd
import json
import os

def convert_csv_to_js():
    # Read the CSV file
    csv_file = 'MULOutput - Vehicles.csv'
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found!")
        return
    
    # Read the CSV data
    df = pd.read_csv(csv_file)
    
    # Add regular and veteran PV columns if they don't exist
    if 'RegPV' not in df.columns:
        df['RegPV'] = df['PV']
    if 'VetPV' not in df.columns:
        df['VetPV'] = df['PV'] * 1.5  # Assuming veteran costs 50% more
    
    # Ensure UnitType is preserved
    df['UnitType'] = df['UnitType'].fillna('Vehicle')  # Fill any NaN values with 'Vehicle'
    
    # Convert to list of dictionaries
    units = df.to_dict('records')
    
    # Create JavaScript file content
    js_content = f"// Auto-generated from {csv_file}\n"
    js_content += "const unitData = " + json.dumps(units, indent=2) + ";\n"
    
    # Write to JavaScript file
    with open('js/units.js', 'w') as f:
        f.write(js_content)
    
    print(f"Successfully converted {csv_file} to js/units.js")

if __name__ == "__main__":
    # Create js directory if it doesn't exist
    if not os.path.exists('js'):
        os.makedirs('js')
    
    convert_csv_to_js() 