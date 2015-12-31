'''
Created on 24.12.2015

@author: Tilmann
'''

import pygame
import numpy as np

from OpenGL import GL
from robot import Robot
from camera import Camera

def prepareGrid():
    display_list = GL.glGenLists(1)
    GL.glNewList(display_list, GL.GL_COMPILE)
    GL.glBegin(GL.GL_LINES)
    GL.glColor3f(0,0,0)
    for x in range(-5, 6):
        GL.glVertex3i(x, -5, 0)
        GL.glVertex3i(x, 5, 0)
    for y in range(-5, 6):
        GL.glVertex3i(-5, y, 0)
        GL.glVertex3i(5, y, 0)
    GL.glEnd()
    GL.glEndList()
    return display_list

def drawGrid(grid):
    GL.glCallList(grid);

def main():
    pygame.init()
    display = (800,600)
    pygame.display.set_mode(display, pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE)
    
    grid = prepareGrid()
    robot = Robot("../resources/robots/", "kuka.json")
    
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
    
    # TODO: clickable object class
    target_position = np.array([2.454, 0.375, 1.927, 1])
    target_orientation = [0,0,0]
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
            elif event.type == pygame.KEYDOWN:
                robot_dict = {pygame.K_1:"kuka.json",
                              pygame.K_2:"hydra.json",
                              pygame.K_3:"screw.json",
                              pygame.K_4:"xyz.json",
                              pygame.K_5:"weights_test.json",
                              pygame.K_0:"empty.json"}
                if event.key in robot_dict:
                    robot = Robot("../resources/robots/", robot_dict[event.key])
# move the robot
        for _ in range(10): # Make many small steps instead of one big one to improve convergence.
            # TODO: Move the iterating into kuka.ik to reuse data between iterations and make guarantees about the result's accuracy.
            robot.update(frame_time, np.identity(4))
            robot.ik("Werkzeug", target_position[:3], target_orientation) # TODO: Add a way to input the target orientation.
        
# prepare rendering
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        
        projection_matrix, inverted_projection_matrix = camera.update(frame_time, mouse_wheel)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadMatrixf(projection_matrix.transpose())
        GL.glMatrixMode(GL.GL_MODELVIEW)
        
# input (TODO: Clean up code duplication in Camera.update().)
        mouse_pos = pygame.mouse.get_pos()
        normalized_mouse_pos = np.array([mouse_pos[0]*2.0/display[0] - 1.0, 1.0 - mouse_pos[1]*2.0/display[1], 0.95, 1.0])
        mouse_world_pos = np.dot(inverted_projection_matrix, normalized_mouse_pos)
        mouse_world_pos /= mouse_world_pos[3]
        mouse_buttons = pygame.mouse.get_pressed()
        keys = pygame.key.get_pressed()

# moving the target
        normalized_screen_target = np.dot(projection_matrix, target_position)
        normalized_screen_target /= normalized_screen_target[3]
        mouse_distance = np.linalg.norm(np.multiply(normalized_screen_target[:2] - normalized_mouse_pos[:2], display))
        target_hovered = (mouse_distance < 16.0)
        if mouse_buttons[0] and target_hovered and not target_clicked:
            target_depth = normalized_screen_target[2]
            target_clicked = True
        if not mouse_buttons[0]:
            target_clicked = False
        
        if target_clicked:
            target_depth += mouse_wheel * (0.0005 if keys[pygame.K_LSHIFT] else 0.005)
            target_position = normalized_mouse_pos
            target_position[2] = target_depth
            target_position = np.dot(inverted_projection_matrix, target_position)
            target_position /= target_position[3]

# rendering
        
        # TEMPORARY: draw the robot's shadow
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glPushMatrix()
        shadow_matrix = np.identity(4)
        shadow_matrix[2,2] = 0
        GL.glMultMatrixf(shadow_matrix);
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glColor3f(0.6,0.6,0.6)
        GL.glDepthMask(False)
        robot.draw()
        GL.glDepthMask(True)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glPopMatrix()
        GL.glMatrixMode(GL.GL_MODELVIEW)
        
        # draw robot
        GL.glEnable(GL.GL_LIGHTING)
        GL.glEnable(GL.GL_TEXTURE_2D)
        robot.draw()
        GL.glDisable(GL.GL_LIGHTING)
        GL.glDisable(GL.GL_TEXTURE_2D)
        
        # draw target
        GL.glLoadIdentity()
        GL.glBegin(GL.GL_POINTS)
        if target_clicked:
            GL.glColor3f(1,1,0)
        elif target_hovered:
            GL.glColor3f(1,0,0)
        else:
            GL.glColor3f(.5,.5,.5)
        GL.glVertex4fv(target_position)
        GL.glEnd()
        GL.glBegin(GL.GL_LINES)
        GL.glVertex4f(target_position[0], target_position[1], 0.0, target_position[3])
        GL.glVertex4fv(target_position)
        GL.glEnd()
        
        drawGrid(grid)
        
        pygame.display.flip()
        pygame.time.wait(10)

main()