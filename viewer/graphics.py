'''
Created on 24.12.2015

@author: Tilmann
'''

import struct
from math import sin, cos

class Matrix(object):
    def __init__(self):
        self.entries = [1.0,0.0,0.0,0.0, 0.0,1.0,0.0,0.0, 0.0,0.0,1.0,0.0, 0.0,0.0,0.0,1.0]
        
    def __getitem__(self, index):
        return self.entries[index]
        
    def __setitem__(self, index, value):
        self.entries[index] = value
    
    def __mul__(self, other):
        if isinstance(other, Matrix):
            result = Matrix()
            for i in range(16):
                result[i] = 0.0
                for k in range(4):
                    result[i] += self[i / 4 + k] * other[i % 4 + 4 * k]
            return result
        elif len(other) == 4:
            result = [0,0,0,0]
            for i in range(16):
                result[i % 4] += self[i] * other[i / 4]
            return result
        else:
            result = Matrix()
            for i in range(16):
                result[i] = self[i] * other
            return result
    
    def __rmul__(self, other):
        return self.__mul__(self, other)
    
    def __add__(self, other):
        result = Matrix()
        for i in range(16):
            result[i] = self[i] + other[i]
        return result
    
    def __sub__(self, other):
        result = Matrix()
        for i in range(16):
            result[i] = self[i] - other[i]
        return result
    
    def inverted(self):
        '''Cramer's Rule'''
        result = Matrix()

        # First half
        t01 = self[2] * self[7];
        t02 = self[2] * self[11];
        t03 = self[2] * self[15];
    
        t10 = self[6] * self[3];
        t12 = self[6] * self[11];
        t13 = self[6] * self[15];
    
        t20 = self[10] * self[3];
        t21 = self[10] * self[7];
        t23 = self[10] * self[15];
    
        t30 = self[14] * self[3];
        t31 = self[14] * self[7];
        t32 = self[14] * self[11];
    
        result[0] = (t23 * self[5] + t31 * self[9] + t12 * self[13]) - (t32 * self[5] + t13 * self[9] + t21 * self[13]);
        result[1] = (t32 * self[1] + t03 * self[9] + t20 * self[13]) - (t23 * self[1] + t30 * self[9] + t02 * self[13]);
        result[2] = (t13 * self[1] + t30 * self[5] + t01 * self[13]) - (t31 * self[1] + t03 * self[5] + t10 * self[13]);
        result[3] = (t21 * self[1] + t02 * self[5] + t10 * self[9]) - (t12 * self[1] + t20 * self[5] + t01 * self[9]);
    
        result[4] = (t32 * self[4] + t13 * self[8] + t21 * self[12]) - (t23 * self[4] + t31 * self[8] + t12 * self[12]);
        result[5] = (t23 * self[0] + t30 * self[8] + t02 * self[12]) - (t32 * self[0] + t03 * self[8] + t20 * self[12]);
        result[6] = (t31 * self[0] + t03 * self[4] + t10 * self[12]) - (t13 * self[0] + t30 * self[4] + t01 * self[12]);
        result[7] = (t12 * self[0] + t20 * self[4] + t01 * self[8]) - (t21 * self[0] + t02 * self[4] + t10 * self[8]);
    
        # Second half
        t01 = self[0] * self[5];
        t02 = self[0] * self[9];
        t03 = self[0] * self[13];
    
        t10 = self[4] * self[1];
        t12 = self[4] * self[9];
        t13 = self[4] * self[13];
    
        t20 = self[8] * self[1];
        t21 = self[8] * self[5];
        t23 = self[8] * self[13];
    
        t30 = self[12] * self[1];
        t31 = self[12] * self[5];
        t32 = self[12] * self[9];
    
        result[8] = (t23 * self[7] + t31 * self[11] + t12 * self[15]) - (t32 * self[7] + t13 * self[11] + t21 * self[15]);
        result[9] = (t32 * self[3] + t03 * self[11] + t20 * self[15]) - (t23 * self[3] + t30 * self[11] + t02 * self[15]);
        result[10] = (t13 * self[3] + t30 * self[7] + t01 * self[15]) - (t31 * self[3] + t03 * self[7] + t10 * self[15]);
        result[11] = (t21 * self[3] + t02 * self[7] + t10 * self[11]) - (t12 * self[3] + t20 * self[7] + t01 * self[11]);
    
        result[12] = (t13 * self[10] + t21 * self[14] + t32 * self[6]) - (t12 * self[14] + t23 * self[6] + t31 * self[10]);
        result[13] = (t02 * self[14] + t23 * self[2] + t30 * self[10]) - (t03 * self[10] + t20 * self[14] + t32 * self[2]);
        result[14] = (t03 * self[6] + t10 * self[14] + t31 * self[2]) - (t01 * self[14] + t13 * self[2] + t30 * self[6]);
        result[15] = (t01 * self[10] + t12 * self[2] + t20 * self[6]) - (t02 * self[6] + t10 * self[10] + t21 * self[2]);
    
        # Divide by determinant
        determinant = self[0] * result[0] + self[4] * result[1] + self[8] * result[2] + self[12] * result[3];
        reciprocal_determinant = 1.0 / determinant;
        result *= reciprocal_determinant;
        return result
    
    def transposed(self):
        result = Matrix()
        for i in range(16):
            result[i] = self[(i % 4) * 4 + i / 4]
        return result
    
    @staticmethod
    def perspective(clip_near, clip_far, fov_x, fov_y):
        result = Matrix()
        result[0] = fov_x
        result[5] = fov_y
        result[10] = (clip_near + clip_far) / (clip_near - clip_far)
        result[11] = -1.0
        result[14] = 2.0 * clip_near * clip_far / (clip_near - clip_far)
        result[15] = 0.0
        return result
    
    @staticmethod
    def euler(psi, theta, phi):
        cos_psi = cos(psi)
        sin_psi = sin(psi)
        cos_theta = cos(theta)
        sin_theta = sin(theta)
        cos_phi = cos(phi)
        sin_phi = sin(phi)
    
        result = Matrix()
        
        result[0] = cos_phi * cos_psi + sin_phi * sin_theta * sin_psi
        result[4] = -sin_phi * cos_psi + cos_phi * sin_theta * sin_psi
        result[8] = cos_theta * sin_psi
    
        result[1] = sin_phi * cos_theta
        result[5] = cos_phi * cos_theta
        result[9] = -sin_theta
    
        result[2] = -cos_phi * sin_psi + sin_phi * sin_theta * cos_psi
        result[6] = sin_phi * sin_psi + cos_phi * sin_theta * cos_psi
        result[10] = cos_theta * cos_psi
        return result
    
    @staticmethod
    def translation(translation_vector):
        result = Matrix()
        result.entries = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, translation_vector[0], translation_vector[1], translation_vector[2], 1]
        return result
    
    @staticmethod
    def rotation_x(angle):
        cos_angle = cos(angle)
        sin_angle = sin(angle)
        result = Matrix()
        result.entries = [1, 0, 0, 0, 0, cos_angle, sin_angle, 0, 0, -sin_angle, cos_angle, 0, 0, 0, 0, 1]
        return result
    
    @staticmethod
    def rotation_y(angle):
        cos_angle = cos(angle)
        sin_angle = sin(angle)
        result = Matrix()
        result.entries = [cos_angle, 0, -sin_angle, 0, 0, 1, 0, 0, sin_angle, 0, cos_angle, 0, 0, 0, 0, 1]
        return result
    
    @staticmethod
    def rotation_z(angle):
        cos_angle = cos(angle)
        sin_angle = sin(angle)
        result = Matrix()
        result.entries = [cos_angle, sin_angle, 0, 0, -sin_angle, cos_angle, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
        return result
        

class Mesh(object):
    '''
    classdocs
    '''

    def __init__(self, filename = None):
        '''
        Constructor
        '''
        self.positions = []
        self.normals = []
        self.triangles = []
        self.display_list = 0
        if(filename):
            self.loadFromFile(filename)
    
    #def __del__(self):
    #    glDeleteLists(self.display_list, 1);
    
    def loadFromFile(self, filename):
        f = open(filename, 'rb')
        num_verts, num_tris = struct.unpack('2I', f.read(8))
        # read vertices
        for i in range(num_verts):
            position = struct.unpack('3f', f.read(12))
            self.positions.append(position)
            normal = struct.unpack('3f', f.read(12))
            self.normals.append(normal)
        # read triangles
        for i in range(num_tris):
            triangle = struct.unpack('3I', f.read(12))
            self.triangles.append(triangle)
            
        f.close()
        
        # put everything into a display list
        self.display_list = glGenLists(1)
        glNewList(self.display_list, GL_COMPILE)
        glBegin(GL_TRIANGLES)
        glColor3f(1.0, 0.5, 0.0)
        for triangle in self.triangles:
            for vertex_index in triangle:
                glNormal3fv(self.normals[vertex_index])
                glVertex3fv(self.positions[vertex_index])
        glEnd()
        glEndList()
        
    def Draw(self):
        glCallList(self.display_list);
        

class Camera(object):
    def __init__(self):
        pass

import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

import numpy as np

def resizeDisplay(display):
    glViewport(0,0,display[0],display[1])

# TODO: Camera Class.
def setCameraMatrix(display, angles, position):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity();
    gluPerspective(45, (display[0]/float(display[1])), 0.1, 50.0)
    glRotatef(angles[1], 1.0, 0.0, 0.0)
    glRotatef(angles[0], 0.0, 0.0, 1.0)
    glTranslatef(-position[0], -position[1], -position[2])

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

def main():
    pygame.init()
    display = (800,600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL|RESIZABLE)
    
    meshes = []
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
    angular_velocities = [.1,.1,.1,.1,.1,.1,.1]
    target = np.array([3, 0, 3, 1.0])

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
        
        projection_matrix = np.array(glGetFloatv(GL_PROJECTION_MATRIX))
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
        normalized_mouse_pos = np.array([mouse_pos[0]*2.0/display[0] - 1.0, 1.0 - mouse_pos[1]*2.0/display[1], 1.0, 1.0])
        mouse_buttons = pygame.mouse.get_pressed()
        keys = pygame.key.get_pressed()

# camera movement
        if mouse_buttons[2]:
            camera_angles[0] += mouse_vel[0] * mouse_sensitivity * frame_time
            camera_angles[1] += mouse_vel[1] * mouse_sensitivity * frame_time
        movement_input = np.array([keys[pygame.K_d] - keys[pygame.K_a], keys[pygame.K_SPACE] - keys[pygame.K_c], keys[pygame.K_w] - keys[pygame.K_s], 0])
        movement_direction = np.dot(projection_matrix, movement_input)
        speed = 0.0005 if keys[pygame.K_LSHIFT] else 0.005
        camera_position += movement_direction * speed * frame_time 

# moving the target
        normalized_screen_target = np.dot(projection_matrix, target)
        screen_target = np.multiply(normalized_screen_target[0:2] * 0.5 + [0.5, 0.5], display)
        mouse_distance = np.linalg.norm(screen_target - mouse_pos[0:2])
        #print normalized_screen_target, screen_target, mouse_distance
        if mouse_buttons[0]:
            target = np.dot(inverted_projection_matrix.transpose(), normalized_mouse_pos)
            #target[0] += (mouse_vel[0] * projection_matrix[0] + mouse_vel[1] * projection_matrix[4]) * mouse_sensitivity
            #target[1] += (mouse_vel[0] * projection_matrix[1] + mouse_vel[1] * projection_matrix[5]) * mouse_sensitivity
            #target[2] += (mouse_vel[0] * projection_matrix[2] + mouse_vel[1] * projection_matrix[6]) * mouse_sensitivity

# rendering
        drawGrid()
        
        # draw robot
        glEnable(GL_LIGHTING)
        glPushMatrix()
        for i in range(len(meshes)):
            meshes[i].Draw()
            glTranslatef(translations[i][0], translations[i][1], translations[i][2])
            glRotatef(angles[i], axes[i][0], axes[i][1], axes[i][2])
            angles[i] += angular_velocities[i] * frame_time
            if angles[i] >= limits[i][1] and angular_velocities[i] > 0 or angles[i] <= limits[i][0] and angular_velocities[i] < 0:
                angular_velocities[i] *= -1
        glPopMatrix()
        glDisable(GL_LIGHTING)
        
        # draw target
        glBegin(GL_POINTS)
        glColor3f(1,1,1)
        glVertex4f(target[0], target[1], target[2], target[3])
        glEnd()
        glBegin(GL_LINES)
        glVertex4f(target[0], target[1], 0.0, target[3])
        glVertex4f(target[0], target[1], target[2], target[3])
        glEnd()
        
        pygame.display.flip()
        pygame.time.wait(30)

main()