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
        self.uvmap = []
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
            uv = struct.unpack('6f', f.read(24))
            print uv
            self.uvmap.append(uv)
            
        f.close()
        
        # put everything into a display list
        self.display_list = glGenLists(1)
        glNewList(self.display_list, GL_COMPILE)
        glBegin(GL_TRIANGLES)
        triangle_index = 0
        for triangle in self.triangles:
            print triangle,triangle_index
            index = 0
            for vertex_id in triangle:
                glTexCoord2fv(self.uvmap[triangle_index][index*2:index*2+2])
                index += 1
                glNormal3fv(self.normals[vertex_id])
                glVertex3fv(self.positions[vertex_id])
            triangle_index += 1
        glEnd()
        glEndList()
        
    def draw(self):
        glCallList(self.display_list);