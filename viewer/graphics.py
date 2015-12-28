'''
Created on 24.12.2015

@author: Tilmann
'''

from math import *

import pygame
from pygame.locals import *

from OpenGL import GL

import numpy as np

from kuka import Kuka

from camera import Camera

def drawGrid():
    GL.glBegin(GL.GL_LINES)
    GL.glColor3f(0,0,0)
    for x in range(-5, 6):
        GL.glVertex3i(x, -5, 0)
        GL.glVertex3i(x, 5, 0)
    for y in range(-5, 6):
        GL.glVertex3i(-5, y, 0)
        GL.glVertex3i(5, y, 0)
    GL.glEnd()

def closestPointOnLine(point, line_start, line_end):
    # fixme
    d_line = line_end[:3] - line_start[:3]
    d_line /= np.linalg.norm(d_line)
    d_point = point[:3] - line_start[:3]
    return np.append(line_start[:3] + d_line * np.dot(d_line, d_point), 1.0)

def main():
    pygame.init()
    display = (800,600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL|RESIZABLE)
    
    kuka = Kuka()
    
    # TODO: Texture class.
    textureSurface = pygame.image.load("../resources/robots/Kuka/texture.png")
    textureData = pygame.image.tostring(textureSurface, "RGBA", 1)
    width = textureSurface.get_width()
    height = textureSurface.get_height()
    texture = GL.glGenTextures(1)
    GL.glBindTexture(GL.GL_TEXTURE_2D, texture)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MAG_FILTER, GL.GL_LINEAR)
    GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
    GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, GL.GL_RGBA, width, height, 0, GL.GL_RGBA, GL.GL_UNSIGNED_BYTE, textureData)
    
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
    target_depth = 0.0
    
    camera = Camera()
    camera.position = np.array([0.0,-7.0,1.0,1.0])
    camera.angles = [0,0,90]
    camera_fov = 60.0
    camera_clip_near = 0.1
    camera_clip_far = 50.0
    camera.changeLens(display, camera_fov, camera_clip_near, camera_clip_far)
    
    GL.glEnable(GL.GL_LIGHT0)
    GL.glLightfv(GL.GL_LIGHT0, GL.GL_POSITION, (0.0, 0.0, 1.0, 0.0))
    GL.glLightfv(GL.GL_LIGHT0, GL.GL_AMBIENT, (0.5, 0.5, 0.5, 1.0))
    GL.glColorMaterial(GL.GL_FRONT_AND_BACK, GL.GL_AMBIENT)
    GL.glEnable(GL.GL_COLOR_MATERIAL)
    GL.glEnable(GL.GL_DEPTH_TEST)
    GL.glClearColor(0.75,0.75,0.75,1.0)
    GL.glPointSize(16.0)
    GL.glEnable(GL.GL_POINT_SMOOTH)
    GL.glEnable(GL.GL_LINE_SMOOTH)
    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
    GL.glEnable(GL.GL_CULL_FACE)
    
    prev_timestamp = pygame.time.get_ticks()
    frame_time = 0

    while True:
# timing
        timestamp = pygame.time.get_ticks()
        frame_time = timestamp - prev_timestamp
        prev_timestamp = timestamp
        
# handle events
        mouse_wheel = 0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.VIDEORESIZE:
                display = event.dict['size']
                GL.glViewport(0,0,display[0],display[1])
                camera.changeLens(display, camera_fov, camera_clip_near, camera_clip_far)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4:
                    mouse_wheel = 1
                if event.button == 5:
                    mouse_wheel = -1
        
# move the robot
        for constraint in kuka.constraints.itervalues():
            constraint.update(frame_time)
        
# prepare rendering
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        
        projection_matrix, inverted_projection_matrix = camera.update(frame_time, mouse_wheel)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadMatrixf(projection_matrix.transpose())
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()
        
# input (TODO: Clean up code duplication in Camera.update().)
        mouse_pos = pygame.mouse.get_pos()
        normalized_mouse_pos = np.array([mouse_pos[0]*2.0/display[0] - 1.0, 1.0 - mouse_pos[1]*2.0/display[1], 0.95, 1.0])
        mouse_world_pos = np.dot(inverted_projection_matrix, normalized_mouse_pos)
        mouse_world_pos /= mouse_world_pos[3]
        mouse_buttons = pygame.mouse.get_pressed()
        keys = pygame.key.get_pressed()

# moving the target
        normalized_screen_target = np.dot(projection_matrix, target)
        normalized_screen_target /= normalized_screen_target[3]
        mouse_distance = np.linalg.norm(np.multiply(normalized_screen_target[0:2] - normalized_mouse_pos[0:2], display))
        target_hovered = (mouse_distance < 16.0)
        if mouse_buttons[0] and target_hovered and not target_clicked:
            target_depth = normalized_screen_target[2]
            target_clicked = True
        if not mouse_buttons[0]:
            target_clicked = False
        
        if target_clicked:
            target_depth += mouse_wheel * (0.0005 if keys[pygame.K_LSHIFT] else 0.005)
            target = normalized_mouse_pos
            target[2] = target_depth
            target = np.dot(inverted_projection_matrix, target)

# rendering
        
        # draw robot shadow (Just a quick, temporary hack)
        GL.glPushMatrix()
        shadow_matrix = np.identity(4)
        shadow_matrix[2,2] = 0
        GL.glColor3f(0.6,0.6,0.6)
        GL.glDepthMask(False)
        kuka.draw(shadow_matrix)
        GL.glDepthMask(True)
        GL.glPopMatrix()
        
        # draw robot
        GL.glEnable(GL.GL_LIGHTING)
        GL.glEnable(GL.GL_TEXTURE_2D)
        GL.glPushMatrix()
        kuka.draw(np.identity(4))
        GL.glPopMatrix()
        GL.glDisable(GL.GL_LIGHTING)
        GL.glDisable(GL.GL_TEXTURE_2D)
        
        # draw target
        GL.glBegin(GL.GL_POINTS)
        if target_clicked:
            GL.glColor3f(1,1,0)
        elif target_hovered:
            GL.glColor3f(1,0,0)
        else:
            GL.glColor3f(.5,.5,.5)
        GL.glVertex4fv(target)
        GL.glEnd()
        GL.glBegin(GL.GL_LINES)
        GL.glVertex4f(target[0], target[1], 0.0, target[3])
        GL.glVertex4fv(target)
        GL.glEnd()
        
        drawGrid()
        
        pygame.display.flip()
        pygame.time.wait(10)

main()