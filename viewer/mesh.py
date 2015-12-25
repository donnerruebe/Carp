'''
Created on 25.12.2015

@author: Tilmann
'''
from OpenGL.GL import *
import struct

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
        
    def draw(self):
        glCallList(self.display_list);