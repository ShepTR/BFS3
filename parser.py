import os
import re
import pprint
import csv
import math
import unicodedata


def parse_weaponType_data(file_path):  # Parses things like LRMWeapon.java
    """
    Parses weapon range and weapon type data from a Java-like class definition and returns a dictionary.

    Args:
        file_path (str): The path to the file containing the weapon data.

    Returns:
        dict: A dictionary containing the weapon type and range attributes.
    """
    weaponType = {}
    try:
        with open(file_path, 'r') as f:
            weapon_text = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return weaponType  # Return an empty dictionary if file not found

    lines = weapon_text.split('\n')
    weapon_type = None

    for line in lines:
        line = line.strip()
        if 'public abstract class' in line:
            weaponType['weaponType'] = line.split()[3].strip()
        elif 'public class' in line:
            weaponType['weaponType'] = line.split()[2].strip()
        elif 'shortRange =' in line:
            weaponType['shortRange'] = line.split('=')[1].strip().rstrip(';')
        elif 'mediumRange =' in line:
            weaponType['mediumRange'] = line.split('=')[1].strip().rstrip(';')
        elif 'longRange =' in line:
            weaponType['longRange'] = line.split('=')[1].strip().rstrip(';')
    return weaponType


def parse_weapon_data(file_path, weaponTypes_list):  # Parses things like ISLRM20.java
    """
    Parses weapon range and weapon type data from a Java-like class definition and returns a dictionary.

    Args:
        file_path (str): The path to the file containing the weapon data.

    Returns:
        dict: A dictionary containing the weapon type and range attributes.
    """
    weapon = {}
    nameList = []
    weaponsList = []
    weapon['displayName'] = ''
    weapon['extends'] = ''
    weapon['extendedBy'] = ''
    weapon['damage'] = 'NODAMAGEFIXME'

    try:
        with open(file_path, 'r') as f:
            weapon_text = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return weaponType  # Return an empty dictionary if file not found

    lines = weapon_text.split('\n')

    for line in lines:
        line = line.strip()
        if line.startswith("this."):
            line = line[len("this."):]

        if 'public abstract class' in line:
            nameList.append(line.split()[3].strip())
            weapon['extends'] = line.split()[3].strip()
            weapon['extendedBy'] = line.split()[5].strip()
        elif 'public class' in line:
            nameList.append(line.split()[2].strip())
            weapon['extends'] = line.split()[2].strip()
            weapon['extendedBy'] = line.split()[4].strip()
        elif 'shortRange =' in line:
            weapon['shortRange'] = line.split('=')[1].strip().rstrip(';')
        elif 'mediumRange =' in line:
            weapon['mediumRange'] = line.split('=')[1].strip().rstrip(';')
        elif 'longRange =' in line:
            weapon['longRange'] = line.split('=')[1].strip().rstrip(';')
        elif 'damage =' in line:
            weapon['damage'] = line.split('=')[1].strip().rstrip(';')
        elif 'rackSize =' in line:
            weapon['rackSize'] = line.split('=')[1].strip().rstrip(';')
        elif 'name =' in line:
            line = line.split('=')[1].strip()[1:-2]
            nameList.append(line)
            weapon['displayName'] = line
        elif 'addLookupName(' in line:
            line = (line[len("addLookupName("):-2].strip('"'))
            nameList.append(line)
        elif 'setInternalName(' in line:
            line = (line[len("setInternalName("):-2].strip('"'))
            nameList.append(line)
        elif 'setInternalName(name);' in line:
            nameList.append(weapon['displayName'])
        elif 'shortname =' in line:
            line = line.split('=')[1].strip()[1:-2]
            nameList.append(line)

    if 'shortRange' not in weapon.keys():
        for weaponType in weaponTypes_list:
            if weapon.get('extendedBy') == weaponType.get('weaponType') and not None:
                weapon['shortRange'] = weaponType.get('shortRange') or 0
                weapon['mediumRange'] = weaponType.get('mediumRange') or 0
                weapon['longRange'] = weaponType.get('longRange') or 0

    if 'damage' not in weapon.keys():
        for weaponType in weaponTypes_list:
            if weapon.get('extendedBy') == weaponType.get('weaponType') and not None:
                if weapon.get('extendedBy').startswith('LRM'):
                    weapon['damage'] = 1
                elif weapon.get('extendedBy').startswith('SRM'):
                    weapon['damage'] = 2

    if weapon.get('displayName') == 'Snub-Nose PPC':
        weapon['damage'] = "8"
    elif weapon.get('displayName') == 'Small VSP Laser':
        weapon['damage'] = "4"
    elif weapon.get('displayName') == 'Medium VSP Laser':
        weapon['damage'] = "7"
    elif weapon.get('displayName') == 'Large VSP Laser':
        weapon['damage'] = "9"
    elif weapon.get('displayName') == 'Heavy Gauss Rifle':
        weapon['damage'] = "15"
    elif weapon.get('displayName') == 'Plasma Cannon':
        weapon['damage'] = "2D6 Heat"
    elif weapon.get('displayName') == 'Anti-Missile System':
        weapon['damage'] = 0
        weapon['shortRange'] = 0
        weapon['mediumRange'] = 0
        weapon['longRange'] = 0
    elif weapon.get('displayName') == 'Magshot':
        weapon['displayName'] = "Magshot Gauss Rifle"

    for name in nameList:
        weapon['name'] = name
        weaponsList.append(weapon.copy())
        weapon['name'] = weapon.get('extends')
        weaponsList.append(weapon.copy())
        weapon['name'] = weapon.get('displayName')
        weaponsList.append(weapon.copy())

    return weaponsList


def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', str(s))
                   if unicodedata.category(c) != 'Mn')


def parse_blk(file_path, weapons_list):
    """
    Parses a BLK file and stores the data in a Python dictionary.

    Args:
        file_path (str): The path to the BLK file.
        weapons_list (list): A list of all possible weapon names.

    Returns:
        dict: A dictionary containing the parsed data.
    """

    data = {}
    current_section = None
    all_equipment = []
    armor_values = []

    clusterTable = [
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12],
        [0, 1, 1, 1, 1, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 7, 7,
            7, 8, 8, 9, 9, 9, 10, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12],
        [0, 1, 1, 2, 2, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 7, 7,
            7, 8, 8, 9, 9, 9, 10, 10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 12],
        [0, 1, 1, 2, 2, 3, 3, 4, 4, 4, 5, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 9,
            10, 10, 10, 11, 11, 11, 12, 12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 18],
        [0, 1, 2, 2, 3, 3, 4, 4, 5, 6, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 13,
            14, 15, 16, 16, 17, 17, 17, 18, 18, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 24],
        [0, 1, 2, 2, 3, 4, 4, 5, 5, 6, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 13,
            14, 15, 16, 16, 17, 17, 17, 18, 18, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 24],
        [0, 1, 2, 3, 3, 4, 4, 5, 5, 6, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 13,
            14, 15, 16, 16, 17, 17, 17, 18, 18, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 24],
        [0, 2, 2, 3, 3, 4, 4, 5, 5, 6, 7, 8, 8, 9, 9, 10, 10, 11, 11, 12, 13,
            14, 15, 16, 16, 17, 17, 17, 18, 18, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 24],
        [0, 2, 2, 3, 4, 5, 6, 6, 7, 8, 9, 10, 11, 11, 12, 13, 14, 14, 15, 16, 17,
            18, 19, 20, 21, 21, 22, 23, 23, 24, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 32],
        [0, 2, 3, 3, 4, 5, 6, 6, 7, 8, 9, 10, 11, 11, 12, 13, 14, 14, 15, 16, 17,
            18, 19, 20, 21, 21, 22, 23, 23, 24, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 32],
        [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21,
            22, 23, 24, 25, 26, 27, 28, 29, 30, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 40],
        [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
            21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 40]
    ]

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()

                if line.startswith('#'):
                    continue
                if not len(line) > 0:
                    continue

                match_start = re.match(r'<([^>]+)>', line)
                if match_start:
                    section_name = match_start.group(1)
                    if section_name.endswith("Equipment") and not (section_name.startswith('/') or section_name.startswith('Rear Equipment')):
                        current_section = section_name
                        data[current_section] = []
                    elif '/' not in section_name:
                        current_section = section_name

                match_end = re.match(r'</([^>]+)>', line)
                if match_end:
                    end_section_name = match_end.group(1)
                    if end_section_name == current_section:
                        current_section = None
                        continue

                if current_section and not ((line.startswith('<') and line.startswith('</')) or current_section.startswith('Rear Equipment') or 'Ammo' in line or 'ammo' in line):
                    if current_section.endswith("Equipment") and not current_section.startswith('Rear Equipment'):
                        if line and not line.startswith('<'):
                            line = line.split(':')[0]
                            line = line.split('(PT)')[0]
                            line = line.split('(ST)')[0]
                            line = line.split('(FL)')[0]
                            line = line.split('(FR)')[0]
                            line = line.split('(CP)')[0]
                            line = line.split('(Sqd4)')[0]
                            line = line.split('(Sqd5)')[0]
                            line = line.split('(Sqd6)')[0]
                            if current_section.startswith('Squad Equipment') or current_section.startswith('Point Equipment'):
                                if ('(Sqd2)' in data.get('Name')) or ('(Sqd 2)' in data.get('Name')) or ('(Sqd2)' in data.get('Model')) or ('(Sqd 2)' in data.get('Model')):
                                    data[current_section].append(line)
                                    all_equipment.append(line)
                                elif ('(Sqd3)' in data.get('Name')) or ('(Sqd 3)' in data.get('Name')) or ('(Sqd3)' in data.get('Model')) or ('(Sqd 3)' in data.get('Model')):
                                    data[current_section].append(line)
                                    data[current_section].append(line)
                                    all_equipment.append(line)
                                    all_equipment.append(line)
                                elif ('(Sqd4)' in data.get('Name')) or ('(Sqd 4)' in data.get('Name')) or ('(Sqd4)' in data.get('Model')) or ('(Sqd 4)' in data.get('Model')):
                                    data[current_section].append(line)
                                    data[current_section].append(line)
                                    data[current_section].append(line)
                                    all_equipment.append(line)
                                    all_equipment.append(line)
                                    all_equipment.append(line)
                                elif '(Sqd5)' in data.get('Name') or '(Sqd 5)' in data.get('Name') or '(Sqd5)' in data.get('Model') or '(Sqd 5)' in data.get('Model'):
                                    data[current_section].append(line)
                                    data[current_section].append(line)
                                    data[current_section].append(line)
                                    data[current_section].append(line)
                                    all_equipment.append(line)
                                    all_equipment.append(line)
                                    all_equipment.append(line)
                                    all_equipment.append(line)
                                elif '(Sqd6)' in data.get('Name') or '(Sqd 6)' in data.get('Name') or '(Sqd6)' in data.get('Model') or '(Sqd 6)' in data.get('Model'):
                                    data[current_section].append(line)
                                    data[current_section].append(line)
                                    data[current_section].append(line)
                                    data[current_section].append(line)
                                    data[current_section].append(line)
                                    all_equipment.append(line)
                                    all_equipment.append(line)
                                    all_equipment.append(line)
                                    all_equipment.append(line)
                                    all_equipment.append(line)
                            data[current_section].append(line)
                            all_equipment.append(line)
                    elif current_section == "armor" or current_section == "Armor":
                        values = line.split()
                        try:
                            armor_values.extend(int(val) for val in values)
                        except ValueError:
                            pass
                    else:
                        data[current_section] = line

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None

    equipment_counts = {}
    lrm_equivalent = 0

    for item in all_equipment:
        if item in equipment_counts:
            equipment_counts[item]["count"] = equipment_counts[item].get(
                'count', 0) + 1
        else:
            equipment_counts[item] = {"count": 1}

        weapon_data = next(
            (weapon for weapon in weapons_list if weapon['name'].replace('"', '').lower() == item.lower() or weapon.get('extends', '').replace('"', '').lower() == item.lower()), None)
        if weapon_data:
            equipment_counts[item]["Range"] = str(weapon_data.get('shortRange', None)) + "/" + str(
                weapon_data.get('mediumRange', None)) + "/" + str(weapon_data.get('longRange', None))
            equipment_counts[item]["DamagePerShot"] = weapon_data.get(
                'damage', None)
            equipment_counts[item]["rackSize"] = weapon_data.get(
                'rackSize', None)
            if weapon_data.get('extendedBy', '').startswith('LRM'):
                try:
                    lrm_equivalent += int(item.split()[1])
                except (ValueError, IndexError):
                    pass
        else:
            equipment_counts[item]["Range"] = None
            equipment_counts[item]["DamagePerShot"] = None
            equipment_counts[item]["rackSize"] = None

    data["Equipment"] = equipment_counts  # Store combined equipment data
    if lrm_equivalent > 0:
        data["IFNumber"] = int(lrm_equivalent / 10)
    data["Movement"] = str(data.get("cruiseMP", 0)) + \
        str(data.get("motion_type", 0))[0]
    if int(data.get("cruiseMP", 0)) > 24:
        data["TMM"] = 6
    elif int(data.get("cruiseMP", 0)) > 17:
        data["TMM"] = 5
    elif int(data.get("cruiseMP", 0)) > 9:
        data["TMM"] = 4
    elif int(data.get("cruiseMP", 0)) > 6:
        data["TMM"] = 3
    elif int(data.get("cruiseMP", 0)) > 4:
        data["TMM"] = 2
    elif int(data.get("cruiseMP", 0)) > 2:
        data["TMM"] = 1
    else:
        data["TMM"] = 0
    if str(data.get("motion_type", 0))[0] == "J":
        data["TMM"] += 1

    if not (data.get('tonnage')):
        data['tonnage'] = data.get('Tonnage')

    data["ArrowIV"] = 0
    data["LongTom"] = 0
    data["Sniper"] = 0
    data["Thumper"] = 0

    if data.get('Model') == "<Model>":
        data['Model'] = ""

    # artemis
    if "Artemis" in equipment_counts:
        data["Artemis"] = True
    else:
        data["Artemis"] = False
    # AMS
    if "Anti-Missile" in equipment_counts or "RISC Advanced Point Defense System" in equipment_counts or "ISAntiMissileSystem(ST)" in equipment_counts:
        data["AMS"] = True
    else:
        data["AMS"] = False
    # artemis
    data["ArrowIV"] = sum(equipment_counts[item]["count"] for item in equipment_counts if item in [
                          "ISArrowIVSystem", "CLArrowIVSystem"])
    # artemis

    long_tom_keywords = [
        "ISLongTom", "CLLongTom", "ISLongTomArtillery", "IS Long Tom",
        "CLLongTom", "CLLongTomArtillery", "Clan Long Tom",
        "ISLongTomCannon", "ISLongTomArtilleryCannon", "IS Long Tom Cannon",
        "CLLongTomCannon", "CLLongTomArtilleryCannon", "CL Long Tom Cannon"]
    data["LongTom"] += sum(equipment_counts.get(keyword, {}).get("count", 0)
                           for keyword in long_tom_keywords)
    long_tom_keywords = [
        "ISLongTomCannon", "ISLongTomArtilleryCannon", "IS Long Tom Cannon",
        "CLLongTomCannon", "CLLongTomArtilleryCannon", "CL Long Tom Cannon"]
    data["LongTom"] -= sum(equipment_counts.get(keyword, {}).get("count", 0)
                           for keyword in long_tom_keywords)

    sniper_keywords = [
        "ISSniper", "CLSniper", "ISSniperArtillery", "IS Sniper",
        "CLSniper", "CLSniperArtillery", "Clan Sniper",
        "ISSniperCannon", "ISSniperArtilleryCannon", "IS Sniper Cannon",
        "CLSniperCannon", "CLSniperArtilleryCannon", "CL Sniper Cannon"]
    data["Sniper"] += sum(equipment_counts.get(keyword, {}).get("count", 0)
                          for keyword in sniper_keywords)
    sniper_keywords = [
        "ISSniperCannon", "ISSniperArtilleryCannon", "IS Sniper Cannon",
        "CLSniperCannon", "CLSniperArtilleryCannon", "CL Sniper Cannon"]
    data["Sniper"] -= sum(equipment_counts.get(keyword, {}).get("count", 0)
                          for keyword in sniper_keywords)

    thumper_keywords = [
        "ISThumper", "CLThumper", "ISThumperArtillery", "IS Thumper",
        "CLThumper", "CLThumperArtillery", "Clan Thumper",
        "ISThumperCannon", "ISThumperArtilleryCannon", "IS Thumper Cannon",
        "CLThumperCannon", "CLThumperArtilleryCannon", "CL Thumper Cannon"]
    data["Thumper"] += round(sum(equipment_counts.get(keyword,
                             {}).get("count", 0) for keyword in thumper_keywords))
    thumper_keywords = [
        "ISThumperCannon", "ISThumperArtilleryCannon", "IS Thumper Cannon",
        "CLThumperCannon", "CLThumperArtilleryCannon", "CL Thumper Cannon"]
    data["Thumper"] -= round(sum(equipment_counts.get(keyword,
                             {}).get("count", 0) for keyword in thumper_keywords))
    # APC
    transporter_value = data.get("transporters", 0)
    try:
        transporter_count = - \
            (-int(float(transporter_value.split(':', 1)[-1])) // 4)
        data["APC"] = transporter_count if transporter_count > 0 else False
    except (ValueError, AttributeError):
        data["APC"] = False
    # ECM
    if any("ECM" in item for item in equipment_counts):
        data["ECM"] = "ECM6"
    else:
        data["ECM"] = False
    # HQ
    data["HQ"] = int(
        any("Communications Equipment" in item for item in equipment_counts)) > 6
    # TAG
    data["TAG"] = any("TAG" in item for item in equipment_counts)
    # TC
    data["TC"] = any("Targeting Computer" in item for item in equipment_counts)

    data['Mechanized'] = (data.get('UnitType') ==
                          'BattleArmor' or data.get('UnitType') == 'Infantry')

    data['Nimble'] = (data.get('UnitType') ==
                      'BattleArmor' or data.get('UnitType') == 'Infantry')

    data['Spotter'] = (data.get('UnitType') ==
                       'BattleArmor' or data.get('UnitType') == 'Infantry')

    data['Swarm'] = (data.get('UnitType') ==
                     'BattleArmor' or data.get('UnitType') == 'Infantry')

    data['No Turret'] = not any("Turret" in key for key in data.keys())

    # Remove equipment with None as the Range value
    data["Equipment"] = {key: value for key, value in equipment_counts.items(
    ) if value.get("Range") is not None}

    data['SpecialRules'] = ', '.join(filter(None, [
        "No Turret" if data.get("No Turret") == True else None,
        "Mechanized" if data.get("Mechanized") else None,
        "Nimble" if data.get("Nimble") else None,
        "Spotter" if data.get("Spotter") else None,
        "Swarm" if data.get("Swarm") else None,
        ("APC" + str(data.get("APC"))) if data.get("APC") else None,
        "ECM6" if data.get("ECM") else None,
        "Commander" if data.get("HQ") else None,
        "TAG9" if data.get("TAG") else None,
        ("ART-Arrow IV" + str(data.get("ArrowIV"))
         ) if data.get("ArrowIV") > 0 else None,
        ("ART-Long Tom" + str(data.get("LongTom"))
         ) if data.get("LongTom") > 0 else None,
        ("ART-Sniper" + str(data.get("Sniper"))
         ) if data.get("Sniper") > 0 else None,
        ("ART-Thumper" + str(data.get("Thumper"))
         ) if data.get("Thumper") > 0 else None,
    ]))

    csvCount = 1
    for equipment, details in equipment_counts.items():
        if details.get('Range') is None:
            continue
        else:
            weapon_data = next((weapon for weapon in weapons_list if weapon['name'].replace(
                '"', '').lower() == equipment.lower()), None)
            data[f'WepName{csvCount}'] = weapon_data.get('displayName', equipment.lstrip('IS').lstrip('Clan').lstrip(
                'Inner Sphere')) if weapon_data else equipment.lstrip('IS').lstrip('Clan').lstrip('Inner Sphere')
            # handle AMS
            if data[f'WepName{csvCount}'].startswith('Anti-Missile System'):
                del data[f'WepName{csvCount}']
                continue
            elif "AMS" in data[f'WepName{csvCount}']:
                del data[f'WepName{csvCount}']
                continue
            # handle AMS
            elif data[f'WepName{csvCount}'].startswith('RISC Advanced Point Defense System'):
                del data[f'WepName{csvCount}']
                continue
            elif "TAG" in data[f'WepName{csvCount}']:  # handle TAG
                del data[f'WepName{csvCount}']
                continue
            elif data[f'WepName{csvCount}'].startswith('C3'):  # handle c3
                del data[f'WepName{csvCount}']
                continue
            elif data[f'WepName{csvCount}'].startswith('Narc'):  # handle c3
                del data[f'WepName{csvCount}']
                continue
            elif data[f'WepName{csvCount}'].startswith('iNarc'):  # handle c3
                del data[f'WepName{csvCount}']
                continue
            elif "LRT" in data[f'WepName{csvCount}']:  # handle c3
                del data[f'WepName{csvCount}']
                continue
            elif "SRT" in data[f'WepName{csvCount}']:  # handle c3
                del data[f'WepName{csvCount}']
                continue
            elif data[f'WepName{csvCount}'].startswith('(iNarc)'):  # handle c3
                del data[f'WepName{csvCount}']
                continue
            elif "TSEMP" in data[f'WepName{csvCount}']:  # handle TSEMP
                del data[f'WepName{csvCount}']
                continue
            elif "Cruise " in data[f'WepName{csvCount}']:  # handle TSEMP
                del data[f'WepName{csvCount}']
                continue
            # handle TSEMP
            elif "Sniper Artillery" in data[f'WepName{csvCount}']:
                del data[f'WepName{csvCount}']
                continue
            # handle TSEMP
            elif "Thumper Artillery" in data[f'WepName{csvCount}']:
                del data[f'WepName{csvCount}']
                continue
            # handle TSEMP
            elif "Long Tom Artillery" in data[f'WepName{csvCount}']:
                del data[f'WepName{csvCount}']
                continue
                        # handle TSEMP
            elif "Leg Attack" in data[f'WepName{csvCount}']:
                del data[f'WepName{csvCount}']
                continue
            # handle c3
            elif data[f'WepName{csvCount}'] == 'Anti-BattleArmor Pods (B-Pods)':
                del data[f'WepName{csvCount}']
                continue
            elif data[f'WepName{csvCount}'] == 'M-Pod':
                del data[f'WepName{csvCount}']
                continue
            data[f'Shots{csvCount}'] = details.get('count')
            data[f'Dam{csvCount}'] = details.get('DamagePerShot')
            data[f'Range{csvCount}'] = details.get('Range')
            # handle SRMs
            if 'SRM' in data[f'WepName{csvCount}'] or 'SRT' in data[f'WepName{csvCount}']:
                data[f'Dam{csvCount}'] = 2
            elif 'LRM' in data[f'WepName{csvCount}'] or 'LRT' in data[f'WepName{csvCount}']:
                data[f'Dam{csvCount}'] = 1
            if data[f'WepName{csvCount}'].startswith('SRM') or data[f'WepName{csvCount}'].startswith('Streak SRM') or data[f'WepName{csvCount}'].startswith('Extended SRM') or data[f'WepName{csvCount}'].startswith('Enhanced SRM') or data[f'WepName{csvCount}'].startswith('Improved SRM'):
                data[f'Range{csvCount}'] = "3/6/9"
                if data['Artemis'] == True:
                    data[f'Shots{csvCount}'] = clusterTable[11][int(
                        details.get('rackSize'))] * details.get('count')
                    data[f'Dam{csvCount}'] = 2
                else:
                    data[f'Shots{csvCount}'] = clusterTable[7][int(
                        details.get('rackSize'))] * details.get('count')
                    data[f'Dam{csvCount}'] = 2
            # handle LRMs
            elif data[f'WepName{csvCount}'].startswith('LRM') or data[f'WepName{csvCount}'].startswith('Streak LRM') or data[f'WepName{csvCount}'].startswith('Enhanced LRM') or data[f'WepName{csvCount}'].startswith('Extended LRM') or data[f'WepName{csvCount}'].startswith('Improved LRM'):
                if data[f'WepName{csvCount}'].startswith('Extended LRM'):
                    data[f'Range{csvCount}'] = "12/22/38"
                else:
                    data[f'Range{csvCount}'] = "7/14/21"
                if data['Artemis'] == True:
                    data[f'Shots{csvCount}'] = round(
                        (clusterTable[11][int(details.get('rackSize'))] * details.get('count')) / 5)
                    data[f'Dam{csvCount}'] = 5
                else:
                    data[f'Shots{csvCount}'] = round(
                        (clusterTable[7][int(details.get('rackSize'))] * details.get('count')) / 5)
                    data[f'Dam{csvCount}'] = 5
            elif data[f'WepName{csvCount}'].startswith('MRM'):  # handle MRMs
                data[f'Range{csvCount}'] = "3/8/15"
                if data['Artemis'] == True:
                    data[f'Shots{csvCount}'] = round(
                        (clusterTable[11][int(details.get('rackSize'))] * details.get('count')) / 5)
                    data[f'Dam{csvCount}'] = 5
                else:
                    data[f'Shots{csvCount}'] = round(
                        (clusterTable[7][int(details.get('rackSize'))] * details.get('count')) / 5)
                    data[f'Dam{csvCount}'] = 5
            elif data[f'WepName{csvCount}'].startswith('MML'):  # handle MMLs
                data[f'Range{csvCount}'] = "3/14/21"
                if data['Artemis'] == True:
                    data[f'Shots{csvCount}'] = round(
                        (clusterTable[11][int(details.get('rackSize'))] * details.get('count')) / 5)
                    data[f'Dam{csvCount}'] = 5
                else:
                    data[f'Shots{csvCount}'] = round(
                        (clusterTable[7][int(details.get('rackSize'))] * details.get('count')) / 5)
                    data[f'Dam{csvCount}'] = 5
            elif data[f'WepName{csvCount}'].startswith('ATM'):  # handle ATMs
                data[f'Range{csvCount}'] = "5/10/15"
                if data['Artemis'] == True:
                    data[f'Shots{csvCount}'] = round(
                        (clusterTable[11][int(details.get('rackSize'))] * details.get('count')) * 2 / 5)
                    data[f'Dam{csvCount}'] = 5
                else:
                    data[f'Shots{csvCount}'] = round(
                        (clusterTable[9][int(details.get('rackSize'))] * details.get('count')) * 2 / 5)
                    data[f'Dam{csvCount}'] = 5
            # handle RL10
            elif data[f'WepName{csvCount}'].startswith('Rocket Launcher 10') or data[f'WepName{csvCount}'].startswith('Prototype Rocket Launcher 10'):
                data[f'Range{csvCount}'] = "5/10/15"
                data[f'Shots{csvCount}'] = round(
                    (clusterTable[7][int(details.get('rackSize'))] * details.get('count')) / 5)
                data[f'Dam{csvCount}'] = 5
            # handle RL15
            elif data[f'WepName{csvCount}'].startswith('Rocket Launcher 15') or data[f'WepName{csvCount}'].startswith('Prototype Rocket Launcher 15'):
                data[f'Range{csvCount}'] = "4/9/15"
                data[f'Shots{csvCount}'] = round(
                    (clusterTable[7][int(details.get('rackSize'))] * details.get('count')) / 5)
                data[f'Dam{csvCount}'] = 5
            # handle RL20
            elif data[f'WepName{csvCount}'].startswith('Rocket Launcher 20') or data[f'WepName{csvCount}'].startswith('Prototype Rocket Launcher 20'):
                data[f'Range{csvCount}'] = "3/7/12"
                data[f'Shots{csvCount}'] = round(
                    (clusterTable[7][int(details.get('rackSize'))] * details.get('count')) / 5)
                data[f'Dam{csvCount}'] = 5
            elif data[f'WepName{csvCount}'].startswith('HAG'):  # handle HAG
                data[f'Range{csvCount}'] = "8/16/24"
                data[f'Shots{csvCount}'] = round(
                    (clusterTable[7][int(details.get('rackSize'))] * details.get('count')) / 5)
                data[f'Dam{csvCount}'] = 1
            elif data[f'WepName{csvCount}'].startswith('Rotary AC'):
                data[f'Shots{csvCount}'] = int(details.get('count')) * 6
            elif data[f'WepName{csvCount}'].startswith('Ultra AC'):
                data[f'Shots{csvCount}'] = int(details.get('count')) * 2
            elif data[f'WepName{csvCount}'].startswith('Thunderbolt'):
                data[f'Dam{csvCount}'] = data[f'WepName{csvCount}'].split()[1]
                data[f'Range{csvCount}'] = "6/12/18"
            elif data[f'WepName{csvCount}'].startswith('LB '):
                acName = data[f'WepName{csvCount}']
                # Slug LBX
                data[f'WepName{csvCount}'] = acName + " (Slug)"
                data[f'Shots{csvCount}'] = details.get('count')
                data[f'Dam{csvCount}'] = details.get('DamagePerShot')
                data[f'Range{csvCount}'] = details.get('Range')
                # Pellet LBX
                csvCount += 1
                data[f'WepName{csvCount}'] = "-- OR --"
                csvCount += 1
                data[f'WepName{csvCount}'] = acName + " (Pellet)"
                data[f'Shots{csvCount}'] = int(details.get(
                    'count')) * int(details.get('DamagePerShot'))
                data[f'Dam{csvCount}'] = 1
                data[f'Range{csvCount}'] = details.get('Range')
                #BA LBX
            elif data[f'WepName{csvCount}'].startswith('Battle Armor LB-X'):
                details['DamagePerShot'] = 1
                data[f'Shots{csvCount}'] = int(details.get(
                    'count')) * int(details.get('DamagePerShot'))
                data[f'Dam{csvCount}'] = 1
                data[f'Range{csvCount}'] = details.get('Range')
            elif data[f'WepName{csvCount}'].startswith('Tube Artillery (BA)'):
                data[f'Dam{csvCount}'] = 1
                data[f'Range{csvCount}'] = details.get('Range')
            elif data[f'WepName{csvCount}'] == ("Thumper Cannon"):
                data[f'WepName{csvCount}'] = "Thumper Cannon"
                data[f'Dam{csvCount}'] = 5
                data[f'Range{csvCount}'] = "4/9/14"
            elif data[f'WepName{csvCount}'] == ("Sniper Cannon"):
                data[f'WepName{csvCount}'] = "Sniper Cannon"
                data[f'Dam{csvCount}'] = 10
                data[f'Range{csvCount}'] = "4/8/12"
            elif data[f'WepName{csvCount}'] == ("Long Tom Cannon"):
                data[f'WepName{csvCount}'] = "Long Tom Cannon"
                data[f'Dam{csvCount}'] = 20
                data[f'Range{csvCount}'] = "6/13/20"
            elif data[f'WepName{csvCount}'] == ("Arrow IV"):
                data[f'Dam{csvCount}'] = 20
            elif data[f'WepName{csvCount}'] == ("Silver Bullet Gauss Rifle"):
                data[f'Shots{csvCount}'] = (
                    clusterTable[7][15] * details.get('count'))
                data[f'Dam{csvCount}'] = 1
            elif data[f'WepName{csvCount}'] == ("'Mech Mortar 2"):
                data[f'Dam{csvCount}'] = 20
            csvCount += 1

    data['RegSkill'] = 6
    data['VetSkill'] = 5
    if data.get('type', '').startswith('Clan'):
        data['RegSkill'] -= 1
        data['VetSkill'] -= 1
    if data.get('TC', '') == True:
        data['RegSkill'] -= 1
        data['VetSkill'] -= 1

    for csvCount in range(1, 8):
        if data.get(f'Shots{csvCount}') and data.get(f'Dam{csvCount}'):
            data[f'CombDam{csvCount}'] = str(
                data.get(f'Shots{csvCount}')) + "x" + str(data.get(f'Dam{csvCount}'))

    if data.get('SpecialRules') != "":
        data[f'SpecialRules'] = "Special: " + str(data.get('SpecialRules'))

    if data.get('TMM') > 0:
        data['TMM'] = "+" + str(data.get('TMM'))

    data['FullName'] = data.get('Name', "") + " " + data.get('Model', "")
    data['Armor'] = round(float(sum(armor_values)) / 30.0)
    data['ArmorIcons'] = 'A' * int(data.get('Armor', 0))
    if data['UnitType'] == 'BattleArmor' or data['UnitType'] == 'Infantry':
        data['Structure'] = 1
    else:
        data['Structure'] = math.ceil(
            ((len(armor_values) * int(round(float(data.get('tonnage', 0))))) / 10 / 10))
    data['StructureIcons'] = 'S' * int(data.get('Structure', 0))
    
    if data.get('FullName') == 'Black Wolf Battle Armor [Heavy Mortar](Sqd4)':
        breakpoint()
        
    if data.get('Trooper Count'):
        trooperCount = int(data.get('Trooper Count'))
    else: trooperCount = 0


    if not ((data['motion_type'] == 'Submarine') or
            (data['motion_type'] == 'Naval') or
            (data['motion_type'] == 'WiGE') or
            (data['Structure'] == 0) or
            ((data['UnitType'] == 'BattleArmor') & (not trooperCount == 6) & ('WoB' in data.get('FullName'))) or
            ((data['UnitType'] == 'BattleArmor') & ("IS" in data['type']) & (not trooperCount == 4) & (not '(WoB)' in data.get('FullName'))) or
            ((data['UnitType'] == 'BattleArmor') & ("Clan" in data['type']) & (not trooperCount == 5) & (not '(WoB)' in data.get('FullName')))):
        print(data.get('FullName'))
        return data


def main():
    fileroot = 'D:\\Games\\Downloads\\mekhq-windows-0.49.19.1\\MMSource\\megamek-master'
    weaponTypes_list = []  # Initialize an empty list to store weaponType dictionaries
    asset_List = []
    weapons_list = []  # Initialize an empty list to store weapon dictionaries
    os.chdir(fileroot+'\\megamek\\src\\megamek\\common\\weapons')
    for root, dirs, files in os.walk(os.getcwd()):
        for filename in files:
            if filename.endswith("Weapon.java"):
                weaponType_data = parse_weaponType_data(
                    os.path.join(root, filename))
                if weaponType_data:  # Check if the returned dictionary is not empty
                    weaponTypes_list.append(weaponType_data)
    # pprint.pp(weaponTypes_list)
    for root, dirs, files in os.walk(os.getcwd()):
        for filename in files:
            # skip handler files
            if filename.endswith(".java") and not filename.endswith("Handler.java") and not filename.endswith("Weapon.java") and not filename.endswith("Helper.java"):
                weapon_data = parse_weapon_data(
                    os.path.join(root, filename), weaponTypes_list)
                if weapon_data:  # Check if the returned dictionary is not empty
                    for weapon in weapon_data:
                        weapons_list.append(weapon)
    weaponDx_file_path = os.path.join(fileroot, 'Python', 'weaponDx.txt')
    with open(weaponDx_file_path, mode='w', encoding='utf-8') as weaponDx_file:
        # Write the list of weapon dictionaries to the file.
        pprint.pprint(weapons_list, stream=weaponDx_file)
    # os.chdir(fileroot+'\\megamek\\data\\mekfiles\\vehicles\\')
    # root = os.getcwd()
    # for root, dirs, files in os.walk(os.getcwd()):
    #     for filename in files:
    #         if filename.endswith(".blk"):
    #             asset = parse_blk(
    #                 os.path.join(root, filename), weapons_list)
    #         if asset:  # Check if the returned dictionary is not empty
    #             asset_List.append(asset)
    os.chdir(fileroot+'\\megamek\\data\\mekfiles\\battlearmor\\')
    root = os.getcwd()
    for root, dirs, files in os.walk(os.getcwd()):
        for filename in files:
            if filename.endswith(".blk"):
                asset = parse_blk(
                    os.path.join(root, filename), weapons_list)
            if asset:  # Check if the returned dictionary is not empty
                asset_List.append(asset)
    # os.chdir(fileroot+'\\megamek\\data\\mekfiles\\infantry\\')
    # root = os.getcwd()
    # for root, dirs, files in os.walk(os.getcwd()):
    #     for filename in files:
    #         if filename.endswith(".blk"):
    #             asset = parse_blk(
    #                 os.path.join(root, filename), weapons_list)
    #         if asset:  # Check if the returned dictionary is not empty
    #             asset_List.append(asset)
    os.chdir(fileroot+'\\megamek\\data\\mekfiles\\protomeks\\')
    root = os.getcwd()
    for root, dirs, files in os.walk(os.getcwd()):
        for filename in files:
            if filename.endswith(".blk"):
                asset = parse_blk(
                    os.path.join(root, filename), weapons_list)
            if asset:  # Check if the returned dictionary is not empty
                asset_List.append(asset)
    # pprint.pp(asset_List)  # print the list of asset dictionaries.
    max_weapon_count = 0
    os.chdir(fileroot+'\\Python\\')
    csv_file_path = os.path.join(os.getcwd(), 'parsed_data_InfBAProto.csv')
    print("Done Parsing files, writing to CSV...")

    with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        # Write the header row
        csv_writer.writerow(['Common', 'unitType', 'FullName', 'Armor', 'ArmorIcons', 'Structure', 'StructureIcons', 'Movement', 'TMM', 'BasePV', 'RegPV', 'VetPV', 'RegSkill', 'VetSkill', 'SpecialRules', 'name', 'model', 'WepName1', 'Shots1', 'Dam1',
                            'Range1', 'WepName2', 'Shots2', 'Dam2', 'Range2', 'WepName3', 'Shots3', 'Dam3', 'Range3', 'WepName4', 'Shots4', 'Dam4', 'Range4', 'WepName5', 'Shots5', 'Dam5', 'Range5', 'WepName6', 'Shots6', 'Dam6', 'Range6', 'WepName7', 'Shots7', 'Dam7', 'Range7',
                             'CombDam1', 'CombDam2', 'CombDam3', 'CombDam4', 'CombDam5', 'CombDam6', 'CombDam7'])

        for asset in asset_List:
            # Write each asset's data to the CSV
            equipment_list = list(asset.get('Equipment', {}).items())[
                :7]  # Get the first 7 equipment entries
            csv_writer.writerow([
                0,
                asset.get('UnitType'),
                strip_accents(asset.get('FullName')),
                asset.get('Armor'),
                asset.get('ArmorIcons'),
                asset.get('Structure'),
                asset.get('StructureIcons'),
                asset.get('Movement'),
                asset.get('TMM'),
                asset.get('BasePV', 0),
                asset.get('RegPV', 0),
                asset.get('VetPV', 0),
                asset.get('RegSkill', 0),
                asset.get('VetSkill', 0),
                asset.get('SpecialRules'),
                strip_accents(asset.get('Name')),
                strip_accents(asset.get('Model')),
                asset.get('WepName1'),
                asset.get('Shots1'),
                asset.get('Dam1'),
                asset.get('Range1'),
                asset.get('WepName2'),
                asset.get('Shots2'),
                asset.get('Dam2'),
                asset.get('Range2'),
                asset.get('WepName3'),
                asset.get('Shots3'),
                asset.get('Dam3'),
                asset.get('Range3'),
                asset.get('WepName4'),
                asset.get('Shots4'),
                asset.get('Dam4'),
                asset.get('Range4'),
                asset.get('WepName5'),
                asset.get('Shots5'),
                asset.get('Dam5'),
                asset.get('Range5'),
                asset.get('WepName6'),
                asset.get('Shots6'),
                asset.get('Dam6'),
                asset.get('Range6'),
                asset.get('WepName7'),
                asset.get('Shots7'),
                asset.get('Dam7'),
                asset.get('Range7'),
                asset.get('CombDam1'),
                asset.get('CombDam2'),
                asset.get('CombDam3'),
                asset.get('CombDam4'),
                asset.get('CombDam5'),
                asset.get('CombDam6'),
                asset.get('CombDam7')
            ])
    print("Done!")


if __name__ == "__main__":
    main()
