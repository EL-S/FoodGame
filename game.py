from random import seed, randint, getstate, randrange, random
import sys

class Game:
    def __init__(self, id):
        self.p1_name_went = False
        self.p2_name_went = False
        self.ready = False
        self.id = id
        self.players = []
        self.grid_width = 18
        self.grid_height = 18
        self.spawn_position = [self.grid_width//2,self.grid_height//2]
        self.grid = {}
        self.history = {}
        self.seed = randrange(sys.maxsize)
        self.starting_moves = 20
        self.starting_food = 50
        self.winner = None


        seed(self.seed) # same level every time # 152214886
        total_food = self.starting_food
        while total_food > 0:
            x,y = randint(0,self.grid_width-1),randint(0,self.grid_height-1)
            if (x,y) not in self.grid:
                self.grid[(x,y)] = (1,(randint(0,255),randint(0,255),randint(0,255))) # (0,127,127))
                total_food -= 1

    def play(self, player_id, move):
        #self.moves[player] = move
        print(f"moving player {player_id} {move}")
        for index, player in enumerate(self.players):
            if player['id'] == player_id:
                if self.players[index]['moves'] > 0:
                    pos = self.players[index]['pos']
                    self.add_history(player['id'],player['colour'],player['moves'],pos.copy())
                    if move == 0:
                        pos[1] -= 1
                    elif move == 1:
                        pos[0] -= 1
                    elif move == 2:
                        pos[1] += 1
                    elif move == 3:
                        pos[0] += 1
                    self.players[index]['pos'] = self.wrap_position(pos)
                    self.players[index]['moves'] -= 1
                    print("Moves left",self.players[index]['moves'])
                    self.check_food(player['id'])
                else:
                    print("Out of moves!")
                break

        if self.game_over():
            print("Gameover")
            #  show who won, wait a few seconds then reset

            self.winner = self.players[0] if self.players[0]['score'] > self.players[1]['score'] else self.players[1]
            #self.reset()

        # maybe useful if I make it turnbased
        # if player == 0:
        #     self.p1Went = True
        # else:
        #     self.p2Went = True

    def check_food(self, player_id):
        try:
            cell_x,cell_y = self.players[player_id]['pos']
            if self.grid[(cell_x,cell_y)][0] == int(1):
                print("Gained move!")
                print("Moves left",self.players[player_id]['moves'])
                self.players[player_id]['moves'] += 3
                self.players[player_id]['score'] += 1
                del self.grid[(cell_x,cell_y)]
        except:
            pass

    def add_history(self, player_id, player_colour, moves, pos):
        # player['id'],player['colour'],player['moves'],pos.copy()
        value = self.starting_moves-moves
        value = max(0, min(value, self.starting_moves)) # keep the value in bounds

        colour_change = (128/self.starting_moves)

        player_r = player_colour[0]
        player_g = player_colour[1]
        player_b = player_colour[2]

        sign_1 = 1 if player_r > 128 else -1
        sign_2 = 1 if player_g > 128 else -1
        sign_3 = 1 if player_b > 128 else -1

        multiplier_1 = player_r/255
        multiplier_2 = player_g/255
        multiplier_3 = player_b/255

        colour_val = (round(max(0, min(128+(value*colour_change*sign_1*multiplier_1), 255))),
                      round(max(0, min(128+(value*colour_change*sign_2*multiplier_2), 255))),
                      round(max(0, min(128+(value*colour_change*sign_3*multiplier_3), 255))))

        self.history[tuple(pos)] = [player_id,colour_val,moves]

    def create_player(self, player, name):
        # self.names[player] = name
        try:
            colour_r = randint(0,255)
            colour_g = randint(0,255)
            colour_b = randint(0,255)
            colour = (colour_r,colour_g,colour_b)
            self.players.append({"id":player,"name":name,"pos":self.spawn_position.copy(),"colour":colour,"moves":self.starting_moves,"score":0})
        except Exception as e:
            print(e)
        if player == 0:
            self.p1_name_went = True
        else:
            self.p2_name_went = True

    def wrap_position(self, pos):
        if int(pos[0]) >= self.grid_width:
            pos[0] = 0
        elif int(pos[0]) < 0:
            pos[0] = self.grid_width-1
        if int(pos[1]) >= self.grid_height:
            pos[1] = 0
        elif int(pos[1]) < 0:
            pos[1] = self.grid_height-1
        return pos

    def connected(self):
        return self.ready

    def both_named(self):
        return self.p1_name_went and self.p2_name_went

    def reset(self):
        self.winner = None
        self.grid = {}
        self.history = {}
        self.seed = randrange(sys.maxsize)
        self.starting_moves = 20
        self.starting_food = 50

        seed(self.seed) # same level every time # 152214886
        total_food = self.starting_food
        while total_food > 0:
            x,y = randint(0,self.grid_width-1),randint(0,self.grid_height-1)
            if (x,y) not in self.grid:
                self.grid[(x,y)] = (1,(randint(0,255),randint(0,255),randint(0,255))) # (0,127,127))
                total_food -= 1

        for index, player in enumerate(self.players):
            self.players[index]['pos'] = self.spawn_position.copy()
            self.players[index]['moves'] = self.starting_moves
            self.players[index]['score'] = 0

    def game_over(self):
        # Check if everyone ran out of moves
        total_moves = 0
        for player in self.players:
            total_moves += player['moves']
        if total_moves < 1:
            return True

        # Check if there is no food left
        for location, value in self.grid.items():
            if value:
                break
        else:
            return True

    # def get_player_name(self, p):
    #     """
    #     :param p: [0,1]
    #     :return: Name
    #     """
    #     return self.names[p]

    # def get_player_move(self, p):
    #     """
    #     :param p: [0,1]
    #     :return: Move
    #     """
    #     return self.moves[p]

    # def bothWent(self):
    #     return self.p1Went and self.p2Went

    # def winner(self):
    #
    #     p1 = self.moves[0].upper()[0]
    #     p2 = self.moves[1].upper()[0]
    #
    #     winner = -1
    #     if p1 == "R" and p2 == "S":
    #         winner = 0
    #     elif p1 == "S" and p2 == "R":
    #         winner = 1
    #     elif p1 == "P" and p2 == "R":
    #         winner = 0
    #     elif p1 == "R" and p2 == "P":
    #         winner = 1
    #     elif p1 == "S" and p2 == "P":
    #         winner = 0
    #     elif p1 == "P" and p2 == "S":
    #         winner = 1
    #
    #     # reset moves
    #     # self.moves = [None, None]
    #
    #     return winner

    # def resetWent(self):
    #     self.p1Went = False
    #     self.p2Went = False
