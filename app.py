from flask import Flask, render_template, jsonify, request
import pandas as pd
import os
import glob

app = Flask(__name__)

# Load the Vehicles CSV file
def load_unit_data():
    csv_file = 'MULOutput - Vehicles.csv'
    if os.path.exists(csv_file):
        df = pd.read_csv(csv_file)
        # Add regular and veteran PV columns if they don't exist
        if 'RegPV' not in df.columns:
            df['RegPV'] = df['PV']
        if 'VetPV' not in df.columns:
            df['VetPV'] = df['PV'] * 1.5  # Assuming veteran costs 50% more
        return df.to_dict('records')
    return []

@app.route('/')
def index():
    unit_data = load_unit_data()
    return render_template('index.html', unit_data=unit_data)

@app.route('/get_units')
def get_units():
    unit_data = load_unit_data()
    return jsonify(unit_data)

@app.route('/get_card/<unit_name>')
def get_card(unit_name):
    card_path = os.path.join('Cards', f'{unit_name}.gif')
    if os.path.exists(card_path):
        return jsonify({'exists': True, 'path': card_path})
    return jsonify({'exists': False})

if __name__ == '__main__':
    app.run(debug=True) 