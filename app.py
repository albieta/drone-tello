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
function_names = {
    0: '0 - Map a Surface',
    1: '1 - Panoramic photo',
    2: '2 - Hallway photo'}
function_colors = {
    0: (255, 255, 255),
    1: (255, 255, 255),
    2: (255, 255, 255)}
param_names = {
    0: {0: '0 - length (cm)', 1: '1 - width (cm)', 2: '2 - overlap (0-100)'}, 
    1: {0: '0 - total_degrees', 1: '1 - interval'},
    2: {0: '0 - length (cm)'}}
param_colors = {
    0: {0: (255, 255, 255), 1: (255, 255, 255), 2: (255, 255, 255)}, 
    1: {0: (255, 255, 255), 1: (255, 255, 255)},
    2: {0: (255, 255, 255)}}
configuration = {
    0: {0: 150, 1: 150, 2: 80}, 
    1: {0: 180, 1: 20},
    2: {0: 500}}
configuring = False
configuring_param = 0
selected_function = False
selected_function_num = 0

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
    global configuring, configuring_param, configuration, selected_function, selected_function_num

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
        if (selected_function == True):
            if number < len(param_names[selected_function_num]):
                param_text = f"{param_names[selected_function_num][number]}: ..."
                config_text = str(configuration[selected_function_num][number])
                param_color = param_colors[selected_function_num][number]

                screen.blit(pygame.font.SysFont("Arial", 20).render(param_text, True, param_color), position_text)
                screen.blit(pygame.font.SysFont("Arial", 20).render(config_text, True, param_color),
                            (position_text[0] + 200, position_text[1]))
                position_text = (position_text[0], position_text[1] + 30)
        else:
            if(number < len(function_names)):
                screen.blit(pygame.font.SysFont("Arial", 20).render(f"{function_names[number]}", True, function_colors[number]), (position_text))
                position_text = (position_text[0], position_text[1]+30)

        number = number + 1
    
    button_rect = pygame.Rect((700,150),(70, 40))
    pygame.draw.rect(screen, (80, 137, 12), button_rect)
    screen.blit(pygame.font.SysFont("Arial", 20).render('select', True, (255, 255, 255)), (700+10, 150+5))
    button_rect = pygame.Rect((700,200),(70, 40))
    pygame.draw.rect(screen, (80, 137, 12), button_rect)
    screen.blit(pygame.font.SysFont("Arial", 20).render('back', True, (255, 255, 255)), (700+10, 200+5))
    button_rect = pygame.Rect((780,150),(40, 40))
    pygame.draw.rect(screen, (255,0,0), button_rect)
    button_rect = pygame.Rect((830,150),(60, 40))
    pygame.draw.rect(screen, (196, 137, 11), button_rect)
    screen.blit(pygame.font.SysFont("Arial", 20).render('clear', True, (255, 255, 255)), (830+10, 150+5))

    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()
            button_rect = pygame.Rect((700,150),(70, 40))
            if button_rect.collidepoint(pos):
                selected_function = True
            button_rect = pygame.Rect((700,200),(70, 40))
            if button_rect.collidepoint(pos):
                selected_function = False
            button_rect = pygame.Rect((830,150),(60, 40))
            if button_rect.collidepoint(pos):
                configuration[selected_function_num][configuring_param] = 0
            button_rect = pygame.Rect((780,150),(40, 40))
            if button_rect.collidepoint(pos):
                configuring = False
                for i in range(len(param_names[selected_function_num])):
                    param_colors[selected_function_num][i] = (255, 255, 255)
                for i in range(len(function_names)):
                    function_colors[i] = (255, 255, 255)
            for i in range(10):
                button_rect = pygame.Rect((700 + 42*(i%5), 50 + 42*(i//5)), (40, 40))
                if button_rect.collidepoint(pos):
                    if selected_function == True:
                        if not configuring: 
                            configuring_param = i
                            configuring = True
                            param_colors[selected_function_num][i] = (20, 137, 160 )
                        else:
                            configuration[selected_function_num][configuring_param] = int(str(configuration[selected_function_num][configuring_param]) + str(i))
                    else: 
                        for e in range(len(function_names)):
                            function_colors[e] = (255, 255, 255)
                        function_colors[i] = (20, 137, 160 )
                        selected_function_num = i

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

    length = configuration[0][0] 
    width = configuration[0][1]
    L_ratio = 1.5
    W_ratio = 1
    overlap = configuration[0][2]/100

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

    total_degrees = configuration[1][0] 
    interval = configuration[1][1]

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

def hallway_panoramic_photo(me):

    global configuration

    length = configuration[2][0]

    images = []

    me.set_video_direction(me.CAMERA_FORWARD)

    interval = 0
    while interval < length:
        filename = f'image_{interval}.jpg'
        image = me.get_frame_read().frame
        if image is not None:
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            cv2.imwrite(filename, image)
            images.append(image)

        me.send_rc_control(30,0,0,0)
        interval = interval + 50
        time.sleep(1)

    stitcher = cv2.Stitcher_create()

    result = stitcher.stitch((tuple(images)))

    cv2.imwrite('./result.jpg', result[1])