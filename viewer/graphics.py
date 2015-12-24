'''
Created on 24.12.2015

@author: Tilmann
'''

import struct
from OpenGL.raw.GL.VERSION.GL_1_1 import GL_AMBIENT

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
        if(filename):
            self.LoadFromFile(filename)
    
    def LoadFromFile(self, filename):
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
        
    def Draw(self):
        glBegin(GL_TRIANGLES)
        glColor3f(1.0, 0.5, 0.0)
        for triangle in self.triangles:
            for vertex_index in triangle:
                glNormal3fv(self.normals[vertex_index])
                glVertex3fv(self.positions[vertex_index])
        glEnd()
        
    
import pygame
from pygame.locals import *

from OpenGL.GL import *
from OpenGL.GLU import *

def ResizeDisplay(display):
    glViewport(0,0,display[0],display[1])

def SetCameraMatrix(display, angles, distance):
    glLoadIdentity();
    gluPerspective(45, (display[0]/float(display[1])), 0.1, 50.0)
    glTranslatef(0.0,-1, -distance)
    glRotatef(angles[1], 1.0, 0.0, 0.0)
    glRotatef(angles[0], 0.0, 0.0, 1.0)

def DrawGrid():
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
    
    angles = [
              0,0,0,0,0,0,0]
    angular_velocities = [
              1,1,1,1,1,1,1]
    
    target = (3, 0, 3)
    
    pygame.init()
    display = (800,600)
    pygame.display.set_mode(display, DOUBLEBUF|OPENGL|RESIZABLE)

    camera_angles = [0,-90]
    camera_distance = 7;
    mouse_sensitivity = 0.5
    
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, (0.0, 1.0, 0.0, 0.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.5, 0.5, 0.5, 1.0))
    glColorMaterial ( GL_FRONT_AND_BACK, GL_AMBIENT ) ;
    glEnable ( GL_COLOR_MATERIAL ) ;
    glEnable(GL_DEPTH_TEST)
    glClearColor(0.75,0.75,0.75,1.0)
    glPointSize(16.0)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.VIDEORESIZE:
                display = event.dict['size']
                ResizeDisplay(display)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 5:
                    camera_distance *= 1.26
                if event.button == 4:
                    camera_distance /= 1.26
        
        mouse_vel = pygame.mouse.get_rel()
        if pygame.mouse.get_pressed()[2]:
            camera_angles[0] += mouse_vel[0] * mouse_sensitivity
            camera_angles[1] += mouse_vel[1] * mouse_sensitivity

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        
        SetCameraMatrix(display, camera_angles, camera_distance)
        
        DrawGrid()
        
        glEnable(GL_LIGHTING)
        glPushMatrix()
        for i in range(len(meshes)):
            meshes[i].Draw()
            glTranslatef(translations[i][0], translations[i][1], translations[i][2])
            glRotatef(angles[i], axes[i][0], axes[i][1], axes[i][2])
            angles[i] += angular_velocities[i]
            if angles[i] >= limits[i][1] and angular_velocities[i] > 0 or angles[i] <= limits[i][0] and angular_velocities[i] < 0:
                angular_velocities[i] *= -1
        glPopMatrix()
        glDisable(GL_LIGHTING)
        
        glBegin(GL_POINTS)
        glColor3f(1,1,1)
        glVertex3fv(target)
        glEnd()
        glBegin(GL_LINES)
        glVertex3f(target[0], target[1], 0)
        glVertex3fv(target)
        glEnd()
        
        pygame.display.flip()
        pygame.time.wait(10)


main()