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
        if 'public abstract class' in line.lower():
            weaponType['weaponType'] = line.split()[3].strip()
        elif 'public class' in line.lower():
            weaponType['weaponType'] = line.split()[2].strip()
        elif 'shortrange =' in line.lower():
            weaponType['shortrange'] = line.split('=')[1].strip().rstrip(';')
        elif 'mediumrange =' in line.lower():
            weaponType['mediumrange'] = line.split('=')[1].strip().rstrip(';')
        elif 'longrange =' in line.lower():
            weaponType['longrange'] = line.split('=')[1].strip().rstrip(';')
    return weaponType


def parse_weapon_data(file_path, weaponTypes_list):  # Parses things like ISLRM20.java
    """
    Parses weapon range and weapon type data from a Java-like class definition and returns a dictionary.

    Args:
        file_path (str): The path to the file containing the weapon data.
        weaponTypes_list (list): A list of weapon type dictionaries.

    Returns:
        dict: A dictionary containing the weapon attributes.
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
        return {}  # Return an empty dictionary if file not found

    lines = weapon_text.split('\n')

    for line in lines:
        line = line.strip()
        if line.lower().startswith("this."):
            line = line[len("this."):]

        if "helper" in line.lower():
            continue
        elif 'public abstract class' in line.lower():
            nameList.append(line.split()[3].strip())
            weapon['extends'] = line.split()[3].strip()
            weapon['extendedBy'] = line.split()[5].strip()
        elif 'public class' in line.lower():
            nameList.append(line.split()[2].strip())
            weapon['extends'] = line.split()[2].strip()
            weapon['extendedBy'] = line.split()[4].strip()
        elif 'shortrange =' in line.lower():
            weapon['shortrange'] = line.split('=')[1].strip().rstrip(';')
        elif 'mediumrange =' in line.lower():
            weapon['mediumrange'] = line.split('=')[1].strip().rstrip(';')
        elif 'longrange =' in line.lower():
            weapon['longrange'] = line.split('=')[1].strip().rstrip(';')
        elif 'damage =' in line.lower():
            weapon['damage'] = line.split('=')[1].strip().rstrip(';')
        elif 'rackSize =' in line.lower():
            weapon['rackSize'] = line.split('=')[1].strip().rstrip(';')
        elif 'name =' in line.lower():
            line = line.split('=')[1].strip()[1:-2]
            nameList.append(line)
            weapon['displayName'] = line
        elif 'addLookupName(' in line.lower():
            line = (line[len("addLookupName("):-2].strip('"'))
            nameList.append(line)
        elif 'setInternalName(' in line.lower():
            line = (line[len("setInternalName("):-2].strip('"'))
            nameList.append(line)
        elif 'setInternalName(name);' in line.lower():
            nameList.append(weapon['displayName'])
        elif 'shortname =' in line.lower():
            line = line.split('=')[1].strip()[1:-2]
            nameList.append(line)

    if 'shortrange' not in weapon.keys():
        for weaponType in weaponTypes_list:
            if weapon.get('extendedBy', '').lower() == weaponType.get('weaponType', '').lower() and weapon.get('extendedBy') is not None:
                weapon['shortrange'] = weaponType.get('shortrange') or 0
                weapon['mediumrange'] = weaponType.get('mediumrange') or 0
                weapon['longrange'] = weaponType.get('longrange') or 0

    if 'damage' not in weapon.keys():
        for weaponType in weaponTypes_list:
            if weapon.get('extendedBy', '').lower() == weaponType.get('weaponType', '').lower() and weapon.get('extendedBy') is not None:
                if weapon.get('extendedBy', '').lower().startswith('lrm'):
                    weapon['damage'] = 1
                elif weapon.get('extendedBy', '').lower().startswith('srm'):
                    weapon['damage'] = 2

    if weapon.get('displayName', '').lower() == 'snub-nose ppc':
        weapon['damage'] = "8"
    elif weapon.get('displayName', '').lower() == 'small vsp laser':
        weapon['damage'] = "4"
    elif weapon.get('displayName', '').lower() == 'medium vsp laser':
        weapon['damage'] = "7"
    elif weapon.get('displayName', '').lower() == 'large vsp laser':
        weapon['damage'] = "9"
    elif weapon.get('displayName', '').lower() == 'heavy gauss rifle':
        weapon['damage'] = "15"
    elif weapon.get('displayName', '').lower() == 'plasma cannon':
        weapon['damage'] = "2D6 Heat"
    elif weapon.get('displayName', '').lower() == 'anti-missile system':
        weapon['damage'] = 0
        weapon['shortrange'] = 0
        weapon['mediumrange'] = 0
        weapon['longrange'] = 0
    elif weapon.get('displayName', '').lower() == 'magshot':
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
        weapons_list (list): A list of all possible weapon names (dictionaries from parse_weapon_data).

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
                    if section_name.lower().endswith("equipment") and not (section_name.lower().startswith('/') or section_name.lower().startswith('rear equipment')):
                        current_section = section_name
                        data[current_section] = []
                    elif '/' not in section_name:
                        current_section = section_name

                match_end = re.match(r'</([^>]+)>', line)
                if match_end:
                    end_section_name = match_end.group(1)
                    if end_section_name.lower() == current_section.lower():
                        current_section = None
                        continue

                if current_section and not ((line.startswith('<') and line.startswith('</')) or current_section.lower().startswith('rear equipment') or 'Ammo' in line or 'ammo' in line):
                    if current_section.lower().endswith("equipment") and not current_section.lower().startswith('rear equipment'):
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
                            if current_section.lower().startswith('squad equipment') or current_section.lower().startswith('point equipment'):
                                if ('(Sqd2)' in data.get('Name', '')) or ('(Sqd 2)' in data.get('Name', '')) or ('(Sqd2)' in data.get('model', '')) or ('(Sqd 2)' in data.get('model', '')):
                                    data[current_section].append(line)
                                    all_equipment.append(line)
                                elif ('(Sqd3)' in data.get('Name', '')) or ('(Sqd 3)' in data.get('Name', '')) or ('(Sqd3)' in data.get('model', '')) or ('(Sqd 3)' in data.get('model', '')):
                                    data[current_section].append(line)
                                    data[current_section].append(line)
                                    all_equipment.append(line)
                                    all_equipment.append(line)
                                elif ('(Sqd4)' in data.get('Name', '')) or ('(Sqd 4)' in data.get('Name', '')) or ('(Sqd4)' in data.get('model', '')) or ('(Sqd 4)' in data.get('model', '')):
                                    data[current_section].append(line)
                                    data[current_section].append(line)
                                    data[current_section].append(line)
                                    all_equipment.append(line)
                                    all_equipment.append(line)
                                    all_equipment.append(line)
                                elif '(Sqd5)' in data.get('Name', '') or '(Sqd 5)' in data.get('Name', '') or '(Sqd5)' in data.get('model', '') or '(Sqd 5)' in data.get('model', ''):
                                    data[current_section].append(line)
                                    data[current_section].append(line)
                                    data[current_section].append(line)
                                    data[current_section].append(line)
                                    all_equipment.append(line)
                                    all_equipment.append(line)
                                    all_equipment.append(line)
                                    all_equipment.append(line)
                                elif '(Sqd6)' in data.get('Name', '') or '(Sqd 6)' in data.get('Name', '') or '(Sqd6)' in data.get('model', '') or '(Sqd 6)' in data.get('model', ''):
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
                    elif current_section.lower() == "armor" or current_section.lower() == "armor":
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
        item_lower = item.lower()
        if item_lower in (key.lower() for key in equipment_counts):
            for key in list(equipment_counts.keys()):
                if key.lower() == item_lower:
                    equipment_counts[key]["count"] = equipment_counts[key].get(
                        'count', 0) + 1
                    break
        else:
            equipment_counts[item] = {"count": 1}

        weapon_data = next(
            (weapon for weapon in weapons_list if weapon['name'].replace('"', '').lower() == item_lower or weapon.get('extends', '').replace('"', '').lower() == item_lower), None)
        if weapon_data:
            equipment_counts[item]["range"] = str(weapon_data.get('shortrange', None)) + "/" + str(
                weapon_data.get('mediumrange', None)) + "/" + str(weapon_data.get('longrange', None))
            equipment_counts[item]["damagePerShot"] = weapon_data.get(
                'damage', None)
            equipment_counts[item]["rackSize"] = weapon_data.get(
                'rackSize', None)
            if weapon_data.get('extendedBy', '').lower().startswith('lrm'):
                try:
                    lrm_equivalent += int(item.split()[1])
                except (ValueError, IndexError):
                    pass
        else:
            equipment_counts[item]["range"] = None
            equipment_counts[item]["damagePerShot"] = None
            equipment_counts[item]["rackSize"] = None

    data["equipment"] = equipment_counts  # Store combined equipment data
    if lrm_equivalent > 0:
        data["ifnumber"] = int(lrm_equivalent / 10)
    data["movement"] = str(data.get("cruiseMP", 0)) + \
        str(data.get("motion_type", 0))[0]
    if int(data.get("cruiseMP", 0)) > 24:
        data["tmm"] = 6
    elif int(data.get("cruiseMP", 0)) > 17:
        data["tmm"] = 5
    elif int(data.get("cruiseMP", 0)) > 9:
        data["tmm"] = 4
    elif int(data.get("cruiseMP", 0)) > 6:
        data["tmm"] = 3
    elif int(data.get("cruiseMP", 0)) > 4:
        data["tmm"] = 2
    elif int(data.get("cruiseMP", 0)) > 2:
        data["tmm"] = 1
    else:
        data["tmm"] = 0
    if str(data.get("motion_type", 0))[0].upper() == "J":
        data["tmm"] += 1

    if not (data.get('tonnage')):
        data['tonnage'] = data.get('tonnage')

    data["arrowiv"] = 0
    data["longtom"] = 0
    data["sniper"] = 0
    data["thumper"] = 0

    if data.get('model', '').lower() == "<model>":
        data['model'] = ""

    # artemis
    if any("artemis" in item.lower() for item in equipment_counts):
        data["artemis"] = True
    else:
        data["artemis"] = False
    # AMS
    if any("anti-missile" in item.lower() for item in equipment_counts) or any("risc advanced point defense system" in item.lower() for item in equipment_counts) or any("isantissileSystem(st)" in item.lower() for item in equipment_counts):
        data["AMS"] = True
    else:
        data["AMS"] = False
    # artemis
    data["arrowiv"] = sum(equipment_counts[item]["count"] for item in equipment_counts if item.lower() in [
        "isarrowivsystem", "clarrowivsystem"])
    # artemis

    long_tom_keywords = [
        "islongtom", "cllongtom", "islongtomartillery", "is long tom",
        "cllongtom", "cllongtomartillery", "clan long tom",
        "islongtomcannon", "islongtomartillerycannon", "is long tom cannon",
        "cllongtomcannon", "cllongtomartillerycannon", "cl long tom cannon"]
    data["longtom"] += sum(equipment_counts.get(keyword, {}).get("count", 0)
                           for keyword in long_tom_keywords)
    long_tom_keywords = [
        "islongtomcannon", "islongtomartillerycannon", "is long tom cannon",
        "cllongtomcannon", "cllongtomartillerycannon", "cl long tom cannon"]
    data["longtom"] -= sum(equipment_counts.get(keyword, {}).get("count", 0)
                           for keyword in long_tom_keywords)

    sniper_keywords = [
        "issniper", "clsniper", "issniperartillery", "is sniper",
        "clsniper", "clsniperartillery", "clan sniper",
        "issnipercannon", "issniperartillerycannon", "is sniper cannon",
        "clsnipercannon", "clsniperartillerycannon", "cl sniper cannon"]
    data["sniper"] += sum(equipment_counts.get(keyword, {}).get("count", 0)
                          for keyword in sniper_keywords)
    sniper_keywords = [
        "issnipercannon", "issniperartillerycannon", "is sniper cannon",
        "clsnipercannon", "clsniperartillerycannon", "cl sniper cannon"]
    data["sniper"] -= sum(equipment_counts.get(keyword, {}).get("count", 0)
                          for keyword in sniper_keywords)

    thumper_keywords = [
        "isthumper", "clthumper", "isthumperartillery", "is thumper",
        "clthumper", "clthumperartillery", "clan thumper",
        "isthumpercannon", "isthumperartillerycannon", "is thumper cannon",
        "clthumpercannon", "clthumperartillerycannon", "cl thumper cannon"]
    data["thumper"] += round(sum(equipment_counts.get(keyword,
                                                      {}).get("count", 0) for keyword in thumper_keywords))
    thumper_keywords = [
        "isthumpercannon", "isthumperartillerycannon", "is thumper cannon",
        "clthumpercannon", "clthumperartillerycannon", "cl thumper cannon"]
    data["thumper"] -= round(sum(equipment_counts.get(keyword,
                                                      {}).get("count", 0) for keyword in thumper_keywords))
    # apc
    transporter_value = data.get("transporters", 0)
    try:
        transporter_count = - \
            (-int(float(transporter_value.split(':', 1)[-1])) // 4)
        data["apc"] = transporter_count if transporter_count > 0 else False
    except (ValueError, AttributeError):
        data["apc"] = False
    # ecm
    if any("ecm" in item.lower() for item in equipment_counts):
        data["ecm"] = "ecm6"
    else:
        data["ecm"] = False
    # hq
    data["hq"] = int(
        any("communications equipment" in item.lower() for item in equipment_counts)) > 6
    # tag
    data["tag"] = any("tag" in item.lower() for item in equipment_counts)
    # tc
    data["tc"] = any("targeting computer" in item.lower()
                     for item in equipment_counts)

    data['mechanized'] = (data.get('unittype', '').lower() ==
                          'battlearmor' or data.get('unittype', '').lower() == 'infantry')

    data['nimble'] = (data.get('unittype', '').lower() ==
                      'battlearmor' or data.get('unittype', '').lower() == 'infantry')

    data['spotter'] = (data.get('unittype', '').lower() ==
                       'battlearmor' or data.get('unittype', '').lower() == 'infantry')

    data['swarm'] = (data.get('unittype', '').lower() ==
                     'battlearmor' or data.get('unittype', '').lower() == 'infantry')

    data['no turret'] = not any("turret" in key.lower() for key in data.keys())

    # Remove equipment with None as the range value
    data["equipment"] = {key: value for key, value in equipment_counts.items()
                         if value.get("range") is not None}

    data['specialrules'] = ', '.join(filter(None, [
        "no turret" if data.get("no turret") == True else None,
        "mechanized" if data.get("mechanized") else None,
        "nimble" if data.get("nimble") else None,
        "spotter" if data.get("spotter") else None,
        "swarm" if data.get("swarm") else None,
        ("apc" + str(data.get("apc"))) if data.get("apc") else None,
        "ecm6" if data.get("ecm") else None,
        "Commander" if data.get("hq") else None,
        "tag9" if data.get("tag") else None,
        ("ART-Arrow IV" + str(data.get("arrowiv"))
         ) if data.get("arrowiv") > 0 else None,
        ("ART-Long Tom" + str(data.get("longtom"))
         ) if data.get("longtom") > 0 else None,
        ("ART-sniper" + str(data.get("sniper"))
         ) if data.get("sniper") > 0 else None,
        ("ART-thumper" + str(data.get("thumper"))
         ) if data.get("thumper") > 0 else None,
    ]))

    csvCount = 1
    for equipment, details in equipment_counts.items():
        if details.get('range') is None:
            continue
        else:
            weapon_data = next((weapon for weapon in weapons_list if weapon['name'].replace(
                '"', '').lower() == equipment.lower()), None)
            data[f'wepname{csvCount}'] = weapon_data.get('displayName', equipment.lstrip('IS').lstrip('Clan').lstrip(
                'Inner Sphere')) if weapon_data else equipment.lstrip('IS').lstrip('Clan').lstrip('Inner Sphere')
            # handle AMS
            if data[f'wepname{csvCount}'].lower().startswith('anti-missile system'):
                del data[f'wepname{csvCount}']
                continue
            elif "ams" in data[f'wepname{csvCount}'].lower():
                del data[f'wepname{csvCount}']
                continue
            # handle AMS
            elif data[f'wepname{csvCount}'].lower().startswith('risc advanced point defense system'):
                del data[f'wepname{csvCount}']
                continue
            elif "tag" in data[f'wepname{csvCount}'].lower():  # handle tag
                del data[f'wepname{csvCount}']
                continue
            elif data[f'wepname{csvCount}'].lower().startswith('c3'):  # handle c3
                del data[f'wepname{csvCount}']
                continue
            elif data[f'wepname{csvCount}'].lower().startswith('narc'):  # handle narc
                del data[f'wepname{csvCount}']
                continue
            elif data[f'wepname{csvCount}'].lower().startswith('inarc'):  # handle inarc
                del data[f'wepname{csvCount}']
                continue
            elif "lrt" in data[f'wepname{csvCount}'].lower():  # handle lrt
                del data[f'wepname{csvCount}']
                continue
            elif "srt" in data[f'wepname{csvCount}'].lower():  # handle srt
                del data[f'wepname{csvCount}']
                continue
            elif data[f'wepname{csvCount}'].lower().startswith('(inarc)'):  # handle (inarc)
                del data[f'wepname{csvCount}']
                continue
            elif "tsemp" in data[f'wepname{csvCount}'].lower():  # handle TSEMP
                del data[f'wepname{csvCount}']
                continue
            # handle Cruise Missiles
            elif "cruise " in data[f'wepname{csvCount}'].lower():
                del data[f'wepname{csvCount}']
                continue
            # handle TSEMP
            elif "sniper artillery" in data[f'wepname{csvCount}'].lower():
                del data[f'wepname{csvCount}']
                continue
            # handle TSEMP
            elif "thumper artillery" in data[f'wepname{csvCount}'].lower():
                del data[f'wepname{csvCount}']
                continue
            # handle TSEMP
            elif "long tom artillery" in data[f'wepname{csvCount}'].lower():
                del data[f'wepname{csvCount}']
                continue
            # handle TSEMP
            elif "leg attack" in data[f'wepname{csvCount}'].lower():
                del data[f'wepname{csvCount}']
                continue
            # handle c3
            elif data[f'wepname{csvCount}'].lower() == 'anti-battlearmor pods (b-pods)':
                del data[f'wepname{csvCount}']
                continue
            elif data[f'wepname{csvCount}'].lower() == 'm-pod':
                del data[f'wepname{csvCount}']
                continue
            data[f'shots{csvCount}'] = details.get('count')
            data[f'dam{csvCount}'] = details.get('damagePerShot')
            data[f'range{csvCount}'] = details.get('range')
            # handle SRMs
            if 'srm' in data[f'wepname{csvCount}'].lower() or 'srt' in data[f'wepname{csvCount}'].lower():
                data[f'dam{csvCount}'] = 2
            elif 'lrm' in data[f'wepname{csvCount}'].lower() or 'lrt' in data[f'wepname{csvCount}'].lower():
                data[f'dam{csvCount}'] = 1
            if data[f'wepname{csvCount}'].lower().startswith('srm') or data[f'wepname{csvCount}'].lower().startswith('streak srm') or data[f'wepname{csvCount}'].lower().startswith('extended srm') or data[f'wepname{csvCount}'].lower().startswith('enhanced srm') or data[f'wepname{csvCount}'].lower().startswith('improved srm'):
                data[f'range{csvCount}'] = "3/6/9"
                if data['artemis'] == True:
                    data[f'shots{csvCount}'] = clusterTable[11][int(
                        details.get('rackSize'))] * details.get('count')
                    data[f'dam{csvCount}'] = 2
                else:
                    data[f'shots{csvCount}'] = clusterTable[7][int(
                        details.get('rackSize'))] * details.get('count')
                    data[f'dam{csvCount}'] = 2
            # handle LRMs
            elif data[f'wepname{csvCount}'].lower().startswith('lrm') or data[f'wepname{csvCount}'].lower().startswith('streak lrm') or data[f'wepname{csvCount}'].lower().startswith('enhanced lrm') or data[f'wepname{csvCount}'].lower().startswith('extended lrm') or data[f'wepname{csvCount}'].lower().startswith('improved lrm'):
                if data[f'wepname{csvCount}'].lower().startswith('extended lrm'):
                    data[f'range{csvCount}'] = "12/22/38"
                else:
                    data[f'range{csvCount}'] = "7/14/21"
                if data['artemis'] == True:
                    data[f'shots{csvCount}'] = round(
                        (clusterTable[11][int(details.get('rackSize'))] * details.get('count')) / 5)
                    data[f'dam{csvCount}'] = 5
                else:
                    data[f'shots{csvCount}'] = round(
                        (clusterTable[7][int(details.get('rackSize'))] * details.get('count')) / 5)
                    data[f'dam{csvCount}'] = 5
            elif data[f'wepname{csvCount}'].lower().startswith('mrm'):  # handle MRMs
                data[f'range{csvCount}'] = "3/8/15"
                if data['artemis'] == True:
                    data[f'shots{csvCount}'] = round(
                        (clusterTable[11][int(details.get('rackSize'))] * details.get('count')) / 5)
                    data[f'dam{csvCount}'] = 5
                else:
                    data[f'shots{csvCount}'] = round(
                        (clusterTable[7][int(details.get('rackSize'))] * details.get('count')) / 5)
                    data[f'dam{csvCount}'] = 5
            elif data[f'wepname{csvCount}'].lower().startswith('mml'):  # handle MMLs
                data[f'range{csvCount}'] = "3/14/21"
                if data['artemis'] == True:
                    data[f'shots{csvCount}'] = round(
                        (clusterTable[11][int(details.get('rackSize'))] * details.get('count')) / 5)
                    data[f'dam{csvCount}'] = 5
                else:
                    data[f'shots{csvCount}'] = round(
                        (clusterTable[7][int(details.get('rackSize'))] * details.get('count')) / 5)
                    data[f'dam{csvCount}'] = 5
            elif data[f'wepname{csvCount}'].lower().startswith('atm'):  # handle ATMs
                data[f'range{csvCount}'] = "5/10/15"
                if data['artemis'] == True:
                    data[f'shots{csvCount}'] = round(
                        (clusterTable[11][int(details.get('rackSize'))] * details.get('count')) * 2 / 5)
                    data[f'dam{csvCount}'] = 5
                else:
                    data[f'shots{csvCount}'] = round(
                        (clusterTable[9][int(details.get('rackSize'))] * details.get('count')) * 2 / 5)
                    data[f'dam{csvCount}'] = 5
            # handle RL10
            elif data[f'wepname{csvCount}'].lower().startswith('rocket launcher 10') or data[f'wepname{csvCount}'].lower().startswith('prototype rocket launcher 10'):
                data[f'range{csvCount}'] = "5/10/15"
                data[f'shots{csvCount}'] = round(
                    (clusterTable[7][int(details.get('rackSize'))] * details.get('count')) / 5)
                data[f'dam{csvCount}'] = 5
            # handle RL15
            elif data[f'wepname{csvCount}'].lower().startswith('rocket launcher 15') or data[f'wepname{csvCount}'].lower().startswith('prototype rocket launcher 15'):
                data[f'range{csvCount}'] = "4/9/15"
                data[f'shots{csvCount}'] = round(
                    (clusterTable[7][int(details.get('rackSize'))] * details.get('count')) / 5)
                data[f'dam{csvCount}'] = 5
# handle RL20
            elif data[f'wepname{csvCount}'].lower().startswith('rocket launcher 20') or data[f'wepname{csvCount}'].lower().startswith('prototype rocket launcher 20'):
                data[f'range{csvCount}'] = "3/7/12"
                data[f'shots{csvCount}'] = round(
                    (clusterTable[7][int(details.get('rackSize'))] * details.get('count')) / 5)
                data[f'dam{csvCount}'] = 5
            elif data[f'wepname{csvCount}'].lower().startswith('hag'):  # handle HAG
                data[f'range{csvCount}'] = "8/16/24"
                data[f'shots{csvCount}'] = round(
                    (clusterTable[7][int(details.get('rackSize'))] * details.get('count')) / 5)
                data[f'dam{csvCount}'] = 1
            elif data[f'wepname{csvCount}'].lower().startswith('rotary ac'):
                data[f'shots{csvCount}'] = int(details.get('count')) * 6
            elif data[f'wepname{csvCount}'].lower().startswith('ultra ac'):
                data[f'shots{csvCount}'] = int(details.get('count')) * 2
            elif data[f'wepname{csvCount}'].lower().startswith('thunderbolt'):
                data[f'dam{csvCount}'] = data[f'wepname{csvCount}'].split()[1]
                data[f'range{csvCount}'] = "6/12/18"
            elif data[f'wepname{csvCount}'].lower().startswith('lb '):
                acName = data[f'wepname{csvCount}']
                # Slug LBX
                data[f'wepname{csvCount}'] = acName + " (slug)"
                data[f'shots{csvCount}'] = details.get('count')
                data[f'dam{csvCount}'] = details.get('damagePerShot')
                data[f'range{csvCount}'] = details.get('range')
                # Pellet LBX
                csvCount += 1
                data[f'wepname{csvCount}'] = "-- OR --"
                csvCount += 1
                data[f'wepname{csvCount}'] = acName + " (pellet)"
                data[f'shots{csvCount}'] = int(details.get(
                    'count')) * int(details.get('damagePerShot'))
                data[f'dam{csvCount}'] = 1
                data[f'range{csvCount}'] = details.get('range')
                # Increment csvCount for the next weapon
            csvCount += 1

    return data


def generate_csv(data, output_file):
    """
    Generates a CSV file from the parsed BLK data.

    Args:
        data (dict): The dictionary containing the parsed data.
        output_file (str): The path to the output CSV file.
    """
    if not data:
        print("No data to write to CSV.")
        return

    fieldnames = [
        'model', 'tonnage', 'unittype', 'movement', 'tmm', 'armor',
        'wepname1', 'shots1', 'dam1', 'range1',
        'wepname2', 'shots2', 'dam2', 'range2',
        'wepname3', 'shots3', 'dam3', 'range3',
        'wepname4', 'shots4', 'dam4', 'range4',
        'wepname5', 'shots5', 'dam5', 'range5',
        'wepname6', 'shots6', 'dam6', 'range6',
        'wepname7', 'shots7', 'dam7', 'range7',
        'wepname8', 'shots8', 'dam8', 'range8',
        'wepname9', 'shots9', 'dam9', 'range9',
        'wepname10', 'shots10', 'dam10', 'range10',
        'ifnumber', 'specialrules'
    ]

    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            row = {
                'model': data.get('model', ''),
                'tonnage': data.get('tonnage', ''),
                'unittype': data.get('unittype', ''),
                'movement': data.get('movement', ''),
                'tmm': data.get('tmm', ''),
                'armor': data.get('armor', ''),
                'ifnumber': data.get('ifnumber', ''),
                'specialrules': data.get('specialrules', '')
            }
            for i in range(1, 11):
                row[f'wepname{i}'] = data.get(f'wepname{i}', '')
                row[f'shots{i}'] = data.get(f'shots{i}', '')
                row[f'dam{i}'] = data.get(f'dam{i}', '')
                row[f'range{i}'] = data.get(f'range{i}', '')
            writer.writerow(row)

        print(f"CSV data written to {output_file}")

    except Exception as e:
        print(f"Error writing to CSV: {e}")


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
        csv_writer.writerow(['common', 'unittype', 'fullname', 'armor', 'armorIcons', 'structure', 'structureIcons', 'movement', 'tmm', 'basepv', 'regpv', 'VetPV', 'RegSkill', 'VetSkill', 'specialrules', 'name', 'model', 'wepname1', 'shots1', 'dam1',
                            'range1', 'wepname2', 'shots2', 'dam2', 'range2', 'wepname3', 'shots3', 'dam3', 'range3', 'wepname4', 'shots4', 'dam4', 'range4', 'wepname5', 'shots5', 'dam5', 'range5', 'wepname6', 'shots6', 'dam6', 'range6', 'wepname7', 'shots7', 'dam7', 'range7',
                             'Combdam1', 'Combdam2', 'Combdam3', 'Combdam4', 'Combdam5', 'Combdam6', 'Combdam7'])

        for asset in asset_List:
            # Write each asset's data to the CSV
            equipment_list = list(asset.get('equipment', {}).items())[
                :7]  # Get the first 7 equipment entries
            csv_writer.writerow([
                0,
                asset.get('unittype'),
                strip_accents(asset.get('fullname')),
                asset.get('armor'),
                asset.get('armorIcons'),
                asset.get('structure'),
                asset.get('structureIcons'),
                asset.get('movement'),
                asset.get('tmm'),
                asset.get('basepv', 0),
                asset.get('regpv', 0),
                asset.get('VetPV', 0),
                asset.get('RegSkill', 0),
                asset.get('VetSkill', 0),
                asset.get('specialrules'),
                strip_accents(asset.get('Name')),
                strip_accents(asset.get('model')),
                asset.get('wepname1'),
                asset.get('shots1'),
                asset.get('dam1'),
                asset.get('range1'),
                asset.get('wepname2'),
                asset.get('shots2'),
                asset.get('dam2'),
                asset.get('range2'),
                asset.get('wepname3'),
                asset.get('shots3'),
                asset.get('dam3'),
                asset.get('range3'),
                asset.get('wepname4'),
                asset.get('shots4'),
                asset.get('dam4'),
                asset.get('range4'),
                asset.get('wepname5'),
                asset.get('shots5'),
                asset.get('dam5'),
                asset.get('range5'),
                asset.get('wepname6'),
                asset.get('shots6'),
                asset.get('dam6'),
                asset.get('range6'),
                asset.get('wepname7'),
                asset.get('shots7'),
                asset.get('dam7'),
                asset.get('range7'),
                asset.get('Combdam1'),
                asset.get('Combdam2'),
                asset.get('Combdam3'),
                asset.get('Combdam4'),
                asset.get('Combdam5'),
                asset.get('Combdam6'),
                asset.get('Combdam7')
            ])
    print("Done!")


if __name__ == "__main__":
    main()
