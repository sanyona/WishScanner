import json
import logging
import time 
from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.utils import units
from openpyxl import load_workbook
from wish import Wish
'''
Data verification and output to different formats
'''
#TODO, add parameter checking for char/wep/wish stuff ig 

WISH_MAP = {
    "Character Event Wish": "Character Event",
    "Character Event Wish-2": "Character Event",
    "Weapon Event Wish": "Weapon Event",
    "Permanent Wish": "Standard", 
    "Novice Wishes": "Beginners\' Wish"
} 

WISH_TYPE = {
    "Character Event Wish",
    "Character Event Wish-2",
    "Weapon Event Wish",
    "Permanent Wish",
    "Novice Wishes"
}

ITEM_TYPE = {
    "Weapon",
    "Character"
}

# TODO, load data from a reliable source instead of manual update
# TODO, update/autocorrect (possibly levenshtein distance)
# get_close_matches from difflib (built in) -> empty list is possible
def data_verification(wishes):
    # load all character/weapon values

    with open("data.json", "r") as f:
        data = json.load(f)
    CHARACTERS = data['characters']
    WEAPONS = data['weapons'] 
    logging.info("Successfully loaded character/weapon values")

    for wish in wishes:
        
        # rarity, wish type, item type
        if ( (wish.item_type not in ITEM_TYPE) or 
        (wish.wish_type not in WISH_TYPE) or
        (wish.rarity not in [3,4,5]) ):
            logging.error(f'Wish value incorrect {wish}') 
            break

        # item name
        if ((wish.item_type == 'Weapon') and (wish.item_name not in WEAPONS)) or ((wish.item_type == 'Character') and 
            (wish.item_name not in CHARACTERS)):
            logging.error(f'Wish item name incorrect {wish}')


        # timestamp 
        try:
            time.strptime(wish.time, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            logging.error(f'Wish time format incorrect {wish}') 
        if(not len(wish.time)==19): 
            logging.error(f'Wish time length incorrect {wish}') 
 
    logging.info("Data verification finished")
    return wishes

def wish2json(wishes, name = "wishes.json"):

    with open(name,'w') as f:
        json.dump([wish.json() for wish in wishes], f, indent=4)

def json2wish(json_file):
    with open('wishes.json', 'r') as f:
        wishes = json.load(f)
    wishes = [Wish(**w) for w in wishes] 
    return wishes

def json2excel(json_file, excel_file, dest_file):
    logging.info("Saving json to excel")
    wishes = json2wish(json_file)
    wish2excel(wishes, excel_file, dest_file)


def wish2excel(wishes, excel_file, dest_file):
    
    # item_type, item_name, time, rarity, <pity>, <roll>,<group>, <banner>, part (Wish 2) [character wish only]
    # separate by type
    sheets = ['Character Event', 'Weapon Event', 'Standard', 'Beginners\' Wish'] 
    # sort by sheet name/wish_type, values are lists
    wishes_by_type = dict()
    for wish in wishes:
        sheet_name = WISH_MAP[wish.wish_type]
        if(sheet_name in wishes_by_type):
            wishes_by_type[sheet_name].append(wish)
        else:
            wishes_by_type[sheet_name] = [wish] 

    # load excel sheet, TODO document downloading sheet from paimon.moe
    wb = load_workbook(excel_file)

    for sheet_name in sheets:
        curr_sheet = wb[sheet_name]  

        if(sheet_name not in wishes_by_type):
            continue 
        # TODO, check for wishes that are identical, use timestamp for comparison
        for wish in wishes_by_type[sheet_name]:
            curr_sheet.append(wish.excel_format())
        wb.save(dest_file)
 
    wb.save(dest_file)
    logging.info("Excel file successfully saved")