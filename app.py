import sys
import math
from PIL import Image, ImageDraw
import pygame
from pygame.locals import *
from djitellopy import tello
import numpy as np
import cv2
import time

frames = 60
param_names = {0: '0 - length (cm)', 1: '1 - width (cm)', 2: '2 - overlap (0-100)', 3: '3 - total_degrees', 4: '4 - interval'}
param_colors = {0: (255, 255, 255), 1: (255, 255, 255), 2: (255, 255, 255), 3: (255, 255, 255), 4: (255, 255, 255)}
configuration = {0: 150, 1: 150, 2: 80, 3: 180, 4: 20}
configuring = False
configuring_param = 0

def deg2rad(degrees):
    return (degrees*2*math.pi)/360

def frameRate(f):
    global frames
    frames = f

def getKey(keyName):
    ans = False
    keyInput = pygame.key.get_pressed()
    myKey = getattr(pygame, 'K_{}'.format(keyName))
    if keyInput[myKey]:
        ans = True
    return ans

def draw_filled_arc(screen, color, pos, radius, start, end):
    pil_size = radius*2
    pil_image = Image.new("RGBA", (pil_size, pil_size))
    pil_draw = ImageDraw.Draw(pil_image)

    pil_draw.pieslice((0, 0, pil_size-1, pil_size-1), start, end, fill=color)

    # - convert into PyGame image -
    mode = pil_image.mode
    size = pil_image.size
    data = pil_image.tobytes()
    image = pygame.image.fromstring(data, size, mode)
    image_rect = image.get_rect(topleft=pos)
    
    # blit image
    screen.blit(image, image_rect)

def draw_number_panel(screen): 
    global configuring, configuring_param, configuration

    number = 0
    position = (700,50)
    position_text = (40, 150)
    while(number < 10):
        button_rect = pygame.Rect(position,(40, 40))
        pygame.draw.rect(screen, (20, 137, 160 ), button_rect)
        screen.blit(pygame.font.SysFont("Arial", 22).render(str(number), True, (255, 255, 255)), (position[0]+15, position[1]+5))
        if (number < 4):
            position = (position[0]+42, position[1])
        elif (number == 4):
            position = (700,92)
        else: 
            position = (position[0]+42, position[1])
        if (number < 5):
            screen.blit(pygame.font.SysFont("Arial", 20).render(f"{param_names[number]}: ...", True, param_colors[number]), (position_text))
            screen.blit(pygame.font.SysFont("Arial", 20).render(f"{configuration[number]}", True, param_colors[number]), (position_text[0]+200, position_text[1]))
            position_text = (position_text[0], position_text[1]+30)
        number = number + 1
    
    button_rect = pygame.Rect((700,150),(40, 40))
    pygame.draw.rect(screen, (80, 137, 12), button_rect)
    button_rect = pygame.Rect((750,150),(60, 40))
    pygame.draw.rect(screen, (196, 137, 11), button_rect)
    screen.blit(pygame.font.SysFont("Arial", 20).render('clear', True, (255, 255, 255)), (750+10, 150+5))

    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()
            button_rect = pygame.Rect((700,150),(40, 40))
            if button_rect.collidepoint(pos):
                configuring = False
                for i in range(10):
                    param_colors[i] = (255, 255, 255)
            button_rect = pygame.Rect((750,150),(40, 40))
            if button_rect.collidepoint(pos):
                configuration[configuring_param] = 0
            for i in range(10):
                button_rect = pygame.Rect((700 + 42*(i%5), 50 + 42*(i//5)), (40, 40))
                if button_rect.collidepoint(pos):
                    if not configuring: 
                        configuring_param = i
                        configuring = True
                        param_colors[i] = (20, 137, 160 )
                    else:
                        configuration[configuring_param] = int(str(configuration[configuring_param]) + str(i))

def run(draw):
    global frames
    global param_names
    global configuration
    global configuring
    global configuring_param
    
    clock = pygame.time.Clock()
    running = True
    while running:
        # Wait for fps
        clock.tick(frames)

        # Wait for events
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False       
    
        # Draw
        draw()
    
        # Blit everything
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

def mapSurface(me):

    global configuration

    length = configuration[0] 
    width = configuration[1]
    L_ratio = 1.5
    W_ratio = 1
    overlap = configuration[2]/100

    if(length == 0 or width == 0 or L_ratio == 0 or W_ratio == 0):
        return
   
    me.set_video_direction(me.CAMERA_DOWNWARD)

    length_photo = L_ratio*me.get_height()
    width_photo = W_ratio*me.get_height()

    useful_length_photo = length_photo*(1-overlap)
    useful_width_photo = width_photo*(1-overlap)

    num_rows = math.ceil(length/useful_length_photo)
    num_columns = math.ceil(width/useful_width_photo)

    #Move to initial position
    me.move_left(int(width_photo/2))
    me.move_forward(int(length_photo/2))

    column = 0
    while column < num_columns:
        row = 0
        while row < num_rows:
            filename = f'image_{column}_{row}.jpg'
            image = me.get_frame_read().frame
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            cv2.imwrite(filename, image)
            if column % 2 == 0:
                me.move_forward(int(useful_length_photo))
            else:
                me.move_back(int(useful_length_photo))
            row = row + 1
        me.move_left(int(useful_width_photo))
        column = column + 1

def rotate_panoramic_photo(me):

    global configuration

    total_degrees = configuration[3] 
    interval = configuration[4]

    if(total_degrees == 0 or interval == 0):
        return

    images = []

    me.set_video_direction(me.CAMERA_FORWARD)

    value_deg = 0
    while value_deg < total_degrees:
        filename = f'image_{value_deg}.jpg'
        image = me.get_frame_read().frame
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        cv2.imwrite(filename, image)
        images.append(image)
        me.rotate_clockwise(interval)
        value_deg = value_deg + interval
        time.sleep(1)

    stitcher = cv2.Stitcher_create()

    result = stitcher.stitch((tuple(images)))

    cv2.imwrite('./result.jpg', result[1])