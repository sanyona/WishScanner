class Wish:
    def __init__(self, item_type, item_name, wish_type, time, rarity):
        self.item_type = item_type
        self.item_name = item_name
        self.wish_type = wish_type
        self.time = time
        self.rarity = rarity 

    def __str__(self):
        return f'{self.item_type} {self.item_name} ({self.rarity}-star) from banner {self.wish_type} {self.time}'

    def __repr__(self):
        return f'{self.item_type} {self.item_name} ({self.rarity}-star) from banner {self.wish_type} {self.time}'
        
    def json(self):
        return {
            "item_type": self.item_type,
            "item_name": self.item_name, 
            "wish_type": self.wish_type,  
            "time": self.time, 
            "rarity": self.rarity  
        }

    # item_type, item_name, time, rarity, <pity>, <roll>,<group>, <banner>, part (Wish 2) [character wish only]
    def excel_format(self):
        return [
            self.item_type, 
            self.item_name, 
            self.time,
            self.rarity,
            "", "", "", "", 
            "Wish 2" if self.wish_type == "Character Event Wish-2" else ""
        ]
        