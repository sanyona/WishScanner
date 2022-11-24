class Wish:
    def __init__(self, item_type, item_name, wish_type, time, rarity):
        self.item_type = item_type
        self.item_name = item_name
        self.wish_type = wish_type
        self.time = time
        self.rarity = rarity 

    def __str__(self):
        return f'{self.item_type} {self.item_name} ({self.rarity}-star) from banner {self.wish_type} {self.time}'

    def json(self):
        return {
            "item_type": self.item_type,
            "item_name": self.item_name, 
            "wish_type": self.wish_type,  
            "time": self.time, 
            "rarity": self.rarity  
        }