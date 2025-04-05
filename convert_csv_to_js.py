import pandas as pd
import json
import os

def convert_csv_to_js():
    # List of CSV files to process
    csv_files = [
        'MULOutput - Vehicles.csv', 
        'MULOutput - Protomechs.csv',
        'MULOutput - BattleArmor.csv',
        'MULOutput - InfantryEmp.csv'
    ]
    all_units = []
    
    for csv_file in csv_files:
        if not os.path.exists(csv_file):
            print(f"Warning: {csv_file} not found!")
            continue
        
        # Read the CSV data
        df = pd.read_csv(csv_file)
        
        # Add regular and veteran PV columns if they don't exist
        if 'RegPV' not in df.columns:
            df['RegPV'] = df['PV']
        if 'VetPV' not in df.columns:
            df['VetPV'] = df['PV'] * 1.5  # Assuming veteran costs 50% more
        
        # Ensure UnitType is preserved and at the start of each record
        df = df[['UnitType'] + [col for col in df.columns if col != 'UnitType']]  # Move UnitType to first column
        
        # Fill any NaN values in UnitType based on the filename
        if 'Vehicles' in csv_file:
            df['UnitType'] = df['UnitType'].fillna('Vehicle')
        elif 'Protomechs' in csv_file:
            df['UnitType'] = df['UnitType'].fillna('Protomech')
        elif 'BattleArmor' in csv_file:
            df['UnitType'] = df['UnitType'].fillna('BattleArmor')
        elif 'InfantryEmp' in csv_file:
            # Check if it's an emplacement or infantry
            df['UnitType'] = df.apply(lambda row: 'Emplacement' if 'Emplacement' in str(row['Name']) else 'Infantry', axis=1)
        
        # Convert to list of dictionaries and add to all units
        units = df.to_dict('records')
        all_units.extend(units)
    
    # Create JavaScript file content
    js_content = f"// Auto-generated from multiple CSV files\n"
    js_content += "const units = " + json.dumps(all_units, indent=2) + ";\n"
    
    # Write to JavaScript file
    with open('js/units.js', 'w') as f:
        f.write(js_content)
    
    print(f"Successfully converted CSV files to js/units.js")

if __name__ == "__main__":
    # Create js directory if it doesn't exist
    if not os.path.exists('js'):
        os.makedirs('js')
    
    convert_csv_to_js() 