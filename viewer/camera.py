'''
Created on 28.12.2015

@author: Tilmann
'''

import math
import numpy as np
import transform
import pygame

class Camera(object):
    def __init__(self):
        self.lens = np.identity(4)
        self.inverted_lens = np.identity(4)
        self.projection_matrix = np.identity(4)
        self.position = np.array([0,0,0])
        self.angles = [0,0,0]
        self.resolution = [640,480]
        self.is_rotating = False
        self.click_direction = np.array([0,0,1])
    
    def changeLens(self, resolution, vertical_fov_in_degrees, near, far):
        self.resolution = resolution
        r = 1.0/(near - far)
        w0 = 2.0*near*far*r
        z0 = (near + far)*r
        y1 = math.tan(math.radians(vertical_fov_in_degrees)*0.5)
        x1 = y1 * resolution[0] / float(resolution[1])
        x0 = 1.0/x1
        y0 = 1.0/y1
        z1 = 1.0/w0
        w1 = z0*z1
        self.lens = np.array([[x0,  0,  0,  0],
                              [ 0, y0,  0,  0],
                              [ 0,  0, z0, w0],
                              [ 0,  0, -1,  0]])
        self.inverted_lens = np.array([[x1,  0,  0,  0],
                                       [ 0, y1,  0,  0],
                                       [ 0,  0,  0, -1],
                                       [ 0,  0, z1, w1]])
    
    def getProjectionMatrix(self):
        rotation = transform.rotation_from_euler_deg(self.angles).transpose() # A transposed rotation matrix is its own inverse.
        translation = transform.translation_matrix(-self.position)
        return np.dot(self.lens, np.dot(rotation, translation))
    
    def getInverseProjectionMatrix(self):
        rotation = transform.rotation_from_euler_deg(self.angles)
        translation = transform.translation_matrix(self.position)
        return np.dot(np.dot(translation, rotation), self.inverted_lens)
    
    def update(self, frame_time, mouse_wheel):
        inverse_projection_matrix = self.getInverseProjectionMatrix()
        
# TODO: Input code doesn't belong here. Get input as argument?
        screen_mouse_vel = pygame.mouse.get_rel()
        screen_mouse_pos = pygame.mouse.get_pos()
        normalized_mouse_pos = np.array([screen_mouse_pos[0]*2.0/self.resolution[0] - 1.0, 1.0 - screen_mouse_pos[1]*2.0/self.resolution[1], 0.95, 1.0])
        normalized_mouse_vel = np.array([screen_mouse_vel[0]*2.0/self.resolution[0]      ,     - screen_mouse_vel[1]*2.0/self.resolution[1], 0.0 , 0.0])
        mouse_world_pos = np.dot(inverse_projection_matrix, normalized_mouse_pos)
        mouse_world_pos /= mouse_world_pos[3]
        mouse_buttons = pygame.mouse.get_pressed()
        keys = pygame.key.get_pressed()
        #movement_input = np.array([keys[pygame.K_d] - keys[pygame.K_a], keys[pygame.K_SPACE] - keys[pygame.K_c], keys[pygame.K_w] - keys[pygame.K_s], 0])
        #speed_factor = 0.0005 if keys[pygame.K_LSHIFT] else 0.005

# camera movement
        if mouse_wheel and not mouse_buttons[0]:
            mouse_dir = mouse_world_pos - self.position
            mouse_dir /= np.linalg.norm(mouse_dir[:3])
            self.position -= mouse_dir * mouse_wheel * (0.01 if keys[pygame.K_LSHIFT] else 1.0)
        if mouse_buttons[1]:
            self.position -= np.dot(inverse_projection_matrix, normalized_mouse_vel) * (1.0 if keys[pygame.K_LSHIFT] else 10.0)
        if mouse_buttons[2]:
            #self.angles[0] += screen_mouse_vel[0] * 0.1
            #self.angles[2] += screen_mouse_vel[1] * 0.1
            if not self.is_rotating:
                self.is_rotating = True
                self.click_direction = (mouse_world_pos - self.position)[:3]
                self.click_direction /= np.linalg.norm(self.click_direction)
            d0 = self.click_direction # identifier shortening
            d1 = (mouse_world_pos - self.position)[:3]
            d1 /= np.linalg.norm(d1)
            # horizontal rotation
            lengths = np.linalg.norm(d0[0:2]) * np.linalg.norm(d1[0:2])
            if lengths > 0.000001:
                sin_angle = (d0[0] * d1[1] - d0[1] * d1[0]) / lengths;
                self.angles[0] -= math.degrees(math.asin(sin_angle))
            # vertical rotation
            self.angles[2] -= math.degrees(math.asin(d1[2]) - math.asin(d0[2]))
            self.angles[2] = min(max(self.angles[2], 0), 180)
        else:
            self.is_rotating = False
        #movement_direction = np.dot(world_from_ndc, movement_input)
        #movement_direction /= movement_direction[3]
        #self.position += movement_direction * speed_factor * frame_time
        self.position /= self.position[3] # Avoid accumulation of rounding errors in the w coordinate.
        
        return (self.getProjectionMatrix(), inverse_projection_matrix)
        