import random

class Property:
    def __init__(self,data):
        self.name = data['name']     # Name of the property
        self.position = data['position']  # Board position
        self.owner = None            # Owner of the property
        self.price = data['price']   # Price of the property
        self.rent = data['rent']     # Rent of the property
        self.is_mortgage = False     # Mortgage status
        

class Street(Property):
    def __init__(self,data):
        Property.__init__(self,data)

        self.monopoly = data['monopoly']
        self.build_cost = data['build_cost']
        self.no_of_building = 0
        self.is_hotel_built = False
        self.house_rent = {}        
        self.house_rent[1] = data['rent_house_1']
        self.house_rent[2] = data['rent_house_2']
        self.house_rent[3] = data['rent_house_3']
        self.house_rent[4] = data['rent_house_4']
        self.rent_hotel = data['rent_hotel']
        
    

class Railboard(Property):
    def __init__(self,data):
        Property.__init__(self,data)
        

class Utility(Property):
    def __init__(self,data):
        Property.__init__(self,data)

################################################################################################################
class space:
    def __init__(self,data):
        self.name = data['name']            # Property name
        self.position = data['position']    # Board position
        


class Tax(space):
    def __init__(self,data):
        space.__init__(self,data)
        self.tax = data['tax']

class Chance(space):
    def __init__(self,data):
        space.__init__(self,data)
        self.get_money = random.randint(10,50)

class Chest(space):
    def __init__(self,data):
        space.__init__(self,data)
        self.get_money = random.randint(10,50)

class Jail(space):
    def __init__(self,data):
        space.__init__(self,data)
        self.pay_money = 50

class Idle(space):
    def __init__(self,data):
        space.__init__(self,data)
        



        