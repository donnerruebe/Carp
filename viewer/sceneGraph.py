'''RotationComponent
    mesh

TranslationComponent
    mesh

PathComponent
    mesh

MESH'''

import numpy as np
import transform
from math import radians

class FixedJoint(object):
    def __init__(self, _=None):
        self.parent = None
        self.children = []
        self.mesh = None
        self.base_transform = np.identity(4)
        self.global_transform = np.identity(4)

    def addChild(self, obj):
        if obj.parent is not None:
            print("Tried to add a child, which already has a parent.")
            return
        obj.parent = self
        self.children.append(obj)
    
    def setMesh(self, mesh):
        self.mesh = mesh

    def setBaseTransform(self, base_transform):
        self.base_transform = base_transform
    
    def getGlobalTransform(self):
        return self.global_transform
    
    def draw(self):
        if self.mesh is not None:
            self.mesh.draw(self.global_transform)
        for child in self.children:
            child.draw()
    
    def recursiveUpdate(self, time, parent_transform):
        self.update(time, parent_transform)
        for child in self.children:
            child.recursiveUpdate(time, self.global_transform)
    
    def update(self, time, parent_transfrom):
        self.global_transform = np.dot(parent_transfrom, self.base_transform)
    
    def getKinematicChain(self):
        if self.parent is None:
            return [self]
        else:
            chain = self.parent.getKinematicChain()
            chain.append(self)
            return chain
    
    def getMobility(self):
        return 0
    
    def getDerivatives(self, _):
        pass
    
    def changeParameters(self, _):
        pass

class RevoluteJoint(FixedJoint):
    def __init__(self, config={}):
        super(type(self),self).__init__()
        self.angular_velocity = 0.01 # Just for testing. Initialize as 0 later.
        limits = config.get("limits", [0, 0])
        self.min_angle = limits[0]
        self.max_angle = limits[1]
        self.angle = config.get("default", (self.min_angle + self.max_angle)*0.5)
        self.axis = config.get("axis", [1, 0, 0])
        self.axis /= np.linalg.norm(self.axis)
    
    def update(self, time, parent_transfrom):
        # Just for testing: constant speed pingponging within the limits.
        '''self.angle += self.angular_velocity * time
        if self.angle >= self.max_angle and self.angular_velocity > 0 \
        or self.angle <= self.min_angle and self.angular_velocity < 0:
            self.angular_velocity *= -1'''
        
        rotation = transform.rotation_matrix_deg(self.angle, self.axis)
        local_transform = np.dot(self.base_transform, rotation)
        self.global_transform = np.dot(parent_transfrom, local_transform)
        
    def getMobility(self):
        return 1
    
    def getDerivatives(self, point):
        angular_velocity = np.dot(self.global_transform[:3,:3], self.axis)
        angular_velocity *= radians(1) # , because we're using degrees instead of radians for self.angle.
        global_position = transform.translation_from_matrix(self.global_transform)
        displacement = point - global_position
        velocity = np.cross(angular_velocity, displacement)
        derivatives = np.append(velocity, angular_velocity)
        return np.expand_dims(derivatives, axis=1)
    
    def changeParameters(self, delta):
        self.angle = min(max(self.angle + delta[0], self.min_angle), self.max_angle)

class PrismaticJoint(FixedJoint):
    def __init__(self, config={}):
        super(type(self),self).__init__()
        self.velocity = 0.001 # Just for testing. Initialize as 0 later.
        limits = config.get("limits", [0, 0])
        self.min_displacement = limits[0]
        self.max_displacement = limits[1]
        self.displacement = config.get("default", (self.min_displacement + self.max_displacement)*0.5)
        self.direction = np.array(config.get("direction", [1, 0, 0]), dtype=np.float64)
        self.direction /= float(np.linalg.norm(self.direction))
    
    def update(self, time, parent_transfrom):
        # Just for testing: constant speed pingponging within the limits.
        '''self.displacement += self.velocity * time
        if self.displacement >= self.max_displacement and self.velocity > 0 \
        or self.displacement <= self.min_displacement and self.velocity < 0:
            self.velocity *= -1'''
        
        translation = transform.translation_matrix(self.direction * self.displacement)
        local_transform = np.dot(self.base_transform, translation)
        self.global_transform = np.dot(parent_transfrom, local_transform)
        
    def getMobility(self):
        return 1
    
    def getDerivatives(self, point):
        velocity = np.dot(self.global_transform[:4,:3], np.append(self.direction,[1]))
        derivatives = np.append(velocity, [0,0,0])
        return np.expand_dims(derivatives, axis=1)
    
    def changeParameters(self, delta):
        self.displacement = min(max(self.angle + delta[0], self.min_displacement), self.max_displacement)

class ScrewJoint(FixedJoint):
    def __init__(self, config={}):
        super(type(self),self).__init__()
        self.angular_velocity = 0.01 # Just for testing. Initialize as 0 later.
        limits = config.get("limits", [0, 0])
        self.min_angle = limits[0]
        self.max_angle = limits[1]
        self.angle = config.get("default", (self.min_angle + self.max_angle)*0.5)
        self.axis = config.get("axis", [1, 0, 0])
        self.axis /= np.linalg.norm(self.axis)
        self.lead = config.get("lead", 0) # Axial motion per turn.
    
    def update(self, time, parent_transfrom):
        # Just for testing: constant speed pingponging within the limits.
        '''self.angle += self.angular_velocity * time
        if self.angle >= self.max_angle and self.angular_velocity > 0 \
        or self.angle <= self.min_angle and self.angular_velocity < 0:
            self.angular_velocity *= -1'''
        
        rotation = transform.rotation_matrix_deg(self.angle, self.axis)
        displacement = self.angle / 360.0 * self.lead 
        translation = transform.translation_matrix(self.axis * displacement)
        local_transform = np.dot(self.base_transform, np.dot(rotation, translation))
        self.global_transform = np.dot(parent_transfrom, local_transform)
        
    def getMobility(self):
        return 1
    
    def getDerivatives(self, point):
        angular_velocity = np.dot(self.global_transform[:3,:3], self.axis)
        angular_velocity *= radians(1) # , because we're using degrees instead of radians for self.angle.
        global_position = transform.translation_from_matrix(self.global_transform)
        displacement = point - global_position
        velocity = np.cross(angular_velocity, displacement) + self.lead / 360.0
        derivatives = np.append(velocity, angular_velocity)
        return np.expand_dims(derivatives, axis=1)
    
    def changeParameters(self, delta):
        self.angle = min(max(self.angle + delta[0], self.min_angle), self.max_angle)