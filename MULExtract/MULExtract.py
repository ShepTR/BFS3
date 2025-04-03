import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import pandas as pd
from tqdm.auto import tqdm
current_datetime = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
timestamp = str(current_datetime)
# Define the URL for all battlemechs
# unitType = "Battlemechs"
# search_url = "http://www.masterunitlist.info/Unit/Filter?Types=18"
# Define the URL for all vehicles
# unitType = "Vehicles"
# search_url = "http://www.masterunitlist.info/Unit/Filter?Types=19"
unitType = "Battle Armor"
search_url = "http://www.masterunitlist.info/Unit/Filter?SubTypes=28"
# # Define the URL for all protomechs
# unitType = "Protomechs"
# search_url = "http://www.masterunitlist.info/Unit/Filter?Types=23"
# Send an HTTP GET request to the URL
response = requests.get(search_url)
if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    print("Access granted!")
else:
    print("Failed to retrieve the webpage.")
# Find all units
unit_names = [
    a.text for a in soup.find_all('a', href=True) if a['href'].startswith("/Unit/Details/")
]
dataset = pd.DataFrame(columns=["Name", "Class", "Model", "Role", "PV", "BV", "Type", "Size", "Tonnage", "Move",
                                "Short", "Medium", "Long", "Overheat", "Armor", "Structure",
                                "Specials", "ImageURL", "MULId"])
unit_urls = [a['href'] for a in soup.find_all(
    'a', href=True) if a['href'].startswith("/Unit/Details/")]
for i, unit_name in enumerate(unit_names):
    if (i % 50 == 0):
        percent_complete = (i + 1) / len(unit_urls) * 100
        print(
            f"Parsing {i + 1} of {len(unit_urls)} units - {percent_complete:.2f}% complete")

    # Define the URL with the query parameters
    url = f"https://masterunitlist.azurewebsites.net/Unit/QuickList?Name={unit_name}"

    # Send an HTTP GET request with the parameters
    response = requests.get(url, stream=True)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:

        # Parse the JSON response
        data = response.json()

        # Identify which unit should be parsed as one request may return several units. For example:
        # https://masterunitlist.azurewebsites.net/Unit/QuickList?Name=Phoenix%20Hawk%20PXH-1k

        for item in data.get("Units"):
            if (item.get("Name") == unit_name):
                index = data.get("Units").index(item)
     

        # Extract the desired information
        parsed_unit = {
            "Name": data.get("Units")[index].get("Name",""),
            "Class": data.get("Units")[index].get("Class",""),
            "Model": data.get("Units")[index].get("Variant",""),
            "Role": data.get("Units")[index].get("Role").get("Name"),
            "PV": data.get("Units")[index].get("BFPointValue", 0),
            "BV": data.get("Units")[index].get("BattleValue", 0),
            "Type": data.get("Units")[index].get("BFType", ""),
            "Size": data.get("Units")[index].get("BFSize", 0),
            "Tonnage": data.get("Units")[index].get("Tonnage", 0),
            "Move": data.get("Units")[index].get("BFMove", ""),
            "Short": data.get("Units")[index].get("BFDamageShort", 0),
            "Medium": data.get("Units")[index].get("BFDamageMedium", 0),
            "Long": data.get("Units")[index].get("BFDamageLong", 0),
            "Overheat": data.get("Units")[index].get("BFOverheat", 0),
            "Armor": data.get("Units")[index].get("BFArmor", 0),
            "Structure": data.get("Units")[index].get("BFStructure", 0),
            "Specials": data.get("Units")[index].get("BFAbilities", ""),
            "ImageURL": data.get("Units")[index].get("ImageUrl", ""),
            "MULId": data.get("Units")[index].get("Id", "")
        }

        # Add unit parameters to the dataframe
        dataset = pd.concat(
            [dataset, pd.DataFrame([parsed_unit])], ignore_index=True)

print(f"Data has been saved to 'datase' DataFrame")
dataset.info()
dataset.nunique()
unitlist = dataset[dataset['PV'] != 0].reset_index(drop=True)
unitlist.info()
unitlist[unitlist["Model"].isna()].head()
unitlist[unitlist["Specials"].isna()].head()
# Define the list of eras
# eras = [
#     {"Name": "Star League (2571 - 2780)", "ID": "star-league"},
#     {"Name": "Early Succession War (2781 - 2900)",
#      "ID": "early-succession-war"},
#     {"Name": "Late Succession War - LosTech (2901 - 3019)",
#      "ID": "late-succession-war---lostech"},
#     {"Name": "Late Succession War - Renaissance (3020 - 3049)",
#      "ID": "late-succession-war---renaissance"},
#     {"Name": "Clan Invasion (3050 - 3061)", "ID": "clan-invasion"},
#     {"Name": "Civil War (3062 - 3067)", "ID": "civil-war"},
#     {"Name": "Jihad (3068 - 3085)", "ID": "jihad"},
#     {"Name": "Early Republic (3086 - 3100)", "ID": "early-republic"},
#     {"Name": "Late Republic (3101 - 3130)", "ID": "late-republic"},
#     {"Name": "Dark Ages (3131 - 3150)", "ID": "dark-age"},
#     {"Name": "ilClan (3151 - 9999)", "ID": "ilclan"}
# ]

# # Create era availabilty dataset to fill later
# era_av = pd.DataFrame(columns=[era["Name"] for era in eras])

# # Send an HTTP GET request to the URL
# response = requests.get(search_url)

# # Check if the request was successful
# if response.status_code == 200:
#     soup = BeautifulSoup(response.text, 'html.parser')

#     # Find all unit URLs
#     unit_urls = [a['href'] for a in soup.find_all(
#         'a', href=True) if a['href'].startswith("/Unit/Details/")]

#     for i, unit_url in enumerate(unit_urls):
#         if i % 50 == 0:
#             percent_complete = (i + 1) / len(unit_urls) * 100
#             print(
#                 f"Parsing {i + 1} of {len(unit_urls)} units - {percent_complete:.2f}% complete")

#         unit_details_url = f"http://www.masterunitlist.info{unit_url}"
#         unit_response = requests.get(unit_details_url)
#         unit_soup = BeautifulSoup(unit_response.text, 'html.parser')

#         unit_era = {'Name': f'{unit_soup.find("h2").get_text().strip()}'}

#         # Make a dict for each unit
#         for era in eras:
#             faction_era_element = unit_soup.find(id=era["ID"])
#             if faction_era_element != None:
#                 factions = [a.get_text().strip()
#                             for a in faction_era_element.find_all("a")]
#                 unit_era[f"{era['Name']}"] = ", ".join(factions)
#             else:
#                 unit_era[f"{era['Name']}"] = "Unknown"

#         # Add unit eras to the dataframe
#         era_av = pd.concat(
#             [era_av, pd.DataFrame([unit_era])], ignore_index=True)


# print(f"Data has been saved to 'era_av' dataset")
# era_av.head()
# unitlist = unitlist.join(era_av.set_index('Name'), on='Name', how="left")
unitlist.head()
path = f"{unitType}_unit_list_{timestamp}.csv"
unitlist.to_csv(path, index=False)

def doBSFSpecials (alphaSpecials):
    print("name")