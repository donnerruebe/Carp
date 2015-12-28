'''RotationComponent
    mesh

TranslationComponent
    mesh

PathComponent
    mesh

MESH'''

import numpy as np
import transform

class GroupNode(object):
    def __init__(self):
        self.children = []
        self.local_transform = np.identity(4)
        
    def addChild(self, obj):
        self.children.append(obj)
    
    def draw(self, parent_transform):
        self.drawChildren(np.dot(parent_transform, self.local_transform))

    def getLocalTransform(self):
        return self.local_transform
    
    def setLocalTransform(self, local_transform):
        self.local_transform = local_transform
    
    def drawChildren(self, global_transform):
        for item in self.children:
            item.draw(global_transform)

class RotationNode(GroupNode):
    def __init__(self, config=None):
        super(RotationNode,self).__init__()
        self.angular_velocity = 0.1 # Just for testing. Initialize as 0 later.
        if config is None:
            self.min_angle = 0
            self.max_angle = 0
            self.angle = 0
            self.axis = [1,0,0]
            return
        limits = config.get("limits", [0, 0])
        self.min_angle = limits[0]
        self.max_angle = limits[1]
        self.angle = config.get("default", (self.min_angle + self.max_angle)*0.5)
        self.axis = config.get("axis", [1, 0, 0])
        self.update(0)
    
    def update(self, time):
        # Just for testing: constant speed pingponging within the limits.
        self.angle += self.angular_velocity * time
        if self.angle >= self.max_angle and self.angular_velocity > 0:
            self.angle = self.max_angle * 2 - self.angle
            self.angular_velocity *= -1
        if self.angle <= self.min_angle and self.angular_velocity < 0:
            self.angle = self.min_angle * 2 - self.angle
            self.angular_velocity *= -1
        
        # update the GroupNode.local_transform
        self.local_transform = transform.rotation_matrix_deg(self.angle, self.axis)
    
class MeshNode(object):
    def __init__(self):
        self.mesh=None
        
    def setMesh(self,mesh):
        self.mesh=mesh
        
    '''
    TODO: Texturerweiterung ETC
    '''

    def draw(self, transform):
        self.mesh.draw(transform)
    
