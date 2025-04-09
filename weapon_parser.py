import os
import re
import csv
from dataclasses import dataclass, asdict
from typing import Optional, Dict, List, Set

@dataclass
class WeaponData:
    name: str = ""
    internal_name: str = ""
    display_name: str = ""
    lookup_names: List[str] = None  # Add lookup names field
    short_range: int = 0
    medium_range: int = 0
    long_range: int = 0
    extreme_range: int = 0
    minimum_range: int = 0
    rack_size: int = 0
    damage: float = 0.0
    cluster_damage: float = 0.0  # For LBX weapons in cluster mode
    cluster_size: int = 0  # For LBX weapons, number of submunitions
    heat: int = 0
    tonnage: float = 0.0
    criticals: int = 0
    ammo_type: str = ""
    weapon_class: str = ""
    parent_class: str = ""
    file_path: str = ""
    tech_base: str = ""
    bv: int = 0
    cost: int = 0
    is_lbx: bool = False

    def __init__(self, file_path=None):
        self.name = ""
        self.internal_name = ""
        self.display_name = ""
        self.lookup_names = []  # Initialize empty list
        self.short_range = 0
        self.medium_range = 0
        self.long_range = 0
        self.extreme_range = 0
        self.minimum_range = 0
        self.rack_size = 0
        self.damage = 0.0
        self.cluster_damage = 0.0
        self.cluster_size = 0
        self.heat = 0
        self.tonnage = 0.0
        self.criticals = 0
        self.ammo_type = ""
        self.weapon_class = ""
        self.parent_class = ""
        self.file_path = file_path if file_path else ""
        self.tech_base = ""
        self.bv = 0
        self.cost = 0
        self.is_lbx = False

    def to_csv_row(self):
        return [
            self.name,
            self.internal_name,
            self.display_name,
            "|".join(self.lookup_names),  # Join lookup names with pipe separator
            self.short_range,
            self.medium_range,
            self.long_range,
            self.extreme_range,
            self.minimum_range,
            self.rack_size,
            self.damage,
            self.cluster_damage,
            self.cluster_size,
            self.heat,
            self.tonnage,
            self.criticals,
            self.ammo_type,
            self.weapon_class,
            self.parent_class,
            self.file_path,
            self.tech_base,
            self.bv,
            self.cost,
            self.is_lbx
        ]

    @staticmethod
    def get_csv_header():
        return [
            "name",
            "internal_name",
            "display_name",
            "lookup_names",  # Add lookup_names to header
            "short_range",
            "medium_range",
            "long_range",
            "extreme_range",
            "minimum_range",
            "rack_size",
            "damage",
            "cluster_damage",
            "cluster_size",
            "heat",
            "tonnage",
            "criticals",
            "ammo_type",
            "weapon_class",
            "parent_class",
            "file_path",
            "tech_base",
            "bv",
            "cost",
            "is_lbx"
        ]

class WeaponParser:
    def __init__(self, base_path: str):
        self.base_path = base_path
        self.weapon_cache: Dict[str, WeaponData] = {}
        self.processed_files: Set[str] = set()
        
    def parse_java_file(self, file_path: str) -> Optional[WeaponData]:
        if file_path in self.weapon_cache:
            return self.weapon_cache[file_path]
            
        if file_path in self.processed_files:
            return None
            
        self.processed_files.add(file_path)
            
        try:
            print(f"Parsing file: {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            weapon = WeaponData(file_path=file_path)
            
            # Check if this is an LBX weapon
            weapon.is_lbx = "LBXACWeapon" in content
            
            # Extract name
            name_match = re.search(r'name\s*=\s*"([^"]+)"', content)
            if name_match:
                weapon.name = name_match.group(1)
                weapon.lookup_names.append(weapon.name)  # Add primary name to lookup names
                print(f"Found name: {weapon.name}")
                
            # Extract internal name from setInternalName
            internal_name_match = re.search(r'setInternalName\("([^"]+)"\)', content)
            if internal_name_match:
                weapon.internal_name = internal_name_match.group(1)
                weapon.lookup_names.append(weapon.internal_name)  # Add internal name to lookup names
                print(f"Found internal name: {weapon.internal_name}")
            else:
                # Extract from class name if setInternalName not found
                class_name_match = re.search(r'public\s+class\s+(\w+)\s+extends', content)
                if class_name_match:
                    weapon.internal_name = class_name_match.group(1)
                    weapon.lookup_names.append(weapon.internal_name)
                    print(f"Found internal name from class: {weapon.internal_name}")
                
            # Extract display name
            display_name_match = re.search(r'displayName\s*=\s*"([^"]+)"', content)
            if display_name_match:
                weapon.display_name = display_name_match.group(1)
                weapon.lookup_names.append(weapon.display_name)  # Add display name to lookup names
                print(f"Found display name: {weapon.display_name}")
                
            # Extract all lookup names
            lookup_pattern = r'addLookupName\("([^"]+)"\)'
            lookup_names = re.findall(lookup_pattern, content)
            for lookup_name in lookup_names:
                if lookup_name not in weapon.lookup_names:
                    weapon.lookup_names.append(lookup_name)
                    print(f"Found lookup name: {lookup_name}")
                
            # Extract ranges
            ranges_match = re.search(r'shortRange\s*=\s*(\d+).*?mediumRange\s*=\s*(\d+).*?longRange\s*=\s*(\d+).*?extremeRange\s*=\s*(\d+)', content, re.DOTALL)
            if ranges_match:
                weapon.short_range = int(ranges_match.group(1))
                weapon.medium_range = int(ranges_match.group(2))
                weapon.long_range = int(ranges_match.group(3))
                weapon.extreme_range = int(ranges_match.group(4))
                print(f"Found ranges: {weapon.minimum_range}/{weapon.short_range}/{weapon.medium_range}/{weapon.long_range}/{weapon.extreme_range}")
                
            # Extract minimum range
            min_range_match = re.search(r'minimumRange\s*=\s*(\d+)', content)
            if min_range_match:
                weapon.minimum_range = int(min_range_match.group(1))
                
            # Extract rack size from name if it's a missile weapon
            if any(x in weapon.name for x in ["LRM", "SRM", "MRM", "ATM"]):
                rack_match = re.search(r'(?:LRM|SRM|MRM|ATM)\s*(\d+)', weapon.name)
                if rack_match:
                    weapon.rack_size = int(rack_match.group(1))
                    weapon.damage = weapon.rack_size * 1.0  # Each missile does 1 damage
                    print(f"Found rack size: {weapon.rack_size}")
                    
            # Extract damage
            damage_match = re.search(r'damage\s*=\s*(\d+)', content)
            if damage_match:
                weapon.damage = float(damage_match.group(1))
                print(f"Found damage: {weapon.damage}")
                
            # For LBX weapons, set cluster values
            if weapon.is_lbx or "LBX" in weapon.parent_class or "LB-X" in weapon.name or "LB X" in weapon.name:
                weapon.cluster_size = int(weapon.damage)
                weapon.cluster_damage = 1.0
                print(f"Found LBX weapon. Normal Damage: {weapon.damage}, Cluster Size: {weapon.cluster_size}, Cluster Damage: {weapon.cluster_damage}")
                
            # Extract heat
            heat_match = re.search(r'heat\s*=\s*(\d+)', content)
            if heat_match:
                weapon.heat = int(heat_match.group(1))
                print(f"Found heat: {weapon.heat}")
                
            # Extract tonnage
            tonnage_match = re.search(r'tonnage\s*=\s*(\d+\.?\d*)', content)
            if tonnage_match:
                weapon.tonnage = float(tonnage_match.group(1))
                print(f"Found tonnage: {weapon.tonnage}")
                
            # Extract criticals
            criticals_match = re.search(r'criticals\s*=\s*(\d+)', content)
            if criticals_match:
                weapon.criticals = int(criticals_match.group(1))
                print(f"Found criticals: {weapon.criticals}")
                
            # Extract ammo type
            ammo_match = re.search(r'ammoType\s*=\s*(\w+)', content)
            if ammo_match:
                weapon.ammo_type = ammo_match.group(1)
                print(f"Found ammo type: {weapon.ammo_type}")
                
            # Extract parent class
            parent_match = re.search(r'extends\s+(\w+)', content)
            if parent_match:
                weapon.parent_class = parent_match.group(1)
                print(f"Found parent class: {weapon.parent_class}")
                
                # Find and parse parent file to get weapon class
                parent_file = self.find_parent_file(weapon.parent_class, os.path.dirname(file_path))
                if parent_file:
                    print(f"Found parent file: {parent_file}")
                    with open(parent_file, 'r') as f:
                        parent_content = f.read()
                        parent_parent_match = re.search(r'extends\s+(\w+)', parent_content)
                        if parent_parent_match:
                            weapon.weapon_class = parent_parent_match.group(1)
                            print(f"Found weapon class: {weapon.weapon_class}")
            
            # Extract tech base
            if "CLAN" in file_path:
                weapon.tech_base = "CLAN"
            else:
                weapon.tech_base = "IS"
            print(f"Found tech base: {weapon.tech_base}")
            
            # Extract BV
            bv_match = re.search(r'bv\s*=\s*(\d+)', content)
            if bv_match:
                weapon.bv = int(bv_match.group(1))
                print(f"Found BV: {weapon.bv}")
            
            # Extract cost
            cost_match = re.search(r'cost\s*=\s*(\d+)', content)
            if cost_match:
                weapon.cost = int(cost_match.group(1))
                print(f"Found cost: {weapon.cost}")
            
            self.weapon_cache[file_path] = weapon
            
            # If we have a parent class, try to find and parse it
            if weapon.parent_class:
                parent_data = self.parse_java_file(self.find_parent_file(weapon.parent_class, os.path.dirname(file_path)))
                if parent_data:
                    # Inherit values that aren't set in the child
                    for field in weapon.__annotations__:
                        if field != 'file_path' and field != 'parent_class':
                            child_value = getattr(weapon, field)
                            parent_value = getattr(parent_data, field)
                            if not child_value and parent_value:
                                setattr(weapon, field, parent_value)
                             
            return weapon
            
        except Exception as e:
            print(f"Error parsing {file_path}: {str(e)}")
            return None
            
    def find_parent_file(self, parent_class: str, start_dir: str) -> Optional[str]:
        """Search for parent class file in the weapons directory structure"""
        weapons_dir = os.path.dirname(os.path.dirname(start_dir))  # Go up to weapons dir
        print(f"Searching for parent class {parent_class} starting from {weapons_dir}")
        
        for root, _, files in os.walk(weapons_dir):
            for file in files:
                if file == f"{parent_class}.java":
                    return os.path.join(root, file)
        return None
        
    def process_weapons_directory(self) -> List[WeaponData]:
        """Process all weapon files in the directory structure"""
        weapons = []
        print(f"Processing weapons directory: {self.base_path}")
        
        for root, _, files in os.walk(self.base_path):
            for file in files:
                if file.endswith('.java'):
                    file_path = os.path.join(root, file)
                    weapon_data = self.parse_java_file(file_path)
                    if weapon_data:
                        weapons.append(weapon_data)
                        
        return weapons

def normalize_weapon_name(name):
    """Normalize weapon name to a standard format"""
    if not name:
        return None
        
    # Remove ammo designations
    if 'ammo' in name.lower():
        return None
        
    # Handle Clan prefixes
    has_clan = any(x in name.lower() for x in ['clan', 'cl'])
    if has_clan:
        # Remove Clan/CL prefix
        name = re.sub(r'^(clan\s+|cl)', '', name, flags=re.IGNORECASE).strip()
    
    # Remove OMNI tags and other suffixes
    name = name.split(':')[0]
    name = re.sub(r'\([^)]*\)', '', name)  # Remove parenthetical notes
    
    # Remove size/weight specifiers
    name = re.sub(r'^(light |medium |heavy |assault )', '', name, flags=re.IGNORECASE)
    
    # Convert to title case
    name = name.title()
    
    # Standard replacements
    replacements = {
        'Ppc': 'PPC',
        'Lrm': 'LRM',
        'Srm': 'SRM',
        'Mrm': 'MRM',
        'Mg': 'Machine Gun',
        'Ultra': 'Ultra',
        'Lb': 'LB',
        'Er': 'ER',
        'Hag': 'HAG',
        'Ac': 'AC',
        'Atm': 'ATM',
        'Iatm': 'iATM',
        'Mml': 'MML',
        'Rac': 'RAC',
        'Lac': 'LAC',
        'Uac': 'UAC',
        'Lbx': 'LB-X',
        'Streak': 'Streak',
        'Ap': 'AP',
        'Vsp': 'VSP',
        'Snub-Nosed': 'Snub-Nosed',
        'Snubnosed': 'Snub-Nosed',
        'Snppc': 'Snub-Nosed PPC',
        'Lppc': 'Light PPC',
        'Hppc': 'Heavy PPC',
        'Mga': 'Machine Gun Array',
        'Lmga': 'Light Machine Gun Array',
        'Hmga': 'Heavy Machine Gun Array',
        'Vsplaser': 'VSP Laser',
        'Xpulselaser': 'X-Pulse Laser',
        'Chemicallaser': 'Chemical Laser',
        'Chemlaser': 'Chemical Laser',
        'Arrowiv': 'Arrow IV',
        'Arrow-Iv': 'Arrow IV',
        'Arrow-4': 'Arrow IV',
        'Thunderbolt': 'Thunderbolt',
        'Tbt': 'Thunderbolt',
        'Thumperartillery': 'Thumper Artillery',
        'Thumpercannon': 'Thumper Cannon',
        'Plasmarifle': 'Plasma Rifle',
        'Plasmacannon': 'Plasma Cannon',
        'Gaussrifle': 'Gauss Rifle',
        'Isstreak': 'Streak',
        'Issmallpulselaser': 'Small Pulse Laser',
        'Ismediumpulselaser': 'Medium Pulse Laser',
        'Islargepulselaser': 'Large Pulse Laser',
        'Iserppc': 'ER PPC',
        'Iser': 'ER',
        'Issrm': 'SRM',
        'Islrm': 'LRM',
        'Ismrm': 'MRM',
        'Isac': 'AC',
        'Isuac': 'Ultra AC',
        'Israc': 'Rotary AC',
        'Islbx': 'LB-X AC',
        'Isheavygaussrifle': 'Heavy Gauss Rifle',
        'Isgaussrifle': 'Gauss Rifle',
        'Isplasmarifle': 'Plasma Rifle',
        'Isplasmacannon': 'Plasma Cannon',
        'Ismga': 'Machine Gun Array',
        'Os': '',  # Remove OS suffix,
    }
    
    # First pass - handle basic replacements
    for old, new in replacements.items():
        name = re.sub(rf'\b{old}\b', new, name, flags=re.IGNORECASE)
    
    # Second pass - handle weapon variants
    name = re.sub(r'Ultra\s*Ac\s*(\d+)', r'Ultra AC/\1', name, flags=re.IGNORECASE)
    name = re.sub(r'Rotary\s*Ac\s*(\d+)', r'Rotary AC/\1', name, flags=re.IGNORECASE)
    name = re.sub(r'Lb[-\s]*X\s*Ac\s*(\d+)', r'LB-X AC/\1', name, flags=re.IGNORECASE)
    name = re.sub(r'Streak\s*Srm\s*(\d+)', r'Streak SRM/\1', name, flags=re.IGNORECASE)
    name = re.sub(r'Streak\s*Lrm\s*(\d+)', r'Streak LRM/\1', name, flags=re.IGNORECASE)
    name = re.sub(r'Er\s*(Small|Medium|Large)\s*Laser', r'ER \1 Laser', name, flags=re.IGNORECASE)
    name = re.sub(r'Ap\s*Gauss\s*Rifle', r'AP Gauss Rifle', name, flags=re.IGNORECASE)
    name = re.sub(r'Auto\s*Cannon', r'Autocannon', name, flags=re.IGNORECASE)
    
    # Handle special Clan weapon formats
    name = re.sub(r'Streak\s*(\d+)', r'Streak LRM/\1', name, flags=re.IGNORECASE)  # Clan Streak defaults to LRM
    
    # Add back Clan prefix if it was present
    if has_clan:
        name = f"Clan {name}"
    
    return name.strip()

def is_weapon(item):
    """Check if an item is a weapon"""
    if not item:
        return False
        
    # Skip if it's clearly not a weapon
    if any(x in item.lower() for x in ['ammo', 'case', 'ecm', 'probe', 'tag', 'narc', 'ams', 'artemis', 'targeting computer']):
        return False
        
    # Check for weapon keywords
    weapon_keywords = [
        'laser', 'ppc', 'gauss', 'ac', 'lrm', 'srm', 'mrm', 'mg', 'machine gun',
        'flamer', 'thunderbolt', 'plasma', 'rifle', 'cannon', 'artillery',
        'streak', 'ultra', 'lb-x', 'lb x', 'rotary', 'rac', 'hag', 'atm',
        'pulse', 'er', 'heavy', 'light', 'medium', 'small', 'large'
    ]
    
    # Convert to lowercase for case-insensitive comparison
    item_lower = item.lower()
    
    # Check each keyword
    for keyword in weapon_keywords:
        if keyword in item_lower:
            return True
            
    return False

def parse_weapons(equipment_list):
    """Parse a list of equipment and return weapons"""
    weapons = []
    for item in equipment_list:
        if not is_weapon(item):
            continue
            
        name = normalize_weapon_name(item)
        if name:
            weapons.append(name)
            
    return weapons

def get_weapon_count(weapon_name):
    """Return the actual count of a weapon (not multiplied by cluster hits)"""
    # Extract the weapon size if present (e.g. LRM 20, SRM 6)
    match = re.search(r'\d+$', weapon_name)
    if not match:
        return 1
        
    # For cluster weapons, return 1 since we count them as individual weapons
    if any(x in weapon_name.upper() for x in ['LRM', 'SRM', 'MRM', 'ATM', 'HAG', 'LB-X']):
        return 1
        
    return 1  # Default to 1 for all other weapons

def format_weapon_list(weapons):
    """Format the list of weapons with proper counts"""
    weapon_counts = {}
    for weapon in weapons:
        count = get_weapon_count(weapon)
        if weapon in weapon_counts:
            weapon_counts[weapon] += count
        else:
            weapon_counts[weapon] = count
            
    return [weapon for weapon, count in weapon_counts.items() for _ in range(count)]

def main():
    # Base path to the weapons directory - now look at all weapons
    base_path = r"D:\Games\Downloads\mekhq-windows-0.49.19.1\MMSource\megamek-master\megamek\src\megamek\common\weapons"
    print(f"Starting weapon parser with base path: {base_path}")
    
    if not os.path.exists(base_path):
        print(f"Error: Path does not exist: {base_path}")
        return
        
    parser = WeaponParser(base_path)
    weapons = parser.process_weapons_directory()
    
    # Print results
    print(f"\nFound {len(weapons)} weapons")
    
    # Save to CSV
    csv_file = "weapons.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=WeaponData.__annotations__.keys())
        writer.writeheader()
        for weapon in weapons:
            writer.writerow(asdict(weapon))
            
    print(f"\nWeapon data saved to {csv_file}")
    
    # Print sample of parsed weapons
    print("\nSample of parsed weapons:")
    for weapon in weapons[:5]:
        print("\nWeapon Details:")
        print(f"Name: {weapon.name}")
        print(f"Internal Name: {weapon.internal_name}")
        print(f"Display Name: {weapon.display_name}")
        print(f"Ranges: {weapon.minimum_range}/{weapon.short_range}/{weapon.medium_range}/{weapon.long_range}/{weapon.extreme_range}")
        if weapon.is_lbx:
            print(f"Normal Damage: {weapon.damage}")
            print(f"Cluster Size: {weapon.cluster_size}")
            print(f"Cluster Damage: {weapon.cluster_damage}")
        else:
            print(f"Damage: {weapon.damage}")
        print(f"Heat: {weapon.heat}")
        print(f"Tonnage: {weapon.tonnage}")
        print(f"Criticals: {weapon.criticals}")
        print(f"Ammo Type: {weapon.ammo_type}")
        print(f"Tech Base: {weapon.tech_base}")
        print(f"BV: {weapon.bv}")
        print(f"Cost: {weapon.cost}")
        print(f"Parent Class: {weapon.parent_class}")
        print(f"File: {weapon.file_path}")

if __name__ == "__main__":
    main() 