import pygame
from network import Network
import pickle
from config_loader import client_settings
import random
import time
import game

pygame.init()
pygame.font.init()

info = pygame.display.Info() # You have to call this before pygame.display.set_mode()
screen_width,screen_height = 720, 720#info.current_w,info.current_h
print(screen_width,screen_height)
grid_size = 40 #automate the process of picking this number so it perfectly fits
grid_height = round(screen_height/grid_size)
grid_width = round(screen_width/grid_size)
width, height = grid_size*grid_width, grid_size*grid_height
print(grid_width,grid_height)
surface = pygame.display.set_mode((screen_width, screen_height))#pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Client")

def main():
    run = True
    paused = False
    n = Network()
    player = int(n.getP())
    print("You are player", player)

    wait_for_other_player(n)

    SONG_END = pygame.USEREVENT + 1

    pygame.mixer.music.set_endevent(SONG_END)
    pygame.mixer.music.load('intro.ogg')
    pygame.mixer.music.play()
    pygame.mixer.music.set_volume(0.01) # lower the musics volume


    clock = pygame.time.Clock()
    while run:
        clock.tick(60)
        try:
            game = n.send("get") # Get position updates and world updates
            print("Received game data")
        except:
            run = False
            print("Couldn't get game")
            break

        # game = n.send("reset")
        # if game.bothWent():

        # update screen
        update_screen(game)

        if game.winner: # Show winner
            render_text_with_outline(360, 360, game.winner['name'], game.winner['colour'], (0,0,0), 120)
            pygame.display.update()
            time.sleep(2)
            n.send("reset")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            elif event.type == SONG_END:
                pygame.mixer.music.load('song.ogg')
                pygame.mixer.music.play(-1)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    break
                if event.key == pygame.K_SPACE: # Only affects the music
                    paused = not paused
                    if paused:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
                move = get_move(event)
                if valid_move(move) and game.connected():
                    n.send("move "+str(move))


        # if game_over():
        #     init(start_food_amount)

# player = {player_id,name,pos} # maybe score and other stuff like hp later
def update_screen(game):
    surface.fill((255,255,255)) # Blank the screen with white
    draw_grid_lines() # Draw the grid first

    for (cell_x,cell_y), (player_id, colour, moves) in game.history.items(): # draw all the history
        #print((cell_x,cell_y), (player_id, colour, moves))
        fill_cell(cell_x,cell_y,colour)

    for (cell_x,cell_y), (value, colour) in game.grid.items(): # draw all cells
        if value == 1: # Alive?
            fill_cell(cell_x,cell_y,colour)
            half_fill_cell(cell_x,cell_y,colour,0.4)

    for player in game.players: # Draw each player
        player_id = player['id']
        cell_x,cell_y = player['pos']
        colour = player['colour'] #(255,0,0)
        fill_cell(cell_x,cell_y,colour)
        half_fill_cell(cell_x,cell_y,colour,1.6)

    draw_text(game)

    pygame.display.update()

def draw_text(game):
    player_1_name = str(game.players[0]['name'])
    player_2_name = str(game.players[1]['name'])

    player_1_moves = str(game.players[0]['moves'])
    player_2_moves = str(game.players[1]['moves'])

    player_1_score = str(game.players[0]['score'])
    player_2_score = str(game.players[1]['score'])

    player_1_colour = game.players[0]['colour']
    player_2_colour = game.players[1]['colour']

    render_text_with_outline(160, 40, player_1_name, player_1_colour, (0,0,0), 60)
    render_text_with_outline(160-60, 110, player_1_moves, player_1_colour, (0,0,0), 60)
    render_text_with_outline(160+60, 110, player_1_score, player_1_colour, (0,0,0), 60)

    render_text_with_outline(560, 40, player_2_name, player_2_colour, (0,0,0), 60)
    render_text_with_outline(560-60, 110, player_2_moves, player_2_colour, (0,0,0), 60)
    render_text_with_outline(560+60, 110, player_2_score, player_2_colour, (0,0,0), 60)

def render_text(x, y, string, colour, size):
    font = pygame.font.Font("impact.ttf", size)
    text = font.render(string, True, colour)
    #text.set_alpha(30)
    textbox = text.get_rect()
    textbox.center = (x, y)
    surface.blit(text, textbox)

def render_text_with_outline(x, y, string, colour, outline_colour, size):
    # Hacky Outline
    render_text(x+2, y-2, string, outline_colour, size)
    render_text(x-2, y+2, string, outline_colour, size)
    render_text(x-2, y-2, string, outline_colour, size)
    render_text(x+2, y+2, string, outline_colour, size)

    # Fill colour
    render_text(x, y, string, colour, size)

def draw_grid_lines(): #optimise pls, render this only once
    for x in range(grid_width):
        grid_colour = (0,0,0)
        start_pos = (x*grid_size,0)
        end_pos = (x*grid_size,height)
        line_width = 1
        pygame.draw.line(surface,grid_colour,start_pos,end_pos,line_width)

    for y in range(grid_height):
        grid_colour = (0,0,0)
        start_pos = (0,y*grid_size)
        end_pos = (width,y*grid_size)
        line_width = 1
        pygame.draw.line(surface,grid_colour,start_pos,end_pos,line_width)

def fill_cell(x,y,colour):
    x, y = x*grid_size, y*grid_size
    pygame.draw.rect(surface, colour, pygame.Rect(x, y, grid_size, grid_size))

def half_fill_cell(x,y,colour,gradient_multiplier):
    x, y = x*grid_size, y*grid_size
    colour = tuple(max(0, min(value*gradient_multiplier, 255)) for value in colour) # use the gradient multiplier and then bound it between 0 and 255
    square_width = grid_size*0.75
    square_height = grid_size*0.75
    width_difference = grid_size - square_width
    height_difference = grid_size - square_height
    x_offset = width_difference/2
    y_offset = height_difference/2
    pygame.draw.rect(surface, colour, pygame.Rect(x+x_offset, y+y_offset, square_width, square_height))


def valid_move(move):
    return move >= 0 and move <= 3

def get_move(event):
    if event.key == pygame.K_w or event.key == pygame.K_UP:
        return 0
    if event.key == pygame.K_a or event.key == pygame.K_LEFT:
        return 1
    if event.key == pygame.K_s or event.key == pygame.K_DOWN:
        return 2
    if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
        return 3
    else: # Invalid key for now
        return -1

def menu_screen():
    run = True
    clock = pygame.time.Clock()

    while run:
        clock.tick(60)
        surface.fill((128, 128, 128))

        render_text_with_outline(360, 360, "Click to Play!", (255,0,0), (0,0,0), 60)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                run = False

    main() # Start the game

def wait_for_other_player(n):
    run_name = True
    clock = pygame.time.Clock()

    response = n.send(f"name={client_settings['display_name']}")#_{random.randint(0,1000)}")
    while run_name:
        try:
            game = n.send("get")
        except Exception as e:
            run_name = False
            print("Couldn't get game in name section")
            print(e)
            break
        if game.both_named():
            print("both players named")
            run_name = False
            break

        clock.tick(60)
        surface.fill((128, 128, 128))

        render_text_with_outline(360, 360, "Waiting for other player!", (255,0,0), (0,0,0), 60)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run_name = False

while True:
    menu_screen()
