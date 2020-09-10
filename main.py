import pygame
from random import seed, randint, getstate, randrange
import math
import time
import sys

#train a nn to find the best path

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
    global grid_size, grid_width, grid_height
    x, y = x*grid_size, y*grid_size
    pygame.draw.rect(surface, colour, pygame.Rect(x, y, grid_size, grid_size))

def fill_grid():
    global nearest_food
    surface.fill((255,255,255))
    draw_history() 
    draw_player()
    nearest_food = get_nearest_food()
    draw_food()

def draw_history():
    global history
    
    for location, colour in history.items():
        cell_x, cell_y = location
        fill_cell(cell_x,cell_y,colour)

def draw_player():
    global moves, player, food, history, grid_width, grid_height, food_move_gain
    
    cell_x = int(player[0])
    cell_y = int(player[1])

    colour = (255,0,0)
    try:
        if grid[(cell_x,cell_y)][0] == int(1):
            food += 1
            moves += food_move_gain
            del grid[(cell_x,cell_y)]
            dead[(cell_x,cell_y)] = (0, 0, 0)
    except:
        pass
    
    fill_cell(cell_x,cell_y,colour)

def draw_food():
    for location, (value, colour) in grid.items():
        if value == 1:
            if nearest_food:
                if nearest_food[-1] == location:
                    colour = (0, 0, 0)
            cell_x,cell_y = location
            fill_cell(cell_x,cell_y,colour)
    if draw_dead:
        for location, colour in dead.items():
            cell_x,cell_y = location
            fill_cell(cell_x,cell_y,colour)

def add_history():
    global history_colour, player, history, moves, original_moves
    value = original_moves-moves
    if value > original_moves:
        value = orginal_moves
    elif value < 0:
        value = 0
    history_colour[0] = 128+(value*colour_change)
    history_colour[1] = 128-(value*colour_change)
    history_colour[2] = 128-(value*colour_change)
    
    for i in range(len(history_colour)):
        if history_colour[i] < 0:
            history_colour[i] = 0
        elif history_colour[i] > 255:
            history_colour[i] = 255

    colour_val = (round(history_colour[0]),round(history_colour[1]),round(history_colour[2]))
    
    loc_pos = (int(player[0]),int(player[1]))
    loc_colour = colour_val

    history[loc_pos] = loc_colour

def wrapping_and_history_update():
    global moves, player, grid_height, grid_width, running
    moves -= 1
    print(moves)
    if int(player[0]) >= grid_width:
        player[0] = 0
    elif int(player[0]) < 0:
        player[0] = grid_width-1
    if int(player[1]) >= grid_height:
        player[1] = 0
    elif int(player[1]) < 0:
        player[1] = grid_height-1
    add_history()
    #print("Moves Remaining: {}".format(moves))
    redraw_scene()
    move_check()

def draw_text():
    global font, text_colour
    # Render the text surface.
    txt_surf = font.render(str(moves), True, text_colour)
    # Create a transparent surface.
    alpha_img = pygame.Surface(txt_surf.get_size(), pygame.SRCALPHA)
    # Fill it with white and the desired alpha value.
    alpha_img.fill((255, 255, 255, 140))
    # Blit the alpha surface onto the text surface and pass BLEND_RGBA_MULT.
    txt_surf.blit(alpha_img, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    text_rect = surface.blit(txt_surf, (38, 45))
    return text_rect

def redraw_scene():
    global player, player_old, last_rect, nearest_food, previous_nearest_food
    fill_grid()
    draw_grid_lines()
    text_rect = draw_text()
    player_rect = [player[0]*grid_size,player[1]*grid_size,grid_size,grid_size]
    player_old_rect = [player_old[0]*grid_size,player_old[1]*grid_size,grid_size,grid_size]
    update_list = [player_rect,player_old_rect,last_rect,text_rect]
    if previous_nearest_food:
        previous_food_rect = [previous_nearest_food[-1][0]*grid_size,previous_nearest_food[-1][1]*grid_size,grid_size,grid_size]
        update_list.append(previous_food_rect)
    if nearest_food:
        nearest_food_rect = [nearest_food[-1][0]*grid_size,nearest_food[-1][1]*grid_size,grid_size,grid_size]
        update_list.append(nearest_food_rect)

    pygame.display.update(update_list)
    
    last_rect = text_rect

def key_check(event):
    global moves, player, player_old
    if event.key == pygame.K_ESCAPE:
        return True
    if event.key == pygame.K_w or event.key == pygame.K_UP:
        player_old = (player[0],player[1])
        player[1] -= 1
        wrapping_and_history_update()
    if move_check():
        return
    if event.key == pygame.K_a or event.key == pygame.K_LEFT:
        player_old = (player[0],player[1])
        player[0] -= 1
        wrapping_and_history_update()
    if move_check():
        return
    if event.key == pygame.K_s or event.key == pygame.K_DOWN:
        player_old = (player[0],player[1])
        player[1] += 1
        wrapping_and_history_update()
    if move_check():
        return
    if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
        player_old = (player[0],player[1])
        player[0] += 1
        wrapping_and_history_update()
    if move_check():
        return

def move_check():
    global moves, running
    if moves <= 0:
        init(start_food_amount)
        return True

def game_over():
    for location, value in grid.items():
        if value:
            break
    else:
        return True

def get_nearest_food():
    global player, grid_width, grid_height, nearest_food, previous_nearest_food
    previous_nearest_food = nearest_food
    nearest_food = None
    for location, value in grid.items():
        if value[0] == 1:
            x_distance = location[0]-player[0]
            y_distance = location[1]-player[1]
            if x_distance > 0:
                # go left
                x_direction = -1
            elif x_distance < 0:
                # go right
                x_direction = 1
            else:
                # stay
                x_direction = 0
            if y_distance > 0:
                # go up
                y_direction = -1
            elif y_distance < 0:
                # go down
                y_direction = 1
            else:
                # stay
                y_direction = 0
            if abs(x_distance) > round(grid_width/2):
                x_distance = grid_width-abs(x_distance)
                x_direction *= -1
            if abs(y_distance) > round(grid_height/2):
                y_distance = grid_height-abs(y_distance)
                y_direction *= -1
            abs_x = abs(x_distance)
            abs_y = abs(y_distance)
            total_distance = abs_x+abs_y
            if not nearest_food:
                nearest_food = [total_distance,x_distance,y_distance,abs_x,abs_y,x_direction,y_direction,location]
            else:
                if total_distance < nearest_food[0]:
                    nearest_food = [total_distance,x_distance,y_distance,abs_x,abs_y,x_direction,y_direction,location]
    return nearest_food

def choose_move():
    global moves, player, player_old, nearest_food
    nearest_food = get_nearest_food()
    if nearest_food:
        if nearest_food[3] > 0 and (nearest_food[3] < nearest_food[4] or nearest_food[4] == 0):
            if nearest_food[-3] > 0:
                player_old = (player[0],player[1])
                player[0] -= 1 # left
            elif nearest_food[-3] < 0:
                player_old = (player[0],player[1])
                player[0] += 1 # right
        elif nearest_food[4] > 0:
            if nearest_food[-2] > 0:
                player_old = (player[0],player[1])
                player[1] -= 1 # up
            elif nearest_food[-2] < 0:
                player_old = (player[0],player[1])
                player[1] += 1 # down
        wrapping_and_history_update()
        move_check()
        #time.sleep(0.1)

def init(starting_food):
    global screen_width, screen_height, grid, history, food, food_move_gain, original_moves, moves, colour_change, history_colour, player, player_old, font, text_colour, last_rect, dead, nearest_food
    seed_gen = randrange(sys.maxsize) 
    print("Seed was:", seed_gen)
    seed(seed_gen) # same level every time # 152214886
    grid = {} #keys are the co ords, values are the type of cell
    history = {}
    dead = {}
    nearest_food = None
    previous_nearest_food = None
    total_food = starting_food
    while total_food > 0:
        x,y = randint(0,grid_width-1),randint(0,grid_height-1)
        if (x,y) not in grid:
            grid[(x,y)] = (1,(randint(0,255),randint(0,255),randint(0,255)))
            total_food -= 1
    food = 0
    food_move_gain = 4
    original_moves = 15
    moves = original_moves
    history_colour = [128.0,128.0,128.0]
    colour_change = (128/moves)
    player = [round(grid_width/2)-1,round(grid_height/2)-1]
    player_old = [0,0]
    font = pygame.font.Font(None, 110)
    text_colour = pygame.Color('black')
    add_history()
    fill_grid()
    draw_grid_lines()
    last_rect = draw_text()
    pygame.display.flip() #first draw
    
pygame.init()
info = pygame.display.Info() # You have to call this before pygame.display.set_mode()
screen_width,screen_height = info.current_w,info.current_h
print(screen_width,screen_height)
grid_size = 40 #automate the process of picking this number so it perfectly fits
grid_height = round(screen_height/grid_size)
grid_width = round(screen_width/grid_size)
width, height = grid_size*grid_width, grid_size*grid_height
print(grid_width,grid_height)
surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

start_food_amount = 82
draw_dead = False

init(start_food_amount)

SONG_END = pygame.USEREVENT + 1

pygame.mixer.music.set_endevent(SONG_END)
pygame.mixer.music.load('intro.ogg')
pygame.mixer.music.play()

bot = True
assisted = False

running = True
paused = False

while running:
    if assisted:
        choose_move()
        time.sleep(0.1)
    if bot and not paused:
        choose_move()
        time.sleep(0.1)
    for event in pygame.event.get():
        if event.type == SONG_END:
            pygame.mixer.music.load('song.ogg')
            pygame.mixer.music.play(-1)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
                break
            if event.key == pygame.K_SPACE:
                paused = not paused
                if paused:
                    pygame.mixer.music.pause()
                else:
                    pygame.mixer.music.unpause()
            if event.key == pygame.K_b:
                assisted = not assisted
                paused = not assisted
                if paused:
                    pygame.mixer.music.pause()
                else:
                    pygame.mixer.music.unpause()
            elif not bot:
                key_check(event)
    if game_over():
        init(start_food_amount)
        #running = False
        

print("Food Collected: {}".format(food))

pygame.quit()
