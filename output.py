import json
import logging
import time 
from wish import Wish
#TODO, add parameter checking for char/wep/wish stuff ig 
WISH_MAP = {
    "Character Event Wish": "character",
    "Character Event Wish-2": "character2",
    "Weapon Event Wish": "weapon",
    "Permanent Wish": "standard", 
    "Novice Wishes": "beginner"
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
 
    logging.info("Data verification finished")

def to_json(wishes, name = "wishes.json"):
    with open(name,'w') as f:
        json.dump([wish.json() for wish in wishes], f, indent=4)

def to_excel():
    pass

def json2excel():
    pass



def main():

    logging.basicConfig(level=logging.INFO)  
    with open('wishes.json', 'r') as f:
        wishes = json.load(f) 
        
    wishes = [Wish(**w) for w in wishes]
    data_verification(wishes)

if __name__ == "__main__": 
    main()