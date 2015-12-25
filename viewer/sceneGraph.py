'''RotationComponent
    mesh

TranslationComponent
    mesh

PathComponent
    mesh

MESH'''

import opengl
import numpy as np

class GroupNode(object):
    def __init__(self):
        self.list=[]
        self.translationmatrix=np.array()
        
    def addNode(self,obj):
        if(True):
            self.list.append(obj)
    
    def draw(self,matrix):
        self.drawChildren(matrix.dot(self.translationmatrix))
        
    def getMatrix(self):
        return self.translationmatrix
    
    def setMatrix(self,matrix):
        self.translationmatrix=matrix
    
    def multMatrix(self,matrix):
        self.translationmatrix=self.translationmatrix.dot(matrix)
    
    def rMultMatrix(self,matrix):
        self.translationmatrix=matrix.dot(self.translationmatrix)
        
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
        print "load Matrix=>",matrix
        print "ich bin ein Baum"
    
