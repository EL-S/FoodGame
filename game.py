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
        self.populate_food()

    def populate_food(self):
        seed(self.seed) # same level every time # 152214886
        total_food = self.starting_food
        while total_food > 0:
            x,y = randint(0,self.grid_width-1),randint(0,self.grid_height-1)
            if (x,y) not in self.grid:
                self.grid[(x,y)] = (1,self.gen_colour((255,255,255))) # (0,127,127))
                total_food -= 1

    def gen_colour(self, mix=None):
        red = randint(0,255)
        green = randint(0,255)
        blue = randint(0,255)

        if (mix != None):
            red, green, blue = self.mix_colours((red,green,blue),(255,255,255))

        colour = (red, green, blue)
        return colour

    def mix_colours(self, colour_1, colour_2):
        red = round(max(0, min((colour_1[0] + colour_2[0]) / 2, 255)))
        green = round(max(0, min((colour_1[1] + colour_2[1]) / 2, 255)))
        blue = round(max(0, min((colour_1[2] + colour_2[2]) / 2, 255)))

        colour = (red, green, blue)
        return colour

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

    def round_bound_colour(self, colour_channel):
        return round(max(0, min(colour_channel, 255)))

    def add_history(self, player_id, player_colour, moves, pos):
        # player['id'],player['colour'],player['moves'],pos.copy()
        value = self.starting_moves-moves
        value = max(0, min(value, self.starting_moves)) # keep the value in bounds
        percentage = value/self.starting_moves
        #colour_change = (128/self.starting_moves)

        color1 = player_colour
        color2 = (255, 255, 255)

        colour_r = (percentage * color1[0]) + ((1 - percentage) * color2[0])
        colour_g = (percentage * color1[1]) + ((1 - percentage) * color2[1])
        colour_b = (percentage * color1[2]) + ((1 - percentage) * color2[2])

        colour_val = (self.round_bound_colour(colour_r), self.round_bound_colour(colour_g), self.round_bound_colour(colour_b))

        #player_r = player_colour[0]-(value*colour_change)
        #player_g = player_colour[1]-(value*colour_change)
        #player_b = player_colour[2]-(value*colour_change)
        #player_other = (player_r,player_g,player_b)

        #origin_r, origin_g, origin_b = (255,255,255)
        #colour_val = self.mix_colours(player_other,(255,255,255))

        self.history[tuple(pos)] = [player_id,colour_val,moves]

    def create_player(self, player, name):
        # self.names[player] = name
        try:
            colour = self.gen_colour((255,255,255))
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

        self.populate_food()

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
