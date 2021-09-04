import pygame
from network import Network
import pickle
from config_loader import client_settings, rewrite_client_config
import random
import time
import datetime
import game
import sys

pygame.init()
pygame.font.init()

program_icon = pygame.image.load('icon.png')
pygame.display.set_icon(program_icon)

info = pygame.display.Info() # You have to call this before pygame.display.set_mode()
screen_width,screen_height = 720, 720#info.current_w,info.current_h
print(screen_width,screen_height)
grid_size = 40 #automate the process of picking this number so it perfectly fits
grid_height = round(screen_height/grid_size)
grid_width = round(screen_width/grid_size)
width, height = grid_size*grid_width, grid_size*grid_height
print(grid_width,grid_height)
surface = pygame.display.set_mode((screen_width, screen_height))#pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("TheNums")

volume_slider_duration = 1 # 1 second
volume_last_changed = None
desired_volume = None

def main():
    global desired_volume, your_player_id
    running = True
    paused = False
    show_ui = True

    n = Network()
    try:
        response = n.getP()
        if response:
            your_player_id = int(response)
        else:
            print("No connection to the server.")
            return
    except Exception as e:
        print(e,"in main menu")
        return
    print("You are player", your_player_id)

    wait_for_other_player(n)

    SONG_END = pygame.USEREVENT + 1

    # TODO: Move audio when title screen is updated
    pygame.mixer.music.set_endevent(SONG_END)
    pygame.mixer.music.load('intro.ogg')
    pygame.mixer.music.play()
    pygame.mixer.music.set_volume(float(client_settings['volume'])) # set the musics volume

    desired_volume = pygame.mixer.music.get_volume()

    clock = pygame.time.Clock()

    max_retries = 10 # If a connection fails, retry 10 times
    retries = 0

    while running:
        clock.tick(60)
        try:
            game = n.send("get") # Get position updates and world updates
            if not game:
                raise Exception("Empty game object due to closed socket")
        except Exception as e:
            print("Couldn't get game",e)
            if retries >= max_retries:
                running = False
                break
            else:
                retries += 1
                continue

        if running:
            retries = 0

        # TODO: Remember the volume in the config
        # TODO: Create a config if it doesn't exist
        # TODO: Remove all the unused stuff and magic numbers
        # TODO: Store the music and font inside the EXE
        # TODO: Main menu is a bot playing the game
        # TODO: Send screensize to server so players can negotiate a common gridsize
        # TODO: Implement winner screen properly, players can spam input currently

        if desired_volume is not None:
            if desired_volume != pygame.mixer.music.get_volume():
                smooth_change_volume()

        # update screen
        update_screen(game,show_ui)

        if game.winner: # Show winner
            render_text_with_outline(360, 360, game.winner['name'], game.winner['colour'], (0,0,0), 120)
            pygame.display.update()
            time.sleep(2)
            n.send("reset")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                running = False
                sys.exit()
                break
            elif event.type == SONG_END:
                pygame.mixer.music.load('song.ogg')
                pygame.mixer.music.play(-1)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    running = False
                    sys.exit()
                    break
                if event.key == pygame.K_SPACE: # Only affects the music
                    paused = not paused
                    if paused:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
                if event.key == pygame.K_TAB: # Only affects the top UI
                    show_ui = not show_ui
                move = get_move(event)
                if valid_move(move) and game.connected():
                    n.send("move "+str(move))
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    change_volume(1) # UP
                elif event.button == 5:
                    change_volume(-1) # DOWN

# player = {player_id,name,pos} # maybe score and other stuff like hp later
def update_screen(game,show_ui):
    surface.fill((255,255,255)) # Blank the screen with white

    for (cell_x,cell_y), (player_id, colour, moves) in game.history.items(): # draw all the history
        #print((cell_x,cell_y), (player_id, colour, moves))
        fill_cell(cell_x,cell_y,colour)

    for (cell_x,cell_y), (value, colour) in game.grid.items(): # draw all cells
        if value == 1: # Alive?
            fill_cell(cell_x,cell_y,colour)
            half_fill_cell(cell_x,cell_y,colour,1.6,True)

    for player in game.players: # Draw each player
        player_id = player['id']
        cell_x,cell_y = player['pos']
        colour = player['colour'] #(255,0,0)
        fill_cell(cell_x,cell_y,colour)
        if player['id'] == your_player_id:
            triangle_fill_cell(cell_x,cell_y,colour,1.1,True)
        else:
            circle_fill_cell(cell_x,cell_y,colour,1.1,True)
        #half_fill_cell(cell_x,cell_y,colour,1.1,True)

    draw_grid_lines() # Draw the grid first

    if show_ui:
        draw_text(game)

    # Draw volume slider
    if volume_last_changed:
        if (volume_last_changed+datetime.timedelta(0,volume_slider_duration)) > datetime.datetime.now(): # Still during the time period
            draw_volume_slider()

    pygame.display.update()

def draw_volume_slider():
    percent_per_square = 10
    volume = pygame.mixer.music.get_volume()
    total_squares = 100/percent_per_square
    cell_x = grid_width-1
    start_y = round((grid_height/2)+((total_squares)/2)-1)
    squares = round((volume*100)/percent_per_square)
    colour = (245,245,245)
    for y_offset in range(squares,round(total_squares)): # Draw inactive squares
        x = cell_x*grid_size
        y = (start_y-y_offset)*grid_size
        pygame.draw.rect(surface, colour, pygame.Rect(x, y, grid_size, grid_size))
    colour = (230,230,230)
    for y_offset in range(0,squares): # Draw active squares
        x = cell_x*grid_size
        y = (start_y-y_offset)*grid_size
        pygame.draw.rect(surface, colour, pygame.Rect(x, y, grid_size, grid_size))

# Transition volume slowly to prevent clicking and cracking noise
def smooth_change_volume(step_size=0.01):
    global desired_volume
    new_volume = 0
    volume = pygame.mixer.music.get_volume()
    if volume > desired_volume:
        new_volume = volume-step_size
    elif volume < desired_volume:
        new_volume = volume+step_size
    new_volume = max(0, min(new_volume, 1))
    pygame.mixer.music.set_volume(new_volume)
    volume = pygame.mixer.music.get_volume()
    if abs(desired_volume-volume) < 0.01: # Finished adjusting the volume
        desired_volume = volume
        client_settings['volume'] = desired_volume
        rewrite_client_config(client_settings)

def change_volume(direction, amount=0.05):
    global desired_volume,volume_last_changed
    if (desired_volume):
        volume = desired_volume
    else:
        volume = pygame.mixer.music.get_volume()
    volume += amount*direction
    volume = max(0, min(volume, 1))
    desired_volume = volume
    volume_last_changed = datetime.datetime.now()

# def old_change_volume(direction, amount=0.05)
#     global volume_last_changed
#     volume = pygame.mixer.music.get_volume()
#     volume += amount*direction
#     volume = max(0, min(volume, 1))
#     desired_volume = volume
#     pygame.mixer.music.set_volume(volume)
#     volume_last_changed = datetime.datetime.now()

def mix_colours(colour_1, colour_2):
    red = round(max(0, min((colour_1[0] + colour_2[0]) / 2, 255)))
    green = round(max(0, min((colour_1[1] + colour_2[1]) / 2, 255)))
    blue = round(max(0, min((colour_1[2] + colour_2[2]) / 2, 255)))

    colour = (red, green, blue)
    return colour

def draw_text(game):
    max_font_size = 60

    player_x_distance_offset = round((screen_width)/(game.player_count+1))
    font_size = round(120/game.player_count)


    if font_size > max_font_size:
        font_size = max_font_size

    player_y_distance_offset = round((font_size/2) + (font_size/6))
    x_offset_offset = font_size # TODO: Make a better name for this variable


    line_height = round(font_size + (font_size/6))

    for index, player in enumerate(game.players):
        x_offset = player_x_distance_offset + player_x_distance_offset*(index)

        y_offset = player_y_distance_offset

        player_name = str(player['name'])
        player_moves = str(player['moves'])
        player_score = str(player['score'])
        player_colour = player['colour']

        gradient_multiplier = 1.1
        outline_colour_faded = tuple(max(0, min(value*gradient_multiplier, 255)) for value in player_colour)

        # TODO: Make text position and size smart and based on length of name

        if game.game_mode == 1 and game.active_player == index:
            outline_colour_faded = (0, 0, 0)
            font_size_multiplier = 1.1
        else:
            font_size_multiplier = 1.0

        if player['id'] == your_player_id:
            player_name = "You"

        actual_font_size = round(font_size * font_size_multiplier)

        render_text_with_outline(x_offset, y_offset, player_name, player_colour, outline_colour_faded, actual_font_size)
        render_text_with_outline(x_offset-x_offset_offset, y_offset+line_height, player_moves, player_colour, outline_colour_faded, actual_font_size)
        render_text_with_outline(x_offset+x_offset_offset, y_offset+line_height, player_score, player_colour, outline_colour_faded, actual_font_size)

def render_text(x, y, string, colour, size):
    font = pygame.font.Font("impact.ttf", size)
    text = font.render(string, True, colour)
    #text.set_alpha(30)
    textbox = text.get_rect()
    textbox.center = (x, y)
    surface.blit(text, textbox)

def render_text_with_outline(x, y, string, colour, outline_colour, size):
    # Hacky Outline
    outline_width = size/15
    outline_offset = outline_width/2
    render_text(x+outline_offset, y-outline_offset, string, outline_colour, size)
    render_text(x-outline_offset, y+outline_offset, string, outline_colour, size)
    render_text(x-outline_offset, y-outline_offset, string, outline_colour, size)
    render_text(x+outline_offset, y+outline_offset, string, outline_colour, size)

    # Fill outline bad, makes it look 3D
    #render_text(x, y, string, outline_colour, size+1)

    # Fill colour
    render_text(x, y, string, colour, size)

def draw_grid_lines(): #optimise pls, render this only once
    for x in range(grid_width):
        grid_colour = (215,215,215)
        start_pos = (x*grid_size,0)
        end_pos = (x*grid_size,height)
        line_width = 1
        pygame.draw.line(surface,grid_colour,start_pos,end_pos,line_width)

    for y in range(grid_height):
        grid_colour = (215,215,215)
        start_pos = (0,y*grid_size)
        end_pos = (width,y*grid_size)
        line_width = 1
        pygame.draw.line(surface,grid_colour,start_pos,end_pos,line_width)

def fill_cell(x,y,colour):
    x, y = x*grid_size, y*grid_size
    pygame.draw.rect(surface, colour, pygame.Rect(x, y, grid_size, grid_size))

def half_fill_cell(x,y,colour,gradient_multiplier,blend_colours=False):
    x, y = x*grid_size, y*grid_size

    if blend_colours:
        faded_colour = tuple(max(0, min(value*gradient_multiplier, 255)) for value in colour)
        middle_colour = mix_colours(colour,faded_colour)
    else:
        middle_colour = colour

    square_width = grid_size*0.75
    square_height = grid_size*0.75
    width_difference = grid_size - square_width
    height_difference = grid_size - square_height
    x_offset = width_difference/2
    y_offset = height_difference/2
    pygame.draw.rect(surface, middle_colour, pygame.Rect(x+x_offset, y+y_offset, square_width, square_height))

def circle_fill_cell(x,y,colour,gradient_multiplier,blend_colours=False):
    x, y = x*grid_size, y*grid_size

    if blend_colours:
        faded_colour = tuple(max(0, min(value*gradient_multiplier, 255)) for value in colour)
        middle_colour = mix_colours(colour,faded_colour)
    else:
        middle_colour = colour

    circle_radius = (grid_size/2)*0.75
    x_offset = (grid_size/2)
    y_offset = (grid_size/2)

    pygame.draw.circle(surface, middle_colour, (x+x_offset,y+y_offset), circle_radius)

def triangle_fill_cell(x,y,colour,gradient_multiplier,blend_colours=False):
    x, y = x*grid_size, y*grid_size

    if blend_colours:
        faded_colour = tuple(max(0, min(value*gradient_multiplier, 255)) for value in colour)
        middle_colour = mix_colours(colour,faded_colour)
    else:
        middle_colour = colour

    circle_radius = (grid_size/2)*0.75
    x_offset = (grid_size/2)
    y_offset = (grid_size/2)

    middle_x = x+x_offset
    top_y = y
    bottom_y = y+grid_size
    left_x = x
    right_x = x+grid_size
    #middle_y = y+x_offset

    # TODO: Make the triangle size make sense and accessible from outside the function
    triangle_size = 7

    points = [(middle_x, top_y+grid_size/triangle_size), (right_x-grid_size/triangle_size, bottom_y-grid_size/triangle_size), (left_x+grid_size/triangle_size, bottom_y-grid_size/triangle_size)]
    pygame.draw.polygon(surface, middle_colour, points)

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
    running = True
    clock = pygame.time.Clock()

    while running:
        clock.tick(60)
        surface.fill((128, 128, 128))

        render_text_with_outline(360, 360, "Click to Play!", (255,0,0), (0,0,0), 60)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                running = False

    main() # Start the game

def wait_for_other_player(n):
    running = True
    clock = pygame.time.Clock()

    response = n.send(f"name={client_settings['display_name']}")#_{random.randint(0,1000)}")
    while running:
        try:
            game = n.send("get")
        except Exception as e:
            running = False
            print("Couldn't get game in name section",e)
            break
        if game.connected():
            print("game is ready")
            running = False
            break

        clock.tick(60)
        surface.fill((128, 128, 128))

        render_text_with_outline(360, 360, "Waiting for other player!", (255,0,0), (0,0,0), 60)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                running = False

while True:
    menu_screen()
