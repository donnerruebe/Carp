'''
Created on 25.12.2015

@author: Tilmann
'''
from OpenGL import GL
import struct

class Mesh(object):
    def __init__(self, filename = None):
        self.positions = []
        self.normals = []
        self.triangles = []
        self.uvmap = []
        self.display_list = 0
        if filename is not None:
            self.loadFromFile(filename)
    
    #def __del__(self):
    #    glDeleteLists(self.display_list, 1);
    
    def loadFromFile(self, filename):
        f = open(filename, 'rb')
        num_verts, num_tris = struct.unpack('2I', f.read(8))
        # read vertices
        for _ in range(num_verts):
            position = struct.unpack('3f', f.read(12))
            self.positions.append(position)
            normal = struct.unpack('3f', f.read(12))
            self.normals.append(normal)
        # read triangles
        for _ in range(num_tris):
            triangle = struct.unpack('3I', f.read(12))
            self.triangles.append(triangle)
            uv = struct.unpack('6f', f.read(24))
            self.uvmap.append(uv)
            
        f.close()
        
        # put everything into a display list
        self.display_list = GL.glGenLists(1)
        GL.glNewList(self.display_list, GL.GL_COMPILE)
        GL.glBegin(GL.GL_TRIANGLES)
        for triangle_index, triangle in enumerate(self.triangles):
            for index, vertex_id in enumerate(triangle):
                GL.glTexCoord2fv(self.uvmap[triangle_index][index*2:index*2+2])
                GL.glNormal3fv(self.normals[vertex_id])
                GL.glVertex3fv(self.positions[vertex_id])
        GL.glEnd()
        GL.glEndList()
        
    def draw(self, transform):
        # TODO: Use shaders and VBOs instead of the old pipeline.
        GL.glLoadMatrixf(transform.transpose())
        GL.glCallList(self.display_list);