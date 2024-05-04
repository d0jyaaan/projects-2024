import random 
import os
import tabulate


from copy import deepcopy

NUMBERS = ["",1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]

WORDLIST_FILENAME = "words.txt"


def main():

    game = sgame()

    clear_terminal()

    # assign each player a hand of 7 tiles
    game.generate_player_hands([])

    # While the game is running
    while True:

        # print out the board
        game.board.print_board()
        # print out every player's hand
        game.print_hands()

        # let player choose to exchange tile, skip or place tile
        choice = None
        flag = False
        # check whether game ended for not
        if len(game.letters()) == 0:
            for i in range(len(game.player_hands)):
                if len(game.player_hands[i]) == 0:
                    index = i
            
            for i in range(len(game.player_hands)):
                if index != i:
                    for tile in game.player_hands[i]:
                        game.player_points[index] += game.letter_values[tile]
            
            choice = 5

        while choice == None:

            print(f"Player {game.player_turn + 1}'s turn ")
            print("1. Place Tile   2. Skip   3. Exchange Tile   4. Shuffle   5. End Game")

            choice = input()
            # check whether the user input is within the valid range
            try:
                choice = int(choice)
                if 0 < choice <= 4:
                    break

            except ValueError:
                choice = None

        # player decides to play and place tiles on board
        if choice == 1:

            # prompt current player to place down tiles at coordinates
            p1, p2, word, words_formed = None, None, None, None
            while not(check_input(p1, p2, word, game, words_formed)):
                
                words_formed = []
                # coordinate / position 1
                p1 = input("Place first tile at: ").split()

                # let player go back to selection menu
                if p1[0] == '0':
                    choice == None
                    flag = True
                    clear_terminal()
                    break

                # coordinate / position 2
                p2 = input("Place last tile at: ").split()
                # word formed
                word = input("Word : ").upper()

                    
            if not flag:
                # calculate score of word formed by player
                score = 0
                for word_2 in words_formed:
                    if word_2.count_score == True:
                        score = game.calculate_score(word_2)
                        game.player_points[game.player_turn] += score

                # update the current state of scrabble board by placing down the tiles of current player's word
                game.board.place_tile(p1, p2, word)
                # if player place down a word, let the player draw n tiles from the bag
                game.update_hands()
                # add move to move history
                game.add_history(word_data(p1, p2, word, True), score, words_formed)
                print(game.move_history)
                # change the current player to the next one
                game.update_player_turn()
                
                # clear the terminal (aesthetic)
                # clear_terminal()
            
        # player decides to skip his/her turn
        elif choice == 2:
            game.update_player_turn()
        
        # player decides to exchange tiles
        elif choice == 3:
            
            flag_3 = False
            ex_tile = None
            while not check_exchange_tiles(ex_tile, game):

                ex_tile = input("Tiles to exchange : ").split()
                if ex_tile == 0:
                    flag = True
                    choice = 0
                    break

            if not flag_3:
                game.exchange_tiles(ex_tile)
                # change the current player to the next one
                game.update_player_turn()
                # clear the terminal (aesthetic)
                clear_terminal()

        # shuffle the tiles of player
        elif choice == 4:
            
            random.shuffle(game.player_hands[game.player_turn])

        # end the game and announce the scores and winner
        elif choice == 5:
            
            clear_terminal()
            game.board.print_board()
            header = []
            points = []
            for i in range(game.n_players):
                header.append(f"Player {i + 1}")
                points.append(f"{game.player_points[i]}")

            print(tabulate.tabulate([points], headers=header, tablefmt="grid"))

            if points.count(points[game.player_points.index(max(game.player_points))]) == 1:

                print(f"Player {game.player_points.index(max(game.player_points)) + 1} Wins!")

            # in case of draw
            else:
                print("Draw!")

            print('Thanks for playing!')
            # end the game
            break


def check_input(p1, p2, word, game, words_formed):

    """
    Check whether the given word and coordinates are valid moves or otherwise

    Conditions :
        1. Tiles must at least be placed at (8, 8) if is first move

        2. Check whether the spaces between p1 and p2 are the same as length of word given
            - If only 1 tile is placed, dont need to check
        
        3. The coordinates are all empty spaces or has the same tile as the word
        
        4. Player has the exact tiles to spell the word. 
            Eg : 'Apple' -> Player must have the tiles 'A', 'P', 'P', 'L', 'E'

        5. Check the validity of given word in the dictionary

        6. Check whether the tiles placed form a new word and whether the words are valid or not

        7. Check for wild tile 
    """

    # check input to ensure tile range is valid
    if (check_user_input_integer(p1, p2)) == False:
        return False

    if word == None:
        return False
    

    p1 = (int(p1[0]), int(p1[1]))
    p2 = (int(p2[0]), int(p2[1]))
    # condition 1
    if game.collective_turn == 0 and game.player_turn == 0:
        if not(p1[0] <= 8 <= p2[0] and p1[1] <= 8 <= p2[1]):
            return False

    # condition 2
    word_length = len(word)
    orientation = None
    
    if word_length >= 1:

        # row
        if (abs(p1[0] - p2[0]) == 0 and abs(p1[1] - p2[1]) >= 1):
            
            orientation = True
            (abs(p1[1] - p2[1]) + 1 , word_length)
            if (abs(p1[1] - p2[1]) + 1 != word_length):
                return False

        # column
        elif (abs(p1[0] - p2[0]) >= 1 and abs(p1[1] - p2[1]) == 0):
            
            orientation = False
            if (abs(p1[0] - p2[0]) + 1 != word_length):
                return False
    
    else:
        return False

    # condition 3
    n = 0
    old_hand = game.player_hands[game.player_turn]
    new_hand = deepcopy(old_hand)
    
    # print(new_hand)
    for i in range(p1[0]-1, int(p2[0])):

        for j in range(p1[1]-1, int(p2[1])):

            flag = False

            if (game.board.state[i][j] == ""):

                # condition 4
                if old_hand.count(word[n]) < word.count(word[n]):
                    if "Wild" in new_hand:
                        if old_hand.count("Wild") + old_hand.count(word[n]) >= word.count(word[n]):
                            
                            game.wilds.append([(i,j), word[n]])
                            new_hand.remove("Wild")
                            old_hand.append(word[n])
                            flag = True
                        else:
                            return False
                    else:
                        return False
                

            elif (game.board.state[i][j] != ""):
                
                if old_hand.count(word[n]) < word.count(word[n]):
                
                    if word[n] != game.board.state[i][j]:
                        # failure here does not accept word that is formed from already placed word
                        return False
                
                flag = True

            elif (word[n] != game.board.state[i][j]):
                # print(word[n] , game.board.state[i][j])
                return False
            
            if not flag:
                new_hand.remove(word[n])

                
            n += 1

    # condition 5 / 6
    # if word is vertical word, check from top to bottom
    # if word is horizontal word, check from left to right 
    x = check_new_word(p1, p2, word, game, orientation)

    if x == False:
        return False
    else:
        words_formed.append(x)

    # if vertical, check for word formed by each letter horizontally
    # if horizontal, check for word formed by each letter vertically

    # row
    temp_word = ""
    for i in range(len(word)):

        if orientation:
            temp_word = check_new_word([p1[0], p1[1] + i], [p1[0], p1[1] + i], word[i], game, False)
            
    # column
        else:
            temp_word = check_new_word([p1[0] + i, p1[1]], [p1[0]+i, p1[1]], word[i], game, True)

        if temp_word != False:
            if temp_word != None:
                words_formed.append(temp_word)

        elif temp_word == False:
            return False
    
    # print(f"Word formed: {words_formed}")
    # word formed must be connected to another word except for first move
    if not(game.collective_turn == 0 and game.player_turn == 0):
        
        n = 0
        for wdata in words_formed:
            if wdata.count_score == True:
                n += 1
        
        if n == len(words_formed):
            return False

    # passes all checks
    game.player_hands[game.player_turn] = new_hand
    return True


    

def check_new_word(p1, p2, word, game, orientation):
    
    
    p1 = [p1[0] - 1, p1[1] - 1]
    p2 = [p2[0] - 1, p2[1] - 1]

    
    # if next tile is blank, stop the loop
    # if next tile is not blank, continue till blank

    new_word = ""
    track_word = ""
    n = 0
    
    r = [None, None]

    # row
    if orientation:
        
        # check to left side first then to right side
        # left side
        for i in range(0, 15):

            if p1[1] - i >= 0:
                
                if game.board.state[p1[0]][p1[1] - i] == "":
                    
                    if r[0] == None:

                        if p1[1] - i != p1[1]:
                            r[0] = p1[1] - i

                        elif p1[1] - i == 0:
                            r[0] = 0

                    else:
                        break

            else:
                break
            
        # right side
        for i in range(0, 15):

            if p2[1] + i <= 14:
                
                if game.board.state[p2[0]][p2[1] + i] == "":
    
                    if r[1] == None:

                        if p2[1] + i != p2[1]:
                            r[1] = p2[1] + i

                        elif p2[1] + i == 14:
                            r[0] = 14

                    else:
                        break
            else:
                break
        
        # check if word is in the list of valid words
        # if the word is valid, return the word, else return false
        
        for i in range(r[0], r[1] + 1):
            
            # form word starting from the first index to last
            if i <= p2[1] and i >= p1[1]:
                new_word += word[n]
                n += 1
                
            else:
                new_word += game.board.state[p2[0]][i]
            
            track_word += game.board.state[p2[0]][i]
                 
    # column
    else:

        # check from top to bottom
        # top
        for i in range(0, 15):

            if p1[0] - i >= 0:
                if game.board.state[p1[0] - i][p1[1]] == "":
                   
                    if r[0] == None:

                        if p1[0] - i != p1[0] :
                            r[0] = p1[0] - i

                        elif p1[0] - i == 0:
                            r[0] = 0

                    else:
                        break

            else:
                break
            
        # bottom
        for i in range(0, 15):

            if p2[0] + i <= 14:
                
                if game.board.state[p2[0] + i][p2[1]] == "":

                    if r[1] == None:

                        if p2[0] + i != p2[0]:
                            r[1] = p2[0] + i

                        elif p2[0] + i == 14:
                            r[1] = 14

                    else:
                        break
            else:
                break
        
        # check if word is in the list of valid words
        # if the word is valid, return the word, else return false
        for i in range(r[0], r[1] + 1):
            # form word starting from the first index to last

            if i <= p2[0] and i >= p1[0]:
                new_word += word[n]
                n += 1
            else:
                new_word += game.board.state[i][p2[1]]
            
            track_word += game.board.state[i][p2[1]]

    p1p2 = [[None, None], [None, None]]

    if orientation:
        p1p2 = [[p1[0], r[0] + 2],[p1[0], r[1]+ 2]]
    else:
        p1p2 = [[r[0]+ 2, p1[0]],[r[1] + 2, p1[0]]]
        
    if new_word in game.word_list:
        if new_word != track_word:
            return word_data(p1p2[0], p1p2[1], new_word, True)
        
        elif new_word == word:
            return word_data(p1p2[0], p1p2[1], new_word, True)

        elif new_word == track_word:
            return word_data(p1p2[0], p1p2[1], new_word, False)
    
    elif len(word) == 1:
        return None
    
    elif new_word not in game.word_list:
        return False
   

def check_user_input_integer(p1, p2):

    """
    Check user input whether the input is a integer between 1 and 15
    Ensure user input is not a string that contains alphabets
    User input is a list representing (x,y) coordinates on scrabble board
    """

    temp_list = [p1, p2]

    for coord in temp_list:

        if not (coord == None):
            # Ensure length of user input is in (x,y) coordinate form
            if (len(coord) != 2):
                return False
            
            # Ensure user input is not a string that contains alphabets
            for i in coord:
                try:
                    
                    val = int(i)
                    # Check user input whether the input is a integer between 1 and 15
                    if not(1 <= val <= 15):
                        # print("Error 1")
                        return False

                except ValueError:
                    # print("Error 2")
                    return False

        else:
            return False

    return True


def check_exchange_tiles(ex_tile, game):

    """
    Check whether the tiles to be exchange are in the current player's hand or not
    """

    if ex_tile == None:
        return False
    
    for tile in ex_tile:
        if len(tile) == 1:
            tile = tile.upper()

        if tile not in game.player_hands[game.player_turn]:
            return False
    
    return True


def clear_terminal():

    """
    Clear the terminal
    """

    os.system('cls' if os.name == 'nt' else 'clear')


class sgame:

    def __init__(self):

        self.letter_values = {
            'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G': 2, 'H': 4, 'I': 1, 'J': 8, 'K': 5, 'L': 1, 'M': 3, 'N': 1, 'O': 1, 'P': 3, 'Q': 10, 'R': 1, 'S': 1, 'T': 1, 'U': 1, 'V': 4, 'W': 4, 'X': 8, 'Y': 4, 'Z': 10, "Wild": 0
        }

        self.letter_count = {
            'A': 9, 'B': 2, 'C': 2, 'D': 4, 'E': 12, 'F': 2, 'H': 3, 'H': 2, 'I': 9, 'J': 1, 'K': 1, 'L': 4, 'M': 2, 'N': 6, 'O': 8, 'P': 2, 'Q': 1, 'R': 6, 'S': 4, 'T': 6, 'U': 4, 'V': 2, 'W': 2, 'X': 1, 'Y': 2, 'Z': 1, "Wild" : 2
        }

        self.player_points = []

        self.n_players = self.get_n_players()

        self.player_hands = [['I' , 'Z' , 'R' , 'B' , 'R' , 'Wild'  , 'E'],['U', 'N']]

        self.word_list = self.load_words()

        self.collective_turn = 0

        self.player_turn = 0

        self.board = sboard()

        self.move_history = []

        self.wilds = []


    def letters(self):

        """
        Return list of tiles that are still available
        """
        
        l = []
        for tile in self.letter_count.keys():

            for i in range(self.letter_count[tile]):

                l.append(tile)

        return l


    def generate_player_hands(self, player_hands):

        """
        Randomly pick letters from the bag and assign to each player

        Return the player hands as a list 
        """

        available_letters = self.letters()

        for i in range(self.n_players):
            
            if (len(player_hands) != self.n_players):
                player_hands.append([])

            n = 7 - len(player_hands[i])

            if (n != 0):
                
                for j in range(n):
                    
                    while True:

                        # randomly pick a letter from the bag
                        letter = random.choice(available_letters)

                        # check whether the bag still has the letter 
                        # if it does not have the letter, repeat this process
                        if (self.letter_count[letter] != 0):
                            player_hands[i].append(letter)
                            self.letter_count[letter] -= 1
                            break

                        else:
                            available_letters.remove(letter)
                    
        return player_hands
 

    def update_hands(self):

        """
        Update current player hands
        """

        self.player_hands = self.generate_player_hands(self.player_hands)


    def get_n_players(self):

        """
        Prompt user for integer input that is between 2 and 4 which 
        represents the number of players in Scrabble game.
        """
        
        toggle = False
        
        # prompt user for input
        if toggle:
            while True:

                user_input = input("Number of Players: ")
                try: 
                    if 1 < int(user_input) <= 4:
                        user_input = int(user_input)
                        break
                    else:
                        user_input = input("Number of Players: ")

                except ValueError:
                    user_input = input("Number of Players: ")

        # set the number of players at the default number (2)
        else:
            user_input = 2

        for i in range(user_input):
            self.player_points.append(0)

        return user_input


    def load_words(self):

        """
        Load in list of words from "words.txt" 

        Words (string and uppercased) are valid in the game of Scrabble

        The list of words that are valid can be changed by 
        changing the "words.txt" file
        """
        
        f = open(WORDLIST_FILENAME, "r", 1)

        word_list = []
        for line in f:
            word_list.append(line.strip())

        return word_list
    

    def update_player_turn(self):
        """
        Update current player turn to the next
        """
        
        if (self.player_turn + 1 > self.n_players - 1):
            self.collective_turn += 1
            self.player_turn = 0
        else:
            self.player_turn += 1


    def print_hands(self):

        """
        Print out every hand 
        """

        for i in range(len(self.player_hands)):

            hand = self.player_hands[i]
            final = []
            final.append(f"Player {i + 1}")
            final.append(self.player_points[i])

            for tile in hand:
                
                if tile == "Wild":
                    final.append("  ")
                
                else:
                    final.append(tile)

            print(tabulate.tabulate([final], tablefmt="grid"))
        

    def wild_tiles(self):
        """
        Return list of coordinates of wild tiles
        """
        l = []

        for wild in self.wilds:
            l.append(wild[0])

        return l


    def calculate_score(self, word_data):

        """
        Given the coordinates of the word, calculate the points score 
        by referring to letter values and premium tiles
        """

        score = 0
        multiplier = 1
        # row 
        if abs(word_data.p1[0] - word_data.p2[0]) == 0:
            
            
            # if 'DL' or 'TL',  multiply tile value by 2 or 3
            # if 'DW' or 'TW', multiply word value by 2 or 3
            n = 0
            i = word_data.p1[0]
            for j in range(word_data.p1[1] -1, word_data.p2[1]-2):
                
                # print(self.wild_tiles())
                if (i,j) not in self.wild_tiles():

                    premium = self.board.premium_squares_board[i][j]
                    if premium == "TL" or premium == "DL":
                        score += self.letter_values[word_data.word[n]] * self.board.premium_squares_multipliers[premium]
                    
                    elif premium == "TW":
                        multiplier = 3

                    elif premium == "DW":
                        multiplier = 2

                    elif premium == '':
                        score += self.letter_values[word_data.word[n]]

                n += 1
            
            

        # column
        elif abs(word_data.p1[1]- word_data.p2[1]) == 0:

            n = 0
            j = word_data.p1[1] 
            
            for i in range(word_data.p1[0]-1, word_data.p2[0] - 2):
                
                if (i,j) not in self.wild_tiles():

                    premium = self.board.premium_squares_board[i][j]
                    if premium == "TL" or premium == "DL":
                        score += self.letter_values[word_data.word[n]] * self.board.premium_squares_multipliers[premium]
                    
                    elif premium == "TW":
                        multiplier = 3

                    elif premium == "DW":
                        multiplier = 2

                    elif premium == '':
                        score += self.letter_values[word_data.word[n]]

                n += 1
            
        # not a bingo
        if len(word_data.word) != 7:
            return score * multiplier
        # bingo, add 50 points
        else:
            return (score * multiplier) + 50
        
                  
    def exchange_tiles(self, tiles_to_exchange):

        """
        Given a list of tiles to exchange, exchange the tiles for new tiles
        """
        
        available_letters = self.letters()

        if len(available_letters) == 0:
            print("No more tiles to be exchanged")

        else:
            # randomly pick n tiles from the bag and add it to the player's hand
            for i in range(len(tiles_to_exchange)):

                new_tile = random.choice(available_letters)
                self.player_hands[self.player_turn].append(new_tile)
                self.letter_count[new_tile] -= 1

            # remove the exchanged tiles from player's hand and add back the tiles into bag
            for tile in tiles_to_exchange:

                self.player_hands[self.player_turn].remove(tile)
                self.letter_count[tile] += 1


    def add_history(self, word_data, score, words_formed):

        """"Add the current move to the move history"""
        
        if self.collective_turn + 1 != len(self.move_history):
            self.move_history.append([])

        print(self.move_history)
        self.move_history[-1].append(move(self.player_turn, word_data, score))

        for word in words_formed:

            if word.count_score == True and word_data.word != word.word:
                self.move_history[-1][-1].words_formed.append(word)
        


class sboard:

    def __init__ (self):
        
        self.premium_squares_multipliers = {
            "DL" : 2,
            "TL" : 2,
            "TW" : 3,
            "DW" : 3,
        }

        self.premium_squares_board = [
            ['TW', '', '', 'DL', '', '', '', 'TW', '', '', '', 'DL', '', '', 'TW'],
            ['', 'DW', '', '', '', 'TL', '', '', '', 'TL', '', '', '', 'DW', ''],
            ['', '', 'DW', '', '', '', 'DL', '', 'DL', '', '', '', 'DW', '', ''],
            ['DL', '', '', 'DW', '', '', '', 'DL', '', '', '', 'DW', '', '', 'DL'],
            ['', '', '', '', 'DW', '', '', '', '', '', 'DW', '', '', '', ''],
            ['', 'TL', '', '', '', 'TL', '', '', '', 'TL', '', '', '', 'TL', ''],
            ['', '', 'DL', '', '', '', 'DL', '', 'DL', '', '', '', 'DL', '', ''],
            ['TW', '', '', 'DL', '', '', '', '', '', '', '', 'DL', '', '', 'TW'],
            ['', '', 'DL', '', '', '', 'DL', '', 'DL', '', '', '', 'DL', '', ''],
            ['', 'TL', '', '', '', 'TL', '', '', '', 'TL', '', '', '', 'TL', ''],
            ['', '', '', '', 'DW', '', '', '', '', '', 'DW', '', '', '', ''],
            ['DL', '', '', 'DW', '', '', '', 'DL', '', '', '', 'DW', '', '', 'DL'],
            ['', '', 'DW', '', '', '', 'DL', '', 'DL', '', '', '', 'DW', '', ''],
            ['', 'DW', '', '', '', 'TL', '', '', '', 'TL', '', '', '', 'DW', ''],
            ['TW', '', '', 'DL', '', '', '', 'TW', '', '', '', 'DL', '', '', 'TW'],
        ]

        self.state = self.generate_board()


    def generate_board(self):

        """
        Generate 15 x 15 scrabble board where each square has no letters 
        """

        board = []

        for i in range(15):
            row = []
            for j in range(15):
                row.append("")

            board.append(row)

        # # print the 15x15 board
        # for i in board:
        #     print(i)

        return board
    

    def print_premium_squares(self):

        """
        Print out the board with corresponding premium squares
        """

        for i in self.premium_squares_board:
            for j in i:
                if j == '':
                    print("  ",end="  ")
                else:
                    print(f"{j}",end="  ")

            print("\n")


    def print_board(self):

        """
        Print out the current state of board
        """

        # setting to show the grid index 
        # True : show index   False : turn off index

        toggle = True
        final = []

        for i in range(len(self.state)):

            temp_list = []

            if toggle:
                temp_list.append(i+1)

            for j in range(len(self.state[i])):

                tile = self.state[i][j]

                if (tile == ""):
                    temp_list.append(self.premium_squares_board[i][j])
                else:
                    temp_list.append(tile)

            
            final.append(temp_list)

        if toggle:
            print(tabulate.tabulate(final, headers=NUMBERS, tablefmt='grid'))
        else:
            print(tabulate.tabulate(final, tablefmt='grid'))


    def place_tile(self, p1, p2, word):

            """
            Place down the word starting from p1 to p2
            """

            n = 0
            for i in range(int(p1[0])-1, int(p2[0])):

                for j in range(int(p1[1])-1, int(p2[1])):
                    
                    # print(i,j)
                    self.state[i][j] = word[n].upper()
                    n += 1


class word_data:

    def __init__(self,p1, p2, word, count_score):
        self.p1 = p1
        self.p2 = p2
        self.word = word
        self.count_score = count_score

class move:

    def __init__ (self, player, data, score):
        
        self.player = player
        self.data = data
        self.score = score
        self.words_formed = []
        

if __name__ == "__main__":
    main()