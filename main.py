import pygame
from random import randint
import math
import time

#set seed to be the same
#train a nn to find the best path

grid_width = 20
grid_height = 20

grid_size = 30

max_val = 6

grid = [[randint(0,max_val) for y in range(grid_height)] for x in range(grid_width)]

history = {}

for x in range(grid_width):
        for y in range(grid_height):
            if grid[x][y] < max_val:
                grid[x][y] = 0
            else:
                grid[x][y] = 1

width = grid_size*grid_width
height = grid_size*grid_height

surface = pygame.display.set_mode((width, height))

def draw_grid_lines():
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
    global player, food, history, grid_width, grid_height
    
    cell_x = int(player[0])
    cell_y = int(player[1])

    colour = (255,0,0)

    if grid[cell_x][cell_y] == int(1):
        food += 1
        grid[cell_x][cell_y] = 0
    
    fill_cell(cell_x,cell_y,colour)

def draw_food():
    for x in range(grid_width):
        for y in range(grid_height):
            if grid[x][y]:
                colour = (0,128,0)
                cell_x = x
                cell_y = y
                fill_cell(cell_x,cell_y,colour)

def add_history():
    global history_colour, player, history
    history_colour[0] += colour_change
    history_colour[1] -= colour_change
    history_colour[2] -= colour_change

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

moves = 3000

history_colour = [128.0,128.0,128.0]

colour_change = (128/moves)

player = [grid_width/2,grid_height/2]

add_history()

fill_grid()

draw_grid_lines()

pygame.display.update()

running = True

moves_old = 0

def wrapping_and_history_update():
    global moves, player, grid_height, grid_width, running
    moves -= 1
    if moves_old != moves:
        if int(player[0]) >= grid_width:
            player[0] = 0
        elif int(player[0]) < 0:
            player[0] = grid_width-1
        if int(player[1]) >= grid_height:
            player[1] = 0
        elif int(player[1]) < 0:
            player[1] = grid_height-1
        add_history()
        print("Moves Remaining: {}".format(moves))
    redraw_scene()
    move_check()
    
def redraw_scene():
    fill_grid()

    draw_grid_lines()
    
    pygame.display.update()
    time.sleep(0.01)

def key_check():
    global moves, player, moves_old
    events = pygame.event.get()
    #listen for input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player[1] -= 1
        wrapping_and_history_update()
    if move_check():
        return
    if keys[pygame.K_a]:
        player[0] -= 1
        wrapping_and_history_update()
    if move_check():
        return
    if keys[pygame.K_s]:
        player[1] += 1
        wrapping_and_history_update()
    if move_check():
        return
    if keys[pygame.K_d]:
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
    
    redraw_scene()

print("Food Collected: {}".format(food))

pygame.quit()
