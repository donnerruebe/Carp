'''RotationComponent
    mesh

TranslationComponent
    mesh

PathComponent
    mesh

MESH'''

import OpenGL.GL
import numpy as np

class GroupNode(object):
    def __init__(self):
        self.list=[]
        self.basematrix=np.identity(4)
        self.movematrix=np.identity(4)
        
    def addNode(self,obj):
        if(True):
            self.list.append(obj)
    
    def draw(self,matrix):
        self.drawChildren(matrix.dot(self.basematrix.dot(self.movematrix)))
        
    def setDefaultMatrix(self,matrix):
        basematrix=matrix
        
    def getMatrix(self):
        return self.movematrix
    
    def setMatrix(self,matrix):
        self.movematrix=matrix
    
    def multMatrix(self,matrix):
        self.movematrix=self.movematrix.dot(matrix)
    
    def rMultMatrix(self,matrix):
        self.movematrix=matrix.dot(self.movematrix)
        
    def drawChildren(self,matrix):
        for item in self.list:
            item.draw(matrix)
         
    
class MeshNode:
    def __init__(self):
        self.mesh
        
    def setMesh(self,mesh):
        self.mesh=mesh
        
    '''
    TODO: Texturerweiterung ETC
    '''

    def draw(self,matrix):
        glLoadMatrix(matrix.transpose())
        self.mesh.draw()
        print "load Matrix=>",matrix
        print "ich bin ein Baum"
    
