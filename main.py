import game
import dice
import property
import time
import datetime
import config

def initialize_game():
    print("\n \n")
    print(f"{'*'*50} WELCOME TO MONOPOLY!!! {'$'*50}")
    print("How many players are want to play the game? This game can be played with 2 to 8 players.")
    
    num_player = int(input("Please input no of players : "))
    print("\n")
    if num_player>=2 and num_player <= 8:
        game_obj.initialize_player(num_player)
        game_obj.remainning_players = num_player
        game_obj.read_board()
        game_obj.create_monopoly_space_list()
    else:
        print("Sorry, This game can be played with 2 to 8 players.")
        initialize_game()   


def main():
        
    round = 1
    
    while True:
        
        game_status = game_obj.check_game_end()             # Check game status is it END.
        if game_status == 1:
            return "END"
        
        if config.set_time_limit != 0:                      # If timer is set, then check whether timer goes off or not?
            game_status_1 = game_obj.check_timer_goes_off(game_obj)
            if game_status_1 == 1:
                return "END"

        print(f"{'*'*50} round {round} {'*'*50}")
        
        is_conti = str(input("Please press 1 to continue, press 2 to show player's details and please press 0 to exit the game."))

        if is_conti != "0" and is_conti != "1" and is_conti != "2":
            print("Please enter valid input")
            continue
        elif is_conti == "0":
            print("Thanks for playing the game")
            return "END"   
        elif is_conti == "2":
              game_obj.show_players_details()

        elif is_conti == "1":

            round += 1                                              # Increment round number
            print(f"Cash in bank : ${game_obj.bank.cash}")          # Cash in bank

            for p_name,turn_player in game_obj.players_details.items():     # Iterate over each player
            
                print("\n")
                print(f"==> Next turn -  {p_name}(Cash in Hand: ${turn_player.cash})")
                
                game_status = game_obj.check_game_end()               # Check game status is it END.
                if game_status == 1:
                    return "END"
                

                define_bankrupt = False
                while True:

                    is_bankrupt = turn_player.check_player_is_bankrupt(game_obj)     # Check turn player is bankrupt?
                    if is_bankrupt == 1:
                        print("You are bankrupt")
                        turn_player.bankrupt_action(p_name,game_obj)
                        define_bankrupt = True
                        break

                    is_in_jail = turn_player.check_user_in_jail(p_name,game_obj)    # Check player in jail?
                    is_neg_balance = turn_player.check_negative_balance()           # Check player has negative balance

                    if is_in_jail == 1 or is_neg_balance == 1:
                        #turn_player.open_menu(p_name,game_obj)                      # will ask the player to sell/mortgage property
                        turn_player.game_option(p_name,game_obj)
                        continue
                    else:
                        break
                                    
                if define_bankrupt == True:
                    continue

                while True:
                    print("\n")
                    is_turn = input(f"{p_name}, Please press 1 to show menu or press enter to roll the dice.\n")
                    if is_turn == "1":
                        turn_player.game_option(p_name,game_obj)
                        continue
                    
                    flag = turn_player.roll_the_dice_and_move()                    # Roll the dice and move 

                    
                    space = game_obj.board[turn_player.position]                   # Let's get the space of the player
                    print(f"You landed at {space.name}.\n")

                    if flag == 1:
                        print("You just crossed GO, you get $200 salary.\n")
                        turn_player.earn(200 , game_obj.bank)

                    if isinstance(space,property.Tax):
                        print(f"You need to pay ${space.tax} as tax.")
                        turn_player.pay(space.tax,game_obj.bank)
                    
                    if isinstance(space,property.Chance):
                        print(f"Yes, You earn ${space.get_money}")
                        turn_player.earn(space.get_money , game_obj.bank)

                    if isinstance(space,property.Chest):
                        print(f"Yes, You earn ${space.get_money}")
                        turn_player.earn(space.get_money , game_obj.bank)

                    if isinstance(space,property.Jail):
                        print(f"OOh, you are in jail. You need to pay ${space.pay_money} to get out of the jail.")
                        turn_player.is_in_jail = True
                        turn_player.position = 11
                                                            
                    if isinstance(space,property.Idle):
                        print(f"Great, you are in free space.")
                    
                    if isinstance(space,property.Property):
                        turn_player.handle_property_space(p_name,space,game_obj)
                    
                    break

if __name__ == "__main__":
    
    game_obj = game.Game()

    while True:
        try:
            initialize_game()
            break
        except:
            print("Please Enter the valid input.")    
            continue

    print("\n Let's start to play MONOPOLY...")
    print("\n")
    
    is_end = main()
    if is_end == "END":
        print(f"{'*'*40} END GAME {'*'*40}")