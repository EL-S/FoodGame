import pygame
from random import randint
import math
import time

#set seed to be the same
#train a nn to find the best path

pygame.init()
info = pygame.display.Info() # You have to call this before pygame.display.set_mode()
screen_width,screen_height = info.current_w,info.current_h
print(screen_width,screen_height)

grid_size = 40 #automate the process of picking this number so it perfectly fits

grid_height = round(screen_height/grid_size)
grid_width = round(screen_width/grid_size)

max_val = 15

#grid = [[randint(0,max_val) for y in range(grid_height)] for x in range(grid_width)]

grid = {} #keys are the co ords, values are the type of cell


history = {}

for x in range(grid_width): #bad but not that bad
    for y in range(grid_height):
        value = randint(0,max_val)
        if value == max_val:
            grid[(x,y)] = 1

width = grid_size*grid_width
height = grid_size*grid_height

surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)

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
    x = x*grid_size
    y = y*grid_size
    pygame.draw.rect(surface, colour, pygame.Rect(x, y, grid_size, grid_size))

def fill_grid():
    
    surface.fill((255,255,255))

    draw_history()
    
    draw_food()    

    draw_player()

def draw_history():
    global history
    
    for location, colour in history.items():
        cell_x = location[0]
        cell_y = location[1]
        fill_cell(cell_x,cell_y,colour)

def draw_player():
    global moves, player, food, history, grid_width, grid_height, food_move_gain
    
    cell_x = int(player[0])
    cell_y = int(player[1])

    colour = (255,0,0)
    try:
        if grid[(cell_x,cell_y)] == int(1):
            food += 1
            moves += food_move_gain
            del grid[(cell_x,cell_y)]
    except:
        pass
    
    fill_cell(cell_x,cell_y,colour)

def draw_food():
    for location, value in grid.items():
        if value == 1:
            colour = (0,128,0)
            cell_x = location[0]
            cell_y = location[1]
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

food = 0

food_move_gain = 4

original_moves = 15

moves = original_moves

history_colour = [128.0,128.0,128.0]

colour_change = (128/moves)

player = [round(grid_width/2)-1,round(grid_height/2)-1]

player_old = [0,0]

add_history()

fill_grid()

draw_grid_lines()

pygame.display.update() #first draw

running = True

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
    
def redraw_scene():
    global player, player_old
    fill_grid()

    draw_grid_lines()
    player_rect = [player[0]*grid_size,player[1]*grid_size,grid_size,grid_size]
    player_old_rect = [player_old[0]*grid_size,player_old[1]*grid_size,grid_size,grid_size]
    pygame.display.update([player_rect,player_old_rect]) #unoptimised yuck
    #pygame.display.update()
    time.sleep(0.1)

def key_check():
    global moves, player, player_old
    events = pygame.event.get()
    #listen for input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player_old = (player[0],player[1])
        player[1] -= 1
        wrapping_and_history_update()
    if move_check():
        return
    if keys[pygame.K_a]:
        player_old = (player[0],player[1])
        player[0] -= 1
        wrapping_and_history_update()
    if move_check():
        return
    if keys[pygame.K_s]:
        player_old = (player[0],player[1])
        player[1] += 1
        wrapping_and_history_update()
    if move_check():
        return
    if keys[pygame.K_d]:
        player_old = (player[0],player[1])
        player[0] += 1
        wrapping_and_history_update()
    if move_check():
        return

def move_check():
    global moves, running
    if moves <= 0:
        running = False
        return True

while running:
    key_check()

print("Food Collected: {}".format(food))

pygame.quit()
