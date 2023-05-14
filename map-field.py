from djitellopy import tello
import numpy as np
import cv2
import math
import time

me = tello.Tello()
me.connect()
me.streamon()

print(me.get_battery())
print(me.get_temperature())

# INFO - considering the drone starts at the bottom right corner of the surface

# L_ratio = length_photo/height (ratio)
# W_ratio = width_photo/height (ratio)
# overlap [0-1]

def mapSurface(length, width, L_ratio, W_ratio, overlap):

    me.takeoff()

    me.set_video_direction(me.CAMERA_DOWNWARD)

    time.sleep(2)

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
            cv2.imwrite(filename, image)
            if column % 2 == 0:
                me.move_forward(int(useful_length_photo))
            else:
                me.move_back(int(useful_length_photo))
            row = row + 1
        me.move_left(int(useful_width_photo))
        column = column + 1

    me.land()

def rotate_panoramic_photo(total_degrees, interval):

    images = []

    me.takeoff()
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

    me.land()

def rotate_panoramic_photo2(total_degrees, interval):

    images = []

    me.takeoff()

    time.sleep(1)

    value_deg = 0
    while value_deg < total_degrees:
        filename = f'image_{value_deg}.jpg'
        image = me.get_frame_read().frame
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        cv2.imwrite(filename, image)
        images.append(image)
        value_deg = value_deg + interval
        time.sleep(1)

    me.land()

        

    me.land()
        
# examples
# mapSurface(80,80, 1.5, 1, 0.5)
rotate_panoramic_photo2(180, 20)

