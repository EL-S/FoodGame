import pygame
from random import randint

grid_width = 20
grid_height = 20

grid_size = 30

grid = [[randint(0,1) for y in range(grid_height)] for x in range(grid_width)]

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

running = True

def fill_cell(x,y,colour):
    global grid_size, grid_width, grid_height
    x = x*grid_size
    y = y*grid_size
    pygame.draw.rect(surface, colour, pygame.Rect(x, y, grid_size, grid_size))

def fill_grid():
    
    surface.fill((255,255,255))
    
    draw_food()    

    draw_player()

def draw_player():
    global player
    cell_x = player[0]
    cell_y = player[1]

    colour = (255,0,0)

    fill_cell(cell_x,cell_y,colour)

def draw_food():
    for x in range(grid_width):
        for y in range(grid_height):
            if grid[x][y]:
                colour = (0,128,0)
                cell_x = x
                cell_y = y
                fill_cell(cell_x,cell_y,colour)

moves = 20

player = [grid_width/2,grid_height/2]

fill_grid()

draw_grid_lines()

pygame.display.update()


#generate the food

#generate the player



while running:

    #listen for input
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                player[1] -= 1
                moves -= 1
            if event.key == pygame.K_a:
                player[0] -= 1
                moves -= 1
            if event.key == pygame.K_s:
                player[1] += 1
                moves -= 1
            if event.key == pygame.K_d:
                player[0] += 1
                moves -= 1

    fill_grid()

    draw_grid_lines()
    #move player

    #subtract 1 from moves
    
    #check moves remaining
        #end game if 0

        #print score
    
    
    pygame.display.update()
        #draw grid
        #draw remaining food
        #draw player
