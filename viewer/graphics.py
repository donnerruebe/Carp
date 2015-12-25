'''
Created on 24.12.2015

@author: Tilmann
'''

from math import sin, cos

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

import numpy as np

from kuka import Kuka

class Camera(object):
    def __init__(self):
        pass

# TODO: Camera Class.
def setCameraMatrix(display, angles, position):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity();
    gluPerspective(45, (display[0]/float(display[1])), 0.1, 50.0)
    glRotatef(angles[1], 1.0, 0.0, 0.0)
    glRotatef(angles[0], 0.0, 0.0, 1.0)
    glTranslatef(-position[0], -position[1], -position[2])

def resizeDisplay(display):
    glViewport(0,0,display[0],display[1])

def drawGrid():
    glBegin(GL_LINES)
    glColor3f(0,0,0)
    for x in range(-5, 6):
        glVertex3i(x, -5, 0)
        glVertex3i(x, 5, 0)
    for y in range(-5, 6):
        glVertex3i(-5, y, 0)
        glVertex3i(5, y, 0)
    glEnd()

def closestPointOnLine(point, line_start, line_end):
    # fixme
    d_line = line_end - line_start
    d_line /= np.linalg.norm(d_line)
    print d_line
    d_point = point - line_start
    return line_start + d_line * np.dot(d_line, d_point)

def main():
    pygame.init()
    display = (800,600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL|RESIZABLE)
    
    kuka = Kuka()
    
    '''meshes = []
    meshes.append(Mesh("../meshes/Achse_000.mesh"))
    meshes.append(Mesh("../meshes/Achse_001.mesh"))
    meshes.append(Mesh("../meshes/Achse_002.mesh"))
    meshes.append(Mesh("../meshes/Achse_003.mesh"))
    meshes.append(Mesh("../meshes/Achse_004.mesh"))
    meshes.append(Mesh("../meshes/Achse_005.mesh"))
    meshes.append(Mesh("../meshes/Achse_006.mesh"))
    
    translations = [
        (0, 0, 0.8),
        (0.4, 0, 0),
        (1.2, 0, 0),
        (0.7, 0, 0),
        (0.3, 0, 0),
        (0.25, 0, 0),
        (1.2, -0.3, 0)
        ]
    
    axes = [
        (0, 0, 1.0),
        (0, 1.0, 0),
        (0, 1.0, 0),
        (1.0, 0, 0),
        (0, 1.0, 0),
        (1.0, 0, 0),
        (0, 1.0, 0)
        ]
    
    limits = [
        (-5, 365),
        (-180, 0),
        (-110, 110),
        (-180, 180),
        (-90, 90),
        (-180, 180),
        (90, 90)
        ]
    
    angles = [0,0,0,0,0,0,0]
    angular_velocities = [.1,.1,.1,.1,.1,.1,.1]'''
    
    # TODO: clickable object class
    target = np.array([3, 0, 3, 1.0])
    target_hovered = False
    target_clicked = False

    camera_angles = [0,-90]
    camera_position = np.array([0.0,-7.0,1.0,1.0])
    mouse_sensitivity = 0.01
    camera_clip_near = 0.1
    camera_clip_far = 50.0
    
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, (1.0, -2.0, 3.0, 0.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.5, 0.5, 0.5, 1.0))
    glColorMaterial ( GL_FRONT_AND_BACK, GL_AMBIENT ) ;
    glEnable ( GL_COLOR_MATERIAL ) ;
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.75,0.75,0.75,1.0)
    glPointSize(16.0)
    glEnable(GL_POINT_SMOOTH)
    glEnable(GL_LINE_SMOOTH)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    prev_timestamp = pygame.time.get_ticks()
    frame_time = 0

    while True:
# timing
        timestamp = pygame.time.get_ticks()
        frame_time = timestamp - prev_timestamp
        prev_timestamp = timestamp
        
# prepare rendering
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        
        setCameraMatrix(display, camera_angles, camera_position)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        projection_matrix = np.array(glGetFloatv(GL_PROJECTION_MATRIX).transpose())
        inverted_projection_matrix = np.linalg.inv(projection_matrix)
        
        '''projection_matrix = Matrix.rotation_z(camera_angles[0]) * Matrix.rotation_y(camera_angles[1])#Matrix.perspective(camera_clip_near, camera_clip_far, 1, 1)# Matrix.translation(camera_position) * 
        print projection_matrix.entries
        glMatrixMode(GL_PROJECTION)
        glLoadMatrixf(projection_matrix.transposed().entries)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()'''
        
# input
        mouse_wheel = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.VIDEORESIZE:
                display = event.dict['size']
                resizeDisplay(display)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    mouse_wheel = 1
                if event.button == 5:
                    mouse_wheel = -1
        
        mouse_vel = pygame.mouse.get_rel()
        mouse_pos = pygame.mouse.get_pos()
        normalized_mouse_pos = np.array([mouse_pos[0]*2.0/display[0] - 1.0, 1.0 - mouse_pos[1]*2.0/display[1], 0.95, 1.0])
        mouse_world_pos = np.dot(inverted_projection_matrix, normalized_mouse_pos)
        mouse_world_pos /= mouse_world_pos[3]
        mouse_buttons = pygame.mouse.get_pressed()
        keys = pygame.key.get_pressed()

# camera movement
        if mouse_buttons[2]:
            camera_angles[0] += mouse_vel[0] * mouse_sensitivity * frame_time
            camera_angles[1] += mouse_vel[1] * mouse_sensitivity * frame_time
        movement_input = np.array([keys[pygame.K_d] - keys[pygame.K_a], keys[pygame.K_SPACE] - keys[pygame.K_c], keys[pygame.K_w] - keys[pygame.K_s], 0])
        movement_direction = np.dot(projection_matrix.transpose(), movement_input)
        speed = 0.0005 if keys[pygame.K_LSHIFT] else 0.005
        camera_position += movement_direction * speed * frame_time

# moving the target
        normalized_screen_target = np.dot(projection_matrix, target)
        normalized_screen_target /= normalized_screen_target[3]
        mouse_distance = np.linalg.norm(np.multiply(normalized_screen_target[0:2] - normalized_mouse_pos[0:2], display))
        target_hovered = (mouse_distance < 16.0)
        target_clicked = mouse_buttons[0] and (target_hovered or target_clicked)
        if target_clicked:
            target = closestPointOnLine(target, camera_position, mouse_world_pos)

# rendering
        
        # draw robot
        '''glEnable(GL_LIGHTING)
        glPushMatrix()
        for i in range(len(meshes)):
            meshes[i].draw()
            glTranslatef(translations[i][0], translations[i][1], translations[i][2])
            glRotatef(angles[i], axes[i][0], axes[i][1], axes[i][2])
            angles[i] += angular_velocities[i] * frame_time
            if angles[i] >= limits[i][1] and angular_velocities[i] > 0 or angles[i] <= limits[i][0] and angular_velocities[i] < 0:
                angular_velocities[i] *= -1
        glPopMatrix()'''
        glEnable(GL_LIGHTING)
        glPushMatrix()
        kuka.draw(np.identity(4))
        glPopMatrix()
        glDisable(GL_LIGHTING)
        
        # draw target
        glBegin(GL_POINTS)
        if target_hovered:
            glColor3f(1,0,0)
        else:
            glColor3f(.5,.5,.5)
        glVertex4f(target[0], target[1], target[2], target[3])
        glEnd()
        glBegin(GL_LINES)
        glVertex4f(target[0], target[1], 0.0, target[3])
        glVertex4f(target[0], target[1], target[2], target[3])
        glEnd()
        
        drawGrid()
        
        pygame.display.flip()
        pygame.time.wait(30)

main()