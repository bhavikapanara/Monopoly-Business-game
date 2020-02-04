import pandas as pd
import property
import bank
import dice
import config
import time
import datetime
import math

class Game:
    def __init__(self):
        self.num_of_player = 0             
        self.players_details = {}
        self.bank = bank.Bank()
        self.remainning_players = None
        self.board = []
        self.players = None
        self.remainning_players_list = []
        self.timer = datetime.datetime.now() + datetime.timedelta(hours = config.set_time_limit)           # set timer
        self.no_of_houses = 32
        self.no_of_hotels = 12
        self.monopoly_property_dict = {}
        self.board_df = pd.read_csv('board.csv')                                                           # read board file

    def initialize_player(self,num_player):                              

        self.num_of_player = num_player
        self.bank.cash -= (num_player * config.initial_amt)

        print(f"Let's start to introduce all {num_player} players")
        
        for e in range(num_player):
            while True:
                s = f"What's the name of player {e+1} : "
                name = str(input(s))
                if name in self.players_details:                                        # Check Player name already exist?
                    print("Player name already exist! Please enter different name.")
                elif len(name) == 0:                                                    # Check name is not empty string?
                    print("Please Enter name: ")
                else:
                    self.players_details[name] = Player()
                    self.remainning_players_list.append(name)
                    break


    def check_game_end(self):                           # This function check: Is game End? if number of remainning player is one => game is end.
        if self.remainning_players == 1:  
            winner = self.remainning_players_list[0]
            print(f"Great {winner}, You win the game. Congrats!!!")
            return 1
        else:
            return 0

    def check_timer_goes_off(self,g_obj):                                                # Check timer?
        current_time = datetime.datetime.now()
        if self.timer > current_time:                                                    # Shows the remaining time
            remainning_duration = math.floor((self.timer-current_time).seconds/60.0)
            print(f"Remainning Time : {remainning_duration} minutes")
        if current_time > self.timer:
            print("Timer goes off. Game is end!!!")

            # Define winner
            winner_dic = {}
            for e in self.remainning_players_list:
                player_o = self.players_details[e]
                total_amt = player_o.cash                              # Cash in hand
                for pro in player_o.properties.values():
                    
                    pro_position = pro['pos']
                    space = g_obj.board[pro_position-1]
                    
                    if space.is_mortgage == False:                     # consider printed price for all unmortgaged properties
                        total_amt += space.price
                    if space.is_mortgage== True:                       # consider half of printed price all for mortgaged properties
                        total_amt += (space.price)/2.0

                    if isinstance(space,property.Street):
                        total_amt += space.no_of_building * space.build_cost    # consider no_of_house * build_cost

                        if space.is_hotel_built == True:
                            total_amt += space.build_cost                       # consider hotel build cost if hotel exist on property.
                    
                winner_dic[e] = total_amt
            winner = max(winner_dic, key=winner_dic.get)                       # win with maximum cash
            print(f"Great {winner}, You win the game. Congrats!!!")
            #################
            return 1
        else:
            return 0



    def show_bank_details(self):
        print("Bank Amount   : ",self.bank.cash)
        

    def show_players_details(self):                         # shows the player's details.
        print("\n")
        print(f"{'*'*50} Players Details {'*'*50}")
        for ind,val in self.players_details.items():
                        
            print("Player Name: ",ind)
            print(f"Cash In Hand: ${val.cash}")
            print("Current Positon: ",val.position)
            print("monopoly : ",val.monopoly)
            print("Bankrupt Status: ",val.bankrupt)
            print("Is player in jail? :",val.is_in_jail)

            print("\n")
            print(f"{'Property Name':^25} | {'Price($)':^15} | {'Monopoly':^20} | {'No of House':^20} | {'Is Hotel Built':^20}\n")

            for k,v in val.properties.items():                                              # List of  property on which you can build house/hotel

                pro_position = v['pos']
                space = self.board[pro_position-1]

                if isinstance(space,property.Street):
                    print(f"{k:^25} | {space.price:^15} | {space.monopoly:^20} | {space.no_of_building:^20} | {space.is_hotel_built:^20}")
                else:
                    print(f"{k:^25} | {space.price:^15} | {'--':^20} | {'--':^20} | {'--':^20}")
            print("\n")
    
        
    def create_monopoly_space_list(self):                          # Create a list of moopoly property  
        df = pd.read_csv("board.csv")
        temp_df = df.loc[df['class']=="Street"]
        df1 = temp_df.groupby('monopoly')['name'].apply(list).reset_index(name='new')
        
        for e in range(len(df1)):
            monopoly = df1['monopoly'].iloc[e]
            val = df1['new'].iloc[e]
            self.monopoly_property_dict[monopoly] = val
        

    def read_board(self):                                        # Read board
        board_df = pd.read_csv('board.csv')
        
        for _, row in board_df.iterrows():
            
            if row['class'] == 'Street':
                self.board.append(property.Street(row))

            if row['class'] == 'Railroad':
                self.board.append(property.Railboard(row))

            if row['class'] == 'Utility':
                self.board.append(property.Utility(row))

            if row['class'] == 'Tax':
                self.board.append(property.Tax(row))

            if row['class'] == 'Chance':
                self.board.append(property.Chance(row))

            if row['class'] == 'Chest':
                self.board.append(property.Chest(row))

            if row['class'] == 'Jail':
                self.board.append(property.Jail(row))

            if row['class'] == 'Idle':
                self.board.append(property.Idle(row))

########################################################## Player Class #########################################################

class Player:
    def __init__(self):
        
        self.cash =  config.initial_amt       # initial Cash 
        self.properties = {}                  #  initial list of properties
        self.monopoly = {}                    # initial list of monopoly
        self.position = 0                     # Board position
        self.bankrupt = False                 # Bankrupt status
        self.is_in_jail = False               # Jail status
    
    # When player is announced bankrupt
    def bankrupt_action(self,p_name,g_obj):      
        self.bankrupt = True                                              # Give status to Bankrupt
        g_obj.remainning_players -= 1                                     # Subtract 1 from remainning_players variable
        g_obj.remainning_players_list.remove(p_name)                      # remove player

        total_amt = 0
        for k,v in self.properties.items():
            pro_position = v['pos']
            total_amt += g_obj.board[pro_position-1].price              # count money
            g_obj.board[pro_position-1].owner = None                    # Remove owner form all properties of bankrupt player
        if total_amt > 0:
            self.pay(build_price , g_obj.bank)                          # Return all monry to bank 
        

    def check_player_is_bankrupt(self,g_obj):
        # Check 3 condition for bankrupt. If a player has negative cash, no house/hotel to sell and no unmortgage property => then player is bankrupt.
        unmortgage_pro_exist = False
        house_exist = False
        negative_bal = False

        if self.cash < 0:                                       # Negative cash
            negative_bal = True

        for k,v in self.properties.items():
            pro_position = v['pos']
            space = g_obj.board[pro_position-1]
            
            if isinstance(space,property.Street) and space.no_of_building > 0 :            # check house/hotel exist? 
                house_exist = True
            
            if space.is_mortgage == False :                          # checck unmortage property?
                unmortgage_pro_exist = True
        

        if negative_bal == True and unmortgage_pro_exist == False and house_exist == False:
            return 1
        else:
            return 0


    def sell_houses(self,g_obj):      # Sell house/hotel

        house_selling_pro_list = []
                
        print(f"{'ID':^10}  {'Property Name':^20} ==> {'Sell Price($)':^20}\n")
        

        for k,v in self.properties.items():         # Make list of properties which has house/hotel
            pro_position = v['pos']
            space = g_obj.board[pro_position-1]
            
            if isinstance(space,property.Street):
                if space.no_of_building > 0 or space.is_hotel_built == True:  

                    build_cost = (space.build_cost)/2.0
                    print(f"{space.position:^10}  {k:^20} ==> {build_cost:^20}")

                    house_selling_pro_list.append(space.position)

        if len(house_selling_pro_list) == 0:                 # No house/hotel 
            print("Sorry, Currently you don't have any house to sell.\n")
            return

        while True:
            try:
                sell_pro_ID = int(input("Please enter the property ID which you want to sell. Press 0 to cancel: "))
            except:
                continue
            
            if sell_pro_ID == 0:     # cancel
                return 
            if sell_pro_ID not in house_selling_pro_list:    # Check given property name exist in selling list?
                print("Please enter correct property ID from the above list : ")
                continue
            else:
                
                space = g_obj.board[sell_pro_ID-1]
                sell_house_price = (space.build_cost)/2.0        # BY selling house, player get half of the price.

                self.earn(sell_house_price , g_obj.bank)                           # get money of your property from bank

                if space.is_hotel_built == True:                         # If hotel is built on property
                    space.is_hotel_built = False                         # set no hotel on property
                    g_obj.no_of_hotels += 1                              # Increase 1 hotel to bank
                else:                                                    # If house is built on property
                    space.no_of_building -= 1                            # Readuce 1 house from that property
                    self.properties[space.name]['no_of_house'] -= 1                 
                    g_obj.no_of_houses += 1                              # Increase 1 house to bank
                
                return 


    def recommand_prop_for_house_building(self,g_obj):     # Build house evenly on color-set property(monopoly)
        
        # Prepare list of properties on which player can build house
        house_building_pro_list = []

        # Find the colorset property based on monopoly size
        your_monoploy_list = [k for k,v in self.monopoly.items() if (v==3) or ((k=="Brown" or k=="Dark Blue") and v==2) ]
        print(f"Your monopoly list : {your_monoploy_list}\n")

        for a in your_monoploy_list:
            temp_dic_cnt_no_house = {e: self.properties[e]['no_of_house'] for e in g_obj.monopoly_property_dict[a] if self.properties[e]['no_of_house'] <= 4}
            min_val = min(list(temp_dic_cnt_no_house.values()))
        
            house_building_pro_list.append([k for k,v in temp_dic_cnt_no_house.items() if v == min_val])

        house_building_pro_list = [f for e in house_building_pro_list for f in e]

        return house_building_pro_list

    def build_house(self,g_obj):                            # Build house/hotel

        house_build_list = []
        if g_obj.no_of_houses == 0 and g_obj.no_of_hotels == 0:
            print("Sorry, Bank doesn't have any house and hotel.\n")
            return

        house_building_pro_list = self.recommand_prop_for_house_building(g_obj)

        if len(house_building_pro_list) == 0:
            print("Sorry, Currently you are not able to build any house.\n")
            return

        print("Please select the property ID on which you want to build house?\n")

        print(f"{'ID':^10}  {'Property Name':^20} ==> {'House Building Price($)':^20}\n")

        for x in house_building_pro_list:                                              # List of  property on which you can build house/hotel
            pro_position = g_obj.board_df['position'][g_obj.board_df.name==x].values[0]

            space = g_obj.board[pro_position-1]

            build_cost = space.build_cost 
            print(f"{space.position:^10}  {x:^20} ==> {build_cost:^20}")
            house_build_list.append(space.position)

        while True:
            try:
                build_house_pro_ID = int(input("Please enter the property ID on which you want to build house. Press 0 to cancel : "))
            except:
                continue
            
            if build_house_pro_ID == 0:
                return 
            if build_house_pro_ID not in house_build_list:
                print("Please enter correct property ID from the above list : ")
                continue
            else:
                #pro_position = self.properties[build_house_pro_name]['pos']    
                space = g_obj.board[build_house_pro_ID-1]

                build_price = space.build_cost 
                no_of_existing_building = space.no_of_building

                if self.cash >= build_price:                       # Check player has sufficient amount to buy house/hotel
                    self.pay(build_price , g_obj.bank)                           
                    build_house_pro_name = space.name

                    if no_of_existing_building == 4:               # build hotel
                        self.properties[build_house_pro_name]['no_of_house'] = 0
                        space.no_of_building = 0
                        g_obj.no_of_houses += 4

                        space.is_hotel_built = True
                        g_obj.no_of_hotels -= 1
                    else:                                          # Build house
                        self.properties[build_house_pro_name]['no_of_house'] += 1
                        space.no_of_building += 1
                
                        g_obj.no_of_houses -= 1
                    return 
                else:
                    print("You don't have sufficient amount to build house.\n")
                    continue

    def redeem_property(self,g_obj):          # Redeem mortgaged property
        
        # create a list of mortgaged property which player can redeem
        redeem_pro_list = []
        print("Please select the property which you want to redeem?")
        print(f"To unmortgage it, the player must pay 10% interest when he/she pay it off.\n")
        
        print(f"{'ID':^10}  {'Property Name':^20} ==> {'Property Price($)':^20}\n")
        for k,v in self.properties.items():
            pro_position = v['pos']
            space = g_obj.board[pro_position-1]

            if space.is_mortgage == True:  
                print(f"{space.position:^10}  {k:^20} ==> {v['price']:^20}")
                redeem_pro_list.append(space.position)

        if len(redeem_pro_list) == 0:
            print("Sorry, Currently you don't have any mortgage property.\n")
            return

        while True:
            try:
                redeem_pro_ID = int(input("Please enter the propert ID which you want to redeem. Press 0 to cancel : "))
            except:
                continue

            if redeem_pro_ID == 0:
                return 
            if redeem_pro_ID not in redeem_pro_list:
                print("Please enter correct property ID from the above list : ")
                continue
            else:

                space = g_obj.board[redeem_pro_ID-1]

                pro_price = space.price
                redeem_price = (pro_price/2) + (pro_price * 0.1)               # Redeem price is with 10% interest
                space.is_mortgage = False                # update mortgage status to false 

                self.pay(redeem_price , g_obj.bank)                            # pay redeem money to bank 
                
                return 

    def mortgage_property(self, p_name, g_obj):       # Mortgage property

        # create a list of mortgaged property which player can redeem
        mortgage_pro_list = []
        print("Please select the property which you want to mortgage? You get half of the property price by mortgaging property.\n")
        
        print(f"{'ID':^10}  {'Property Name':^20} ==> {'Property Price($)':^20}\n")
        for k,v in self.properties.items():
            pro_position = v['pos']
            space = g_obj.board[pro_position-1]
            if space.is_mortgage == False:  
                print(f"{space.position:^10}  {k:^20} ==> {v['price']:^20}")
                mortgage_pro_list.append(space.position)

        if len(mortgage_pro_list) == 0:
            print("Sorry, Currently you don't have any property to mortgage.\n")
            return

        while True:
            try:
                mortgage_pro_ID = int(input("Please enter the property ID which you want to mortgage. Press 0 to cancel : "))
            except:
                continue

            if mortgage_pro_ID == 0:
                return 
            if mortgage_pro_ID not in mortgage_pro_list:
                print("Please enter correct property ID from the above list : ")
                continue
            else:
                
                space = g_obj.board[mortgage_pro_ID-1]
                mortgage_price = space.price/2.0
                space.is_mortgage = True

                #mortgage_price = (self.properties[mortgage_pro_name]['price'])/2
                #pro_position = self.properties[mortgage_pro_name]['pos']
                #g_obj.board[pro_position-1].is_mortgage = True                     # is_mortgage statue change
                self.earn(mortgage_price , g_obj.bank)                           # get money of your property from bank
                
                return 
      

    def pay(self,payment,desti):
                
        self.cash -= payment
        desti.cash += payment
        print("\n")
        print(f"Debited amount : ${payment}")
        print(f"Current balance: ${self.cash}\n")
            
    
    def earn(self,payment,desti):
        
        if desti.cash >= payment:
            desti.cash -= payment
            self.cash += payment
        print("\n")
        print(f"Credited amount: ${payment}")
        print(f"Current balance: ${self.cash}\n")

    
    def roll_the_dice_and_move(self):
        # Let's roll the dice
        dice_obj = dice.Dice()
        dice_obj.roll_the_dice()

        old_position = self.position
        self.position += dice_obj.dice_sum

        flag = 0
        # Move the player
        if self.position >= 40:
            self.position -= 40
            flag = 1

        print(f"You move from {old_position} to {self.position} on board")
        return flag

    def handle_property_space(self,p_name,space,game_obj):
        while True:
            if space.owner == None:                       # No owner assign?
                if isinstance(space,property.Street):
                    print(f"Do you want to buy this property {space.name} [monopoly-{space.monopoly}] at price ${space.price}? Otherwise you need to pay rent ${space.rent}.\n")
                else:
                    print(f"Do you want to buy this property {space.name} at price ${space.price}? Otherwise you need to pay rent ${space.rent}.\n")

                print(f"Currently, you have ${self.cash} cash in hand.\n")
                while True:
                    ans = str(input("Press (Y/N)? (To open the menu Press 1) : "))
                    if ans == 'y' or ans == 'Y' or ans == 'N' or ans == 'n' or ans == "1":
                        break
                    else:
                        print("Please enter valid input")

                if ans== 'Y' or ans=='y':     # Player want to buy this property

                    if self.cash >= space.price: 
                        self.pay(space.price,game_obj.bank)
                        space.owner = p_name
                        print(f"Property {space.name} has been bought successfully.\n")
                        self.properties[space.name] = {'pos':space.position, 'price':space.price, 'no_of_house':0}
                        # add monopoly
                        if isinstance(space,property.Street):
                            try:
                                self.monopoly[space.monopoly] += 1
                            except:
                                self.monopoly[space.monopoly] = 1
                        return
                    else:
                        print("You don't have sufficient amount to buy property\n")
                    
                elif ans == 'N' or ans == 'n':     # Player not interested to buy property
                    print(f"You need to pay the rent ${space.rent} for this property")
                    self.pay(space.rent , game_obj.bank)   
                    return                     
                elif ans == "1":
                    self.game_option(p_name,game_obj)

            else:                     # already own by player

                if space.owner == p_name:       # if turn player is owner of the property
                    print("This property is already owned by you. \n") 
                    return   
                else:
                    if space.is_mortgage == True:                 # If player land on mortgaged property => no need to pay rent
                        print("This property is mortgaged, you don't need to pay rent.")
                        return
                    else:                          # Pay rent to owner player
                        if isinstance(space,property.Street):
                            if space.no_of_building > 0:    
                                pay_rent = space.house_rent[space.no_of_building]     # pay rent as number of house built on property
                            elif space.is_hotel_built == True:
                                pay_rent = space.rent_hotel                           # If hotel is built on the property
                            else:
                                pay_rent = space.rent
                        else:
                            pay_rent = space.rent

                        print(f"This property is owned by {space.owner}. So, you need to pay rent ${pay_rent}.")
                        self.pay(pay_rent , game_obj.players_details[space.owner])
                        return

    def open_menu(self,p_name,game_obj):
        while True:
            self.game_option(p_name,game_obj)
            is_menu = str(input("Do you want to open menu again? Press (Y/N) : "))
            if is_menu == 'Y' or is_menu == 'y':
                continue
            elif is_menu == 'N' or is_menu == 'n':
                return

    def check_negative_balance(self):
        if self.cash < 0:
            print(f"You owe the bank.Dept is {self.cash}")
            print("You cannot roll the dice until you repay the bank. (Sell/Mortgage)")
            return 1
        else:
            return 0

    def check_user_in_jail(self,p_name,game_obj):             # Check user in jail?
        if self.is_in_jail == True:
            print(f"{p_name}, you are in jail. you need to pay $50 bail to get out of the jail. Otherwise your turn will be skipped.")
            if self.cash < 50:
                print("You don't have sufficient amount.(Sell/Mortgage)\n")
                return 1
            else:
                self.pay(50 , game_obj.bank)                  # Pay $50 bail
                self.is_in_jail = False
                print("yes, you are out of the jail")
                return 0

    def game_option(self,p_name,g_obj):                       # Menu option 
        print("\n  **** MENU *****")
        print("\n Press (B/b) to build the house \n Press (S/s) to sell the house \n Press (M/m) to mortgage the land \n Press (R/r) to redeem the land. \n Press 0 to cancel")
        
        while True:
            inp1 = str(input("\n Please enter valid input value : "))
            if inp1 == "B" or inp1 == "b":                    # build house/hotel
                self.build_house(g_obj)
                return
            elif inp1 == "S" or inp1 == "s":                  # sell house/hotel
                self.sell_houses(g_obj)
                return
            elif inp1 == "M" or inp1 == 'm':                  # Mortgage property
                self.mortgage_property(p_name,g_obj)
                return
            elif inp1 == "R" or inp1 == "r":                 # Redeem property
                self.redeem_property(g_obj)
                return
            elif inp1 == "0":
                return
            else:
                continue

class Bank:
    def __init__(self):
        self.cash = 20000