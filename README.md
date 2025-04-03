# BattleTech Force Builder

A web-based force builder for BattleTech that allows you to create and print forces using unit data from the Master Unit List.

## Setup for Local Development

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Place your unit data CSV file in the root directory:
   - Currently supports: `MULOutput - Vehicles.csv`
   - More unit types will be added in future updates

3. Create a `Cards` directory in the root folder and place your unit card GIF files there:
   - Each card should be named exactly the same as the unit name in the CSV file
   - Example: If you have a unit named "Manticore" in the CSV, the card should be `Cards/Manticore.gif`

4. Convert the CSV data to JavaScript:
   ```
   python convert_csv_to_js.py
   ```

5. Open the `index.html` file in your browser to test locally.

## Deployment to GitHub Pages

1. Create a new GitHub repository.

2. Push your code to the repository:
   ```
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/your-repo-name.git
   git push -u origin main
   ```

3. Go to your repository settings on GitHub.

4. Scroll down to the "GitHub Pages" section.

5. Under "Source", select the branch you want to deploy (usually `main`).

6. Click "Save".

7. Your site will be published at `https://yourusername.github.io/your-repo-name/`.

## Usage

1. Select a unit from the dropdown menu
2. Choose between Regular or Veteran experience level
3. Click "Add Unit" to add it to your force
4. The unit's card will appear below the force list
5. Click "Print Force" to open a print-friendly view of your force

## Features

- Select units from the Master Unit List
- Choose between Regular and Veteran experience levels
- Automatic point value calculation
- Display unit cards
- Print-friendly force list with cards
- Remove units from your force

## Future Updates

- Support for additional unit types (BattleMechs, Battle Armor, etc.)
- Force composition validation
- Save and load force lists
- Additional unit filtering options 