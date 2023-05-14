import app
import pygame
from pygame.locals import *
from djitellopy import tello
import numpy as np
import cv2
import time
import math

me = tello.Tello()
me.connect()
me.streamon()

print(me.get_battery())
print(me.get_temperature())

pygame.init()
screen = pygame.display.set_mode((980, 740))
font = pygame.freetype.SysFont("Arial", 12)

video = cv2.VideoWriter('video.avi', cv2.VideoWriter_fourcc(*'XVID'), 30, (960,720))
isMakingVideo = False
frontCamera = True


def draw():
    global battery, roll, pitch, yaw, height, isMakingVideo, frontCamera
    
    # Get data
    battery = me.get_battery()
    roll = me.get_roll()
    pitch = me.get_pitch()
    yaw = me.get_yaw()
    height = me.get_height()

    # Draw
    
    img = me.get_frame_read().frame
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    
    if img is not None:
       
       if isMakingVideo:
           print("VIDEO")
           video.write(img)
       
       img = np.fliplr(img)
       img = np.rot90(img)
       img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
       
       surf = pygame.surfarray.make_surface(img)
       screen.blit(surf, (0,0))
       
       
    else:
        screen.fill((100, 100, 100))
    
    font.render_to(screen, (40, 40), f"Battery: {battery}", (0, 255, 0))
    font.render_to(screen, (40, 60), f"Roll: {roll}", (0, 255, 0))
    font.render_to(screen, (40, 80), f"Pitch: {pitch}", (0, 255, 0))
    font.render_to(screen, (40, 100), f"Yaw: {yaw}", (0, 255, 0))
    font.render_to(screen, (40, 120), f"Height: {height}", (0, 255, 0))
    
    #indicador bateria
    pygame.draw.rect(screen, (128,128,128), [450,40, 100, 30])
    if battery > 20:
        pygame.draw.rect(screen, (0,255,0), [450,40, battery, 30])
    else:
        pygame.draw.rect(screen, (255,0,0), [450,40, battery, 30])
    pygame.draw.rect(screen, (0,0,0), [450,40, 100, 30],2)        
    
    app.draw_filled_arc(screen, (235,177,52), (750,300), 30, roll, roll+180)
    app.draw_filled_arc(screen, (52,235,229), (750,300), 30, roll+180, roll+360)
    app.draw_number_panel(screen)
    
    #movimiento
    lr, fb, ud, yv = (0, 0, 0, 0)
    MOVEMENT = 50
    if app.getKey("LEFT"):
        lr = -MOVEMENT
    if app.getKey("RIGHT"):
        lr = MOVEMENT

    if app.getKey("UP"):
        fb = MOVEMENT
    if app.getKey("DOWN"):
        fb = -MOVEMENT

    if app.getKey("w"):
        ud = MOVEMENT
    if app.getKey("s"):
        ud = -MOVEMENT

    if app.getKey("a"):
        yv = -MOVEMENT
    if app.getKey("d"):
        yv = MOVEMENT

    if app.getKey("t"):
        me.takeoff()
    if app.getKey("l"):
        me.land()
        video.release()
        me.streamoff()
        
    if app.getKey("v"):
        isMakingVideo = True

    if app.getKey("b"):
        isMakingVideo = False

    if app.getKey("p"):
        app.rotate_panoramic_photo(me)

    if app.getKey("f"):
        app.mapSurface(me)


    if app.getKey("h"):
        if frontCamera:
            frontCamera = False
            me.set_video_direction(me.CAMERA_DOWNWARD)
        else:
            frontCamera = True
            me.set_video_direction(me.CAMERA_FORWARD)

    me.send_rc_control(lr,fb,ud,yv)

app.run(draw)
app.handle_events(screen)
