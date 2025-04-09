import csv
import re
import os
from collections import defaultdict
from weapon_parser import WeaponParser, normalize_weapon_name, is_weapon, parse_weapons, format_weapon_list

# Define the vehicles directory
vehicles_dir = r"D:\Games\Downloads\mekhq-windows-0.49.19.1\MMSource\megamek-master\megamek\data\mekfiles\vehicles"

# Define weapons directory
weapons_dir = r"D:\Games\Downloads\mekhq-windows-0.49.19.1\MMSource\megamek-master\megamek\src\megamek\common\weapons"

# Define output files
CSV_FILE = "vehicle_weapons.csv"
VEHICLES_WITHOUT_WEAPONS_FILE = "vehicles_without_weapons.txt"

# Load weapon stats from Java files
weapon_parser = WeaponParser(weapons_dir)
weapons_data = weapon_parser.process_weapons_directory()

# Create lookup dictionary
weapon_stats = {}
for weapon in weapons_data:
    # Add all lookup names to the dictionary
    for lookup_name in weapon.lookup_names:
        if lookup_name:
            weapon_stats[lookup_name.lower()] = {
                'damage': weapon.damage,
                'rack_size': weapon.rack_size,
                'cluster_damage': weapon.cluster_damage,
                'cluster_size': weapon.cluster_size,
                'is_streak': 'streak' in lookup_name.lower(),
                'is_cluster': weapon.is_lbx or any(x in lookup_name.lower() for x in ['srm', 'lrm', 'mrm']),
                'short_range': weapon.short_range,
                'medium_range': weapon.medium_range,
                'long_range': weapon.long_range
            }

# Check if directory exists
if not os.path.exists(vehicles_dir):
    print(f"Error: Vehicles directory not found at {vehicles_dir}")
    exit(1)

# Special equipment that should be ignored
special_equipment = {
    'CASE',
    'TARGETING COMPUTER',
    'BAP',
    'ECM',
    'ACTIVE PROBE',
    'MASC',
    'C3 MASTER',
    'C3 SLAVE',
    'TAG',
    'ARTEMIS',
    'ARTEMIS IV',
    'ARTEMIS V',
    'APOLLO',
    'RISC',
    'TSM',
    'COMMAND CONSOLE',
    'CAMO SYSTEM',
    'STEALTH',
    'ANGEL ECM',
    'WATCHDOG',
    'NOVA',
    'LIGHT ENGINE',
    'XL ENGINE',
    'XXL ENGINE',
    'COMPACT ENGINE',
    'PRIMITIVE ENGINE',
    'ARMORED COMPONENT',
    'REINFORCED',
    'HARDENED',
    'CLAN',
    'ENDO STEEL',
    'FERRO-FIBROUS',
    'REACTIVE',
    'REFLECTIVE',
    'BALLISTIC-REINFORCED',
    'INDUSTRIAL',
    'COMMERCIAL',
    'COMMUNICATIONS',
    'MAST MOUNT',
    'OMNI',
    'AMPHIBIOUS',
    'DUMPER',
    'CARGO',
    'INFANTRY',
    'BEAGLE',
    'CLAN TECH',
    'COMSTAR',
    'PRIMITIVE',
    'PROTOTYPE',
    'SUPERHEAVY',
    'SUPPORT VEHICLE',
    'COMBAT VEHICLE',
    'INDUSTRIAL VEHICLE',
    'VTOL',
    'WIGE',
    'NAVAL',
    'SUBMARINE',
    'HYDROFOIL',
    'TRACKED',
    'WHEELED',
    'HOVER',
    'JUMP JET',
    'COMMAND',
    'RECON',
    'SCOUT',
    'TRANSPORT',
    'REPAIR',
    'RECOVERY',
    'MEDICAL',
    'MASH',
    'MOBILE HQ',
    'ARTILLERY',
    'MISSILE',
    'TANK',
    'APC',
    'IFV',
    'MBT',
    'CARRIER',
    'PLATFORM',
    'VEHICLE',
    'CRAFT',
    'DRONE',
    'REMOTE',
    'TRAILER',
    'UNIT',
    'SYSTEM',
    'MOUNT',
    'POD',
    'BAY',
    'ARRAY',
    'SUITE',
    'KIT',
    'GEAR',
    'EQUIPMENT',
    'COMPONENT',
    'ASSEMBLY',
    'MODULE',
    'DEVICE',
    'SENSOR',
    'SCANNER',
    'DETECTOR',
    'JAMMER',
    'DISRUPTOR',
    'SHIELD',
    'ARMOR',
    'PLATING',
    'COATING',
    'LINING',
    'CELL',
    'BATTERY',
    'GENERATOR',
    'REACTOR',
    'ENGINE',
    'DRIVE',
    'MOTOR',
    'THRUSTER',
    'PROPULSION',
    'LIFT',
    'JUMP',
    'HOVER',
    'VTOL',
    'WIGE',
    'NAVAL',
    'SUB',
    'HYDRO',
    'TRACK',
    'WHEEL',
    'COMMAND',
    'CONTROL',
    'COMPUTER',
    'PROCESSOR',
    'CORE',
    'BRAIN',
    'AI',
    'NETWORK',
    'LINK',
    'COMM',
    'RADIO',
    'TRANSMITTER',
    'RECEIVER',
    'ANTENNA',
    'DISH',
    'ARRAY',
    'SUITE',
    'KIT',
    'SET',
    'PACK',
    'UNIT',
    'SYSTEM',
    'MOUNT',
    'POD',
    'BAY',
    'BIN',
    'RACK',
    'MAGAZINE',
    'AMMO',
    'MUNITION',
    'ROUND',
    'SHELL',
    'MISSILE',
    'ROCKET',
    'TORPEDO',
    'BOMB',
    'MINE',
    'CHARGE',
    'WARHEAD',
    'FUSE',
    'DETONATOR',
    'TRIGGER',
    'SAFETY',
    'LOCK',
    'GUARD',
    'SHIELD',
    'ARMOR',
    'PLATE',
    'PANEL',
    'SECTION',
    'PIECE',
    'PART',
    'COMPONENT',
    'ASSEMBLY',
    'MODULE',
    'DEVICE',
    'TOOL',
    'IMPLEMENT',
    'INSTRUMENT',
    'APPARATUS',
    'MACHINE',
    'MECHANISM',
    'GEAR',
    'EQUIPMENT',
    'HARDWARE',
    'SOFTWARE',
    'PROGRAM',
    'CODE',
    'DATA',
    'FILE',
    'RECORD',
    'LOG',
    'REPORT',
    'DOCUMENT',
    'MANUAL',
    'GUIDE',
    'INSTRUCTION',
    'PROTOCOL',
    'PROCEDURE',
    'PROCESS',
    'METHOD',
    'TECHNIQUE',
    'SKILL',
    'ABILITY',
    'POWER',
    'FORCE',
    'ENERGY',
    'HEAT',
    'LIGHT',
    'SOUND',
    'WAVE',
    'PULSE',
    'BEAM',
    'RAY',
    'STREAM',
    'FLOW',
    'CURRENT',
    'CHARGE',
    'FIELD',
    'ZONE',
    'AREA',
    'SPACE',
    'VOLUME',
    'MASS',
    'WEIGHT',
    'SIZE',
    'SHAPE',
    'FORM',
    'STRUCTURE',
    'BUILD',
    'MAKE',
    'MODEL',
    'TYPE',
    'CLASS',
    'GRADE',
    'LEVEL',
    'RANK',
    'STATUS',
    'STATE',
    'CONDITION',
    'MODE',
    'SETTING',
    'CONFIG',
    'SETUP',
    'LAYOUT',
    'DESIGN',
    'PLAN',
    'SPEC',
    'STANDARD',
    'RULE',
    'LAW',
    'CODE',
    'REGULATION',
    'REQUIREMENT',
    'LIMIT',
    'BOUND',
    'RANGE',
    'SCOPE',
    'EXTENT',
    'REACH',
    'COVERAGE',
    'SPAN',
    'SPREAD',
    'WIDTH',
    'LENGTH',
    'HEIGHT',
    'DEPTH',
    'DIMENSION',
    'MEASURE',
    'QUANTITY',
    'AMOUNT',
    'NUMBER',
    'COUNT',
    'TOTAL',
    'SUM',
    'WHOLE',
    'PART',
    'PIECE',
    'SECTION',
    'SEGMENT',
    'DIVISION',
    'UNIT',
    'GROUP',
    'SET',
    'COLLECTION',
    'ARRAY',
    'SERIES',
    'SEQUENCE',
    'ORDER',
    'ARRANGEMENT',
    'PATTERN',
    'SYSTEM',
    'NETWORK',
    'GRID',
    'MATRIX',
    'STRUCTURE',
    'FRAME',
    'CHASSIS',
    'BODY',
    'HULL',
    'SHELL',
    'CASE',
    'HOUSING',
    'CONTAINER',
    'BOX',
    'BIN',
    'TANK',
    'VESSEL',
    'CRAFT',
    'VEHICLE',
    'MACHINE',
    'DEVICE',
    'TOOL',
    'IMPLEMENT',
    'INSTRUMENT',
    'APPARATUS',
    'EQUIPMENT',
    'GEAR',
    'KIT',
    'SET',
    'PACK',
    'BUNDLE',
    'LOT',
    'BATCH',
    'LOAD',
    'CARGO',
    'FREIGHT',
    'GOODS',
    'MATERIAL',
    'SUBSTANCE',
    'MATTER',
    'STUFF',
    'THING',
    'ITEM',
    'OBJECT',
    'ARTICLE',
    'PIECE',
    'UNIT',
    'ELEMENT',
    'COMPONENT',
    'PART',
    'SECTION',
    'SEGMENT',
    'DIVISION',
    'PORTION',
    'SHARE',
    'CUT',
    'SLICE',
    'PIECE',
    'BIT',
    'FRAGMENT',
    'CHUNK',
    'BLOCK',
    'MASS',
    'BULK',
    'VOLUME',
    'QUANTITY',
    'AMOUNT',
    'NUMBER',
    'COUNT',
    'TOTAL',
    'SUM',
    'AGGREGATE',
    'WHOLE',
    'COMPLETE',
    'FULL',
    'ENTIRE',
    'ALL',
    'EVERY',
    'EACH',
    'ANY',
    'SOME',
    'FEW',
    'MANY',
    'MUCH',
    'MORE',
    'LESS',
    'MOST',
    'LEAST',
    'FIRST',
    'LAST',
    'NEXT',
    'PREVIOUS',
    'CURRENT',
    'PRESENT',
    'PAST',
    'FUTURE',
    'NEW',
    'OLD',
    'YOUNG',
    'AGED',
    'FRESH',
    'STALE',
    'GOOD',
    'BAD',
    'RIGHT',
    'WRONG',
    'CORRECT',
    'INCORRECT',
    'TRUE',
    'FALSE',
    'YES',
    'NO',
    'ON',
    'OFF',
    'IN',
    'OUT',
    'UP',
    'DOWN',
    'HIGH',
    'LOW',
    'BIG',
    'SMALL',
    'LARGE',
    'LITTLE',
    'HEAVY',
    'LIGHT',
    'FAST',
    'SLOW',
    'HOT',
    'COLD',
    'HARD',
    'SOFT',
    'STRONG',
    'WEAK',
    'TOUGH',
    'FRAGILE',
    'SOLID',
    'LIQUID',
    'GAS',
    'PLASMA',
    'ENERGY',
    'POWER',
    'FORCE',
    'STRENGTH',
    'MIGHT',
    'ABILITY',
    'SKILL',
    'TALENT',
    'GIFT',
    'TRAIT',
    'QUALITY',
    'PROPERTY',
    'ATTRIBUTE',
    'CHARACTERISTIC',
    'FEATURE',
    'ASPECT',
    'FACET',
    'SIDE',
    'ANGLE',
    'VIEW',
    'LOOK',
    'APPEARANCE',
    'FORM',
    'SHAPE',
    'SIZE',
    'COLOR',
    'TEXTURE',
    'PATTERN',
    'DESIGN',
    'STYLE',
    'FASHION',
    'MODE',
    'MANNER',
    'WAY',
    'METHOD',
    'MEANS',
    'TECHNIQUE',
    'PROCESS',
    'PROCEDURE',
    'OPERATION',
    'ACTION',
    'ACT',
    'DEED',
    'MOVE',
    'STEP',
    'STAGE',
    'PHASE',
    'PERIOD',
    'TIME',
    'MOMENT',
    'INSTANT',
    'SECOND',
    'MINUTE',
    'HOUR',
    'DAY',
    'WEEK',
    'MONTH',
    'YEAR',
    'DECADE',
    'CENTURY',
    'ERA',
    'AGE',
    'EPOCH',
    'EON'
}

def is_special_equipment(equipment):
    """Check if equipment is special (non-weapon) equipment"""
    equipment_lower = equipment.lower()
    
    # Load weapon names from weapons.csv if not already loaded
    global weapon_names
    if 'weapon_names' not in globals():
        weapon_names = set()
        try:
            with open('weapons.csv', 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Add main name
                    if row['name']:
                        weapon_names.add(row['name'].lower())
                    # Add lookup names
                    if row['lookup_names']:
                        lookup_names = eval(row['lookup_names'])  # Safely evaluate the list string
                        weapon_names.update(name.lower() for name in lookup_names if name)
        except Exception as e:
            print(f"Warning: Could not load weapons.csv: {e}")
            # Fallback to basic weapon type checking
            return _is_special_equipment_fallback(equipment)
    
    # First check if it's an exact match for a known weapon
    if equipment_lower in weapon_names:
        return False
        
    # Check for special equipment prefixes
    if any(equipment_lower.startswith(prefix.lower()) for prefix in [
        'Ammo:', 'ISAmmo:', 'CLAmmo:', 'CASE', 'Endo-Steel',
        'Ferro-Fibrous', 'XL', 'Compact', 'Standard', 'Stealth',
        'ECM', 'BAP', 'C3', 'TAG', 'NARC', 'Probe', 'Targeting Computer',
        'Reactive', 'Reflective', 'Hardened'
    ]):
        return True
    
    # Check for ammo entries
    if 'ammo' in equipment_lower and '(' in equipment_lower:
        return True
    
    # Check for special equipment matches but exclude weapon-related terms
    return any(special.lower() in equipment_lower and not any(weapon in equipment_lower for weapon in [
        'laser', 'ppc', 'gauss', 'ac', 'lrm', 'srm', 'mrm', 'hag',
        'plasma', 'flamer', 'machine gun', 'rifle', 'thunderbolt',
        'autocannon', 'ultra', 'rotary', 'lb', 'artillery', 'thumper',
        'sniper', 'long tom', 'arrow iv', 'nail', 'rivet', 'hvac'
    ]) for special in special_equipment)

def _is_special_equipment_fallback(equipment):
    """Fallback method when weapons.csv cannot be loaded"""
    equipment_lower = equipment.lower()
    
    # Never filter out these weapon types
    if any(weapon in equipment_lower for weapon in [
        'laser', 'ppc', 'gauss', 'ac', 'lrm', 'srm', 'mrm', 'hag',
        'plasma', 'flamer', 'machine gun', 'rifle', 'thunderbolt',
        'autocannon', 'ultra', 'rotary', 'lb', 'artillery', 'thumper',
        'sniper', 'long tom', 'arrow iv', 'nail', 'rivet', 'hvac'
    ]):
        return False
    
    # Check for special equipment prefixes
    if any(equipment_lower.startswith(prefix.lower()) for prefix in [
        'Ammo:', 'ISAmmo:', 'CLAmmo:', 'CASE', 'Endo-Steel',
        'Ferro-Fibrous', 'XL', 'Compact', 'Standard', 'Stealth',
        'ECM', 'BAP', 'C3', 'TAG', 'NARC', 'Probe', 'Targeting Computer',
        'Reactive', 'Reflective', 'Hardened'
    ]):
        return True
    
    # Check for ammo entries
    if 'ammo' in equipment_lower and '(' in equipment_lower:
        return True
    
    # Check for special equipment matches
    return any(special.lower() in equipment_lower for special in special_equipment)

def parse_weapons_csv(weapons_file):
    weapons_data = {}
    weapon_lookup = {}  # Map of lookup names to canonical names
    try:
        with open(weapons_file, 'r') as f:
            reader = csv.reader(f)
            headers = next(reader)  # Get header row
            
            # Find column indices
            name_idx = headers.index('name')
            lookup_names_idx = headers.index('lookup_names')
            damage_idx = headers.index('damage')
            cluster_size_idx = headers.index('cluster_size')
            range_indices = [headers.index(x) for x in ['short_range', 'medium_range', 'long_range', 'extreme_range']]
            
            for row in reader:
                if len(row) >= max(name_idx, lookup_names_idx, damage_idx, cluster_size_idx, max(range_indices)) + 1:
                    name = row[name_idx]
                    if name:  # Skip empty names
                        try:
                            # Parse weapon data
                            damage = float(row[damage_idx]) if row[damage_idx] else 0.0
                            cluster = int(row[cluster_size_idx]) if row[cluster_size_idx] else 0
                            ranges = [int(row[i]) if row[i] and row[i].isdigit() else 0 for i in range_indices]
                            
                            # Store main weapon data
                            weapons_data[name.lower()] = {
                                'damage': damage,
                                'cluster_size': cluster,
                                'ranges': ranges
                            }
                            
                            # Add main name to lookup
                            weapon_lookup[name.lower()] = name
                            
                            # Process lookup names
                            if row[lookup_names_idx]:
                                lookup_names = row[lookup_names_idx].split('|')
                                for lookup_name in lookup_names:
                                    if lookup_name:
                                        weapon_lookup[lookup_name.lower()] = name
                                        
                        except (ValueError, IndexError) as e:
                            if name != 'name':  # Don't warn about header row
                                print(f"Warning: Could not parse weapon data for {name}: {e}")
                            continue
    except Exception as e:
        print(f"Error reading weapons file: {e}")
        return {}, {}
        
    # Add special weapons
    weapons_data['vehicle flamer'] = {
        'damage': 2.0,
        'cluster_size': 0,
        'ranges': [1, 2, 3, 0]
    }
        
    if not weapons_data:
        print("Warning: No weapon data was loaded")
    else:
        print(f"Loaded {len(weapons_data)} weapons with {len(weapon_lookup)} lookup names")
        
    return weapons_data, weapon_lookup

def is_weapon(item):
    # Skip empty items
    if not item:
        return False
        
    # Skip obvious non-weapons
    non_weapons = ['Ammo', 'CASE', 'ECM', 'Probe', 'Jump Jet', 'Sensors', 'Armor', 'System', 'Bay', 'Motive', 'Operating']
    if any(x in item for x in non_weapons):
        return False
        
    # Check for weapon keywords
    weapon_keywords = [
        'Laser', 'PPC', 'Gauss', 'AC', 'SRM', 'LRM', 'MRM', 'Machine Gun', 'Flamer', 'Artillery',
        'LBXAC', 'LBX', 'UAC', 'RAC', 'Thumper', 'Sniper', 'Cannon', 'Rifle', 'TAG', 'Narc'
    ]
    
    # Check for weapon prefixes
    weapon_prefixes = ['IS', 'CL', 'Clan']
    
    # Remove prefixes for checking
    item_no_prefix = item
    for prefix in weapon_prefixes:
        if item.startswith(prefix):
            item_no_prefix = item[len(prefix):]
            break
    
    return any(x in item_no_prefix for x in weapon_keywords)

def parse_blk(blk_file):
    weapons = []
    special_equipment = []
    try:
        with open(blk_file, 'r', encoding='utf-8') as f:
            in_equipment = False
            for line in f:
                line = line.strip()
                if not line:
                    continue
                    
                # Check for equipment sections
                if any(x in line for x in ['<Body Equipment>', '<Front Equipment>', '<Right Equipment>', 
                                         '<Left Equipment>', '<Rear Equipment>', '<Turret Equipment>']):
                    in_equipment = True
                    continue
                    
                # Check for end of equipment section
                if line.startswith('</') and 'Equipment>' in line:
                    in_equipment = False
                    continue
                    
                # Process equipment lines
                if in_equipment and not line.startswith('<'):
                    item = line.strip()
                    if is_weapon(item):
                        weapons.append(item)
                    else:
                        special_equipment.append(item)
    except UnicodeDecodeError:
        try:
            with open(blk_file, 'r', encoding='latin1') as f:
                in_equipment = False
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                        
                    # Check for equipment sections
                    if any(x in line for x in ['<Body Equipment>', '<Front Equipment>', '<Right Equipment>', 
                                             '<Left Equipment>', '<Rear Equipment>', '<Turret Equipment>']):
                        in_equipment = True
                        continue
                        
                    # Check for end of equipment section
                    if line.startswith('</') and 'Equipment>' in line:
                        in_equipment = False
                        continue
                        
                    # Process equipment lines
                    if in_equipment and not line.startswith('<'):
                        item = line.strip()
                        if is_weapon(item):
                            weapons.append(item)
                        else:
                            special_equipment.append(item)
        except Exception as e:
            print(f"Error reading file {blk_file}: {str(e)}")
            return None, None
    
    return weapons, special_equipment

def validate_blk_vs_csv(blk_file, csv_data):
    blk_weapons, special_equipment = parse_blk(blk_file)
    if not blk_weapons:
        print(f"Warning: No weapons or equipment found in {blk_file}")
        return
    
    vehicle_name = os.path.splitext(os.path.basename(blk_file))[0]
    if vehicle_name in csv_data:
        csv_weapons = csv_data[vehicle_name]
        if sorted(blk_weapons) != sorted(csv_weapons):
            print(f"\nMismatch found in {vehicle_name}:")
            print(f"BLK weapons: {sorted(blk_weapons)}")
            print(f"CSV weapons: {sorted(csv_weapons)}")
            if special_equipment:
                print(f"Special equipment: {sorted(special_equipment)}")
    else:
        print(f"Vehicle {vehicle_name} not found in CSV data")

def write_csv(data, output_file):
    # Define all columns based on the required format
    fieldnames = [
        'UnitType', 'Name', 'FullName', 'Common', 'Class', 'Model', 'Role', 'PV', 'BV',
        'Type', 'Size', 'Tonnage', 'ASMove', 'Short', 'Medium', 'Long', 'Overheat',
        'CBTMove', 'Armor', 'ArmorIcons', 'Structure', 'StructureIcons', 'TMM',
        'RegSkill', 'VetSkill', 'RegPV', 'VetPV', 'Specials', 'TUR', 'AMS', 'ECM2',
        'ECM6', 'PRB', 'IF', 'APC', 'CAR', 'ART', 'STL', 'MHQ', '', '', '', '', '',
        'SpecialRules', 'ImageURL', 'MULId', 'Weapons'
    ]
    
    # Add weapon columns (7 weapons max)
    for i in range(1, 8):
        fieldnames.extend([f'WepName{i}', f'Shots{i}', f'Dam{i}', f'Range{i}'])
    
    # Add combined damage columns
    for i in range(1, 8):
        fieldnames.append(f'CombDam{i}')

    # Create error log file for weapons with no shots and no damage
    with open('weapon_errors.txt', 'w') as error_file:
        error_file.write("Weapons with no shots and no damage:\n")

    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        # Sort data by name for consistent output
        sorted_data = sorted(data, key=lambda x: x['name'])
        
        for item in sorted_data:
            # Initialize row with empty values
            row = {field: '' for field in fieldnames}
            
            # Set basic vehicle info
            row['UnitType'] = 'Vehicle'
            row['Name'] = item['name']
            row['FullName'] = item['name']
            
            # Set special equipment flags
            special_equip = [x.upper() for x in item['special_equipment']]
            row['TUR'] = 'X' if any('TURRET' in x for x in special_equip) else ''
            row['AMS'] = 'X' if any('ANTIMISSILE' in x for x in special_equip) else ''
            row['ECM2'] = 'X' if any('ECM' in x for x in special_equip) else ''
            row['ECM6'] = 'X' if any('ANGEL' in x for x in special_equip) else ''
            row['PRB'] = 'X' if any('PROBE' in x for x in special_equip) else ''
            row['IF'] = 'X' if any('INFANTRY' in x for x in special_equip) else ''
            row['APC'] = 'X' if any('APC' in x for x in special_equip) else ''
            row['CAR'] = 'X' if any('CARGO' in x for x in special_equip) else ''
            row['ART'] = 'X' if any('ARTILLERY' in x for x in special_equip) else ''
            row['STL'] = 'X' if any('STEALTH' in x for x in special_equip) else ''
            row['MHQ'] = 'X' if any('HQ' in x for x in special_equip) else ''
            
            # Process weapons
            weapons = [normalize_weapon_name(w) for w in item['weapons']]
            weapons = [w for w in weapons if w]
            
            # Filter out zero-damage weapons
            filtered_weapons = []
            for weapon in weapons:
                base_weapon = weapon.replace(' (Slug)', '').replace(' (Pellet)', '')
                weapon_variants = [
                    base_weapon.lower(),
                    normalize_weapon_name(base_weapon).lower(),
                    f"is {base_weapon.lower()}",
                    f"clan {base_weapon.lower()}",
                    base_weapon.lower().replace('(vehicle)', '').strip(),
                    base_weapon.lower().replace('(st)', '').strip(),
                    base_weapon.lower().replace('(pt)', '').strip(),
                    base_weapon.lower().replace(':omni', '').strip()
                ]
                
                stats = None
                for variant in weapon_variants:
                    if variant in weapon_stats:
                        stats = weapon_stats[variant]
                        break

                if stats:
                    damage = float(stats.get('damage', 0))
                    # Handle variable damage weapons
                    if damage == 0:
                        if 'VSP' in weapon:
                            # VSP lasers average damage
                            if 'Large' in weapon:
                                damage = 9  # Average of 4-14
                            elif 'Medium' in weapon:
                                damage = 6  # Average of 3-9
                            elif 'Small' in weapon:
                                damage = 3  # Average of 1-5
                        elif 'Snub-Nose PPC' in weapon:
                            damage = 10  # Average damage across ranges
                        elif any(x in weapon.lower() for x in ['i narc', 'tag', 'narc']):
                            print(f"Removing zero-damage weapon from {item['name']}: {weapon}")
                            continue
                        
                        if damage == 0:  # If still zero after checks
                            with open('weapon_errors.txt', 'a') as error_file:
                                error_file.write(f"{item['name']}: {weapon}\n")
                            continue
                            
                    filtered_weapons.append(weapon)
                else:
                    with open('weapon_errors.txt', 'a') as error_file:
                        error_file.write(f"{item['name']}: {weapon} (No stats found)\n")

            if filtered_weapons:
                # Group identical weapons and count them
                weapon_groups = {}
                for weapon in filtered_weapons:
                    if weapon in weapon_groups:
                        weapon_groups[weapon] += 1
                    else:
                        weapon_groups[weapon] = 1
                
                # Create expanded weapon list to handle LBX modes
                expanded_weapons = []
                for weapon, count in weapon_groups.items():
                    if 'LB' in weapon and 'X AC' in weapon:
                        expanded_weapons.append((f"{weapon} (Slug)", count))
                        expanded_weapons.append(("-- OR --", 0))
                        expanded_weapons.append((f"{weapon} (Pellet)", count))
                    else:
                        expanded_weapons.append((weapon, count))
                
                # Set Weapons field to total count of unique weapons (excluding spacers)
                row['Weapons'] = str(len([w for w, _ in expanded_weapons if "-- OR --" not in w]))
                
                # Add weapons (up to 7)
                i = 1
                for weapon, count in expanded_weapons[:7]:
                    row[f'WepName{i}'] = weapon
                    
                    if weapon == "-- OR --":
                        row[f'Shots{i}'] = ""
                        row[f'Dam{i}'] = ""
                        row[f'Range{i}'] = ""
                        row[f'CombDam{i}'] = ""
                        i += 1
                        continue
                    
                    # Look up weapon stats
                    stats = None
                    base_weapon = weapon.replace(' (Slug)', '').replace(' (Pellet)', '')
                    weapon_variants = [
                        base_weapon.lower(),
                        normalize_weapon_name(base_weapon).lower(),
                        f"is {base_weapon.lower()}",
                        f"clan {base_weapon.lower()}",
                        base_weapon.lower().replace('(vehicle)', '').strip(),
                        base_weapon.lower().replace('(st)', '').strip(),
                        base_weapon.lower().replace('(pt)', '').strip(),
                        base_weapon.lower().replace(':omni', '').strip()
                    ]
                    
                    for variant in weapon_variants:
                        if variant in weapon_stats:
                            stats = weapon_stats[variant]
                            break
                    
                    if stats:
                        damage = float(stats.get('damage', 0))
                        rack_size = int(stats.get('rack_size', 0))
                        cluster_damage = float(stats.get('cluster_damage', 0))
                        is_streak = bool(stats.get('is_streak', False))
                        is_cluster = bool(stats.get('is_cluster', False))
                        
                        # Handle variable damage weapons
                        if damage == 0:
                            if 'VSP' in weapon:
                                if 'Large' in weapon:
                                    damage = 9  # Average of 4-14
                                elif 'Medium' in weapon:
                                    damage = 6  # Average of 3-9
                                elif 'Small' in weapon:
                                    damage = 3  # Average of 1-5
                            elif 'Snub-Nose PPC' in weapon:
                                damage = 10  # Average damage across ranges

                        # Handle LBX modes
                        if 'LB' in weapon and 'X AC' in weapon:
                            rack_size = int(re.search(r'LB (\d+)-X', weapon).group(1))
                            if '(Slug)' in weapon:
                                row[f'Shots{i}'] = str(count)
                                row[f'Dam{i}'] = str(rack_size)
                                row[f'CombDam{i}'] = f"{count}x{rack_size}"
                            else:  # Pellet mode
                                pellets = int((rack_size * 0.6) + 0.5)
                                total_pellets = pellets * count
                                row[f'Shots{i}'] = str(total_pellets)
                                row[f'Dam{i}'] = "1"
                                row[f'CombDam{i}'] = f"{total_pellets}x1"
                        # Handle Ultra and Rotary ACs
                        elif 'Ultra' in weapon and 'AC' in weapon:
                            rack_size = int(re.search(r'Ultra AC ?(\d+)', weapon).group(1))
                            total_shots = 2 * count
                            row[f'Shots{i}'] = str(total_shots)
                            row[f'Dam{i}'] = str(rack_size)
                            row[f'CombDam{i}'] = f"{total_shots}x{rack_size}"
                        elif 'Rotary' in weapon and 'AC' in weapon:
                            rack_size = int(re.search(r'Rotary AC ?(\d+)', weapon).group(1))
                            total_shots = 6 * count
                            row[f'Shots{i}'] = str(total_shots)
                            row[f'Dam{i}'] = str(rack_size)
                            row[f'CombDam{i}'] = f"{total_shots}x{rack_size}"
                        elif is_cluster:
                            if is_streak or any('ARTEMIS' in x for x in special_equip):
                                projectiles = rack_size
                            else:
                                projectiles = max(1, int((rack_size * 0.6) + 0.5))
                            
                            if 'srm' in weapon.lower():
                                projectile_damage = 2
                                total_damage = projectiles * projectile_damage
                                groups = total_damage // 2
                                total_shots = groups * count
                                damage = 2
                            else:
                                total_damage = projectiles
                                groups = max(1, int(total_damage / 5))
                                total_shots = groups * count
                                damage = 5
                            
                            row[f'Shots{i}'] = str(total_shots)
                            row[f'Dam{i}'] = str(int(damage))
                            row[f'CombDam{i}'] = f"{total_shots}x{row[f'Dam{i}']}"
                        else:
                            # Always show shots, even if it's 1
                            row[f'Shots{i}'] = str(count)
                            row[f'Dam{i}'] = str(int(damage)) if float(damage) == int(float(damage)) else str(damage)
                            row[f'CombDam{i}'] = f"{count}x{row[f'Dam{i}']}"
                            
                        # Format range string
                        short_range = int(stats.get('short_range', 0))
                        medium_range = int(stats.get('medium_range', 0))
                        long_range = int(stats.get('long_range', 0))
                        if any(r > 0 for r in [short_range, medium_range, long_range]):
                            row[f'Range{i}'] = f"{short_range}/{medium_range}/{long_range}"
                    else:
                        print(f"Warning: No stats found for weapon: {weapon}")
                    
                    i += 1
                
            writer.writerow(row)

def read_csv_weapons(filename):
    """Read weapons from CSV file"""
    csv_data = {}
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            weapons = []
            # Read up to 7 weapons
            for i in range(1, 8):
                weapon_name = row.get(f'WepName{i}', '').strip()
                if weapon_name:
                    weapons.append(weapon_name)
            if weapons:
                csv_data[row['Name']] = weapons
    return csv_data

def process_blk_files():
    """Process BLK files and extract weapon data"""
    processed_data = []
    for root, _, files in os.walk("../megamek/data/mekfiles/vehicles"):
        for file in files:
            if file.endswith('.blk'):
                blk_file = os.path.join(root, file)
                weapons, special_equipment = parse_blk(blk_file)
                if weapons:
                    # Get vehicle name from file name
                    vehicle_name = os.path.splitext(file)[0]
                    # Store as dictionary with required fields
                    processed_data.append({
                        'name': vehicle_name,
                        'weapons': weapons,
                        'special_equipment': special_equipment or []
                    })
    return processed_data

def normalize_weapon_name(name):
    if not name:
        return name
        
    # Check if it's a Clan weapon before removing prefixes
    is_clan = name.startswith(('CL', 'Clan'))
        
    # Remove common prefixes
    name = re.sub(r'^(IS|CL|Clan)', '', name)
    
    # Handle special suffixes and markers
    name = re.sub(r'\(Vehicle\)', '', name)
    name = re.sub(r'\(ST\)', '', name)
    name = re.sub(r'\(PT\)', '', name)
    name = re.sub(r':OMNI', '', name)
    name = re.sub(r':SIZE:\d+\.?\d*', '', name)
    
    # Handle rifle weapons as a special case
    rifle_match = re.search(r'Rifle\s*\((Cannon|Machine Gun|Laser|Support),\s*(Light|Medium|Heavy|Support|Semi-Portable)\)', name)
    if rifle_match:
        weapon_type = rifle_match.group(1)
        size = rifle_match.group(2)
        if weapon_type == "Cannon":
            name = f"{size} Rifle"
        else:
            name = f"{size} {weapon_type}"
            
    # Handle special weapon variants
    name = re.sub(r'ImprovedHeavyGaussRifle', 'Improved Heavy Gauss Rifle', name)
    name = re.sub(r'LargeChemLaser', 'Large Chemical Laser', name)
    name = re.sub(r'MediumChemLaser', 'Medium Chemical Laser', name)
    name = re.sub(r'SmallChemLaser', 'Small Chemical Laser', name)
    name = re.sub(r'LargeVariableSpeedLaser', 'Large VSP Laser', name)
    name = re.sub(r'MediumVariableSpeedLaser', 'Medium VSP Laser', name)
    name = re.sub(r'SmallVariableSpeedLaser', 'Small VSP Laser', name)
    name = re.sub(r'Hyper Velocity Auto Cannon[/](\d+)', r'Hyper Velocity AC/\1', name)
    name = re.sub(r'LongTomCannon', 'Long Tom Cannon', name)
    name = re.sub(r'Machine Gun \((Semi-Portable)\)', r'\1 Machine Gun', name)
    
    # Handle weapon calibers and types
    name = re.sub(r'LBXAC(\d+)', r'LB \1-X AC', name)
    name = re.sub(r'LB(\d+)-XAC', r'LB \1-X AC', name)
    name = re.sub(r'UltraAC(\d+)', r'Ultra AC\1', name)
    name = re.sub(r'RotaryAC(\d+)', r'Rotary AC\1', name)
    name = re.sub(r'LightAC(\d+)', r'Light AC\1', name)
    name = re.sub(r'Light Auto Cannon/(\d+)', r'Light AC/\1', name)
    name = re.sub(r'Auto Cannon/(\d+)', r'AC/\1', name)
    
    # Handle special equipment and modifiers
    name = re.sub(r'TAG', 'TAG', name)
    name = re.sub(r'SRM(\d+)IOS', r'SRM \1 IOS', name)
    name = re.sub(r'ExtendedLRM(\d+)', r'Extended LRM \1', name)
    name = re.sub(r'StreakLRM(\d+)', r'Streak LRM \1', name)
    name = re.sub(r'StreakSRM(\d+)', r'Streak SRM \1', name)
    name = re.sub(r'SNPPC', r'Snub-Nose PPC', name)
    name = re.sub(r'ImprovedNarc', r'i Narc', name)
    name = re.sub(r'iNarc Pods', r'i Narc Pods', name)
    
    # Split camelCase into words
    name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
    
    # Normalize ER and other common prefixes
    name = re.sub(r'ER([A-Z])', r'ER \1', name)
    name = re.sub(r'Heavy([A-Z])', r'Heavy \1', name)
    name = re.sub(r'Light([A-Z])', r'Light \1', name)
    
    # Add spaces between weapon type and numbers
    name = re.sub(r'([A-Za-z])(\d+)', r'\1 \2', name)
    name = re.sub(r'(\d+)([A-Za-z])', r'\1 \2', name)
    
    # Clean up spaces and final formatting
    name = re.sub(r'\s+', ' ', name)
    name = name.strip()
    
    # Special case for Flamer (Vehicle)
    if "Flamer (Vehicle)" in name:
        name = "Flamer"
        
    # Add back Clan prefix if it was a Clan weapon
    if is_clan:
        name = "Clan " + name
    
    return name

def get_cluster_hits(rack_size, is_streak_or_artemis):
    """Get number of hits from cluster table based on rack size and if Streak/Artemis"""
    # Use roll of 11 for Streak/Artemis weapons, 7 for regular weapons
    roll = 11 if is_streak_or_artemis else 7
    
    # Cluster hits table implementation based on the provided image
    if roll == 2:
        if rack_size <= 2: return 1
        elif rack_size <= 4: return 1
        elif rack_size <= 6: return 2
        elif rack_size <= 8: return 3
        elif rack_size <= 10: return 3
        elif rack_size <= 12: return 4
        elif rack_size <= 14: return 5
        elif rack_size <= 16: return 5
        elif rack_size <= 18: return 6
        elif rack_size <= 20: return 7
        else: return 8
    elif roll == 3:
        if rack_size <= 2: return 1
        elif rack_size <= 4: return 1
        elif rack_size <= 6: return 2
        elif rack_size <= 8: return 3
        elif rack_size <= 10: return 3
        elif rack_size <= 12: return 4
        elif rack_size <= 14: return 5
        elif rack_size <= 16: return 5
        elif rack_size <= 18: return 6
        elif rack_size <= 20: return 7
        else: return 8
    elif roll == 4:
        if rack_size <= 2: return 1
        elif rack_size <= 4: return 2
        elif rack_size <= 6: return 2
        elif rack_size <= 8: return 3
        elif rack_size <= 10: return 4
        elif rack_size <= 12: return 4
        elif rack_size <= 14: return 5
        elif rack_size <= 16: return 6
        elif rack_size <= 18: return 7
        elif rack_size <= 20: return 8
        else: return 9
    elif roll == 5:
        if rack_size <= 2: return 1
        elif rack_size <= 4: return 2
        elif rack_size <= 6: return 3
        elif rack_size <= 8: return 4
        elif rack_size <= 10: return 5
        elif rack_size <= 12: return 7
        elif rack_size <= 14: return 8
        elif rack_size <= 16: return 9
        elif rack_size <= 18: return 10
        elif rack_size <= 20: return 11
        else: return 12
    elif roll == 6:
        if rack_size <= 2: return 1
        elif rack_size <= 4: return 2
        elif rack_size <= 6: return 3
        elif rack_size <= 8: return 4
        elif rack_size <= 10: return 5
        elif rack_size <= 12: return 7
        elif rack_size <= 14: return 8
        elif rack_size <= 16: return 9
        elif rack_size <= 18: return 10
        elif rack_size <= 20: return 11
        else: return 12
    elif roll == 7:
        if rack_size <= 2: return 1
        elif rack_size <= 4: return 2
        elif rack_size <= 6: return 3
        elif rack_size <= 8: return 4
        elif rack_size <= 10: return 5
        elif rack_size <= 12: return 6
        elif rack_size <= 14: return 8
        elif rack_size <= 16: return 9
        elif rack_size <= 18: return 10
        elif rack_size <= 20: return 11
        else: return 12
    elif roll == 8:
        if rack_size <= 2: return 2
        elif rack_size <= 4: return 2
        elif rack_size <= 6: return 3
        elif rack_size <= 8: return 4
        elif rack_size <= 10: return 5
        elif rack_size <= 12: return 6
        elif rack_size <= 14: return 8
        elif rack_size <= 16: return 9
        elif rack_size <= 18: return 10
        elif rack_size <= 20: return 11
        else: return 12
    elif roll == 9:
        if rack_size <= 2: return 2
        elif rack_size <= 4: return 2
        elif rack_size <= 6: return 3
        elif rack_size <= 8: return 4
        elif rack_size <= 10: return 5
        elif rack_size <= 12: return 6
        elif rack_size <= 14: return 8
        elif rack_size <= 16: return 9
        elif rack_size <= 18: return 10
        elif rack_size <= 20: return 11
        else: return 12
    elif roll == 10:
        if rack_size <= 2: return 2
        elif rack_size <= 4: return 3
        elif rack_size <= 6: return 3
        elif rack_size <= 8: return 4
        elif rack_size <= 10: return 5
        elif rack_size <= 12: return 6
        elif rack_size <= 14: return 8
        elif rack_size <= 16: return 9
        elif rack_size <= 18: return 10
        elif rack_size <= 20: return 11
        else: return 12
    elif roll == 11:
        if rack_size <= 2: return 2
        elif rack_size <= 4: return 3
        elif rack_size <= 6: return 4
        elif rack_size <= 8: return 5
        elif rack_size <= 10: return 6
        elif rack_size <= 12: return 8
        elif rack_size <= 14: return 10
        elif rack_size <= 16: return 11
        elif rack_size <= 18: return 12
        elif rack_size <= 20: return 14
        else: return 15
    elif roll == 12:
        if rack_size <= 2: return 2
        elif rack_size <= 4: return 3
        elif rack_size <= 6: return 4
        elif rack_size <= 8: return 5
        elif rack_size <= 10: return 6
        elif rack_size <= 12: return 8
        elif rack_size <= 14: return 10
        elif rack_size <= 16: return 11
        elif rack_size <= 18: return 12
        elif rack_size <= 20: return 14
        else: return 15
    else:
        return rack_size  # For very small racks, hit with all

def main():
    # Process BLK files
    processed_data = process_blk_files()
    
    # Write to CSV with proper formatting
    write_csv(processed_data, CSV_FILE)
    
    # Read CSV data for validation using the new function
    csv_data = read_csv_weapons(CSV_FILE)
    
    # Validate BLK files against CSV data
    for root, _, files in os.walk("../megamek/data/mekfiles/vehicles"):
        for file in files:
            if file.endswith('.blk'):
                blk_file = os.path.join(root, file)
                validate_blk_vs_csv(blk_file, csv_data)

if __name__ == '__main__':
    main() 