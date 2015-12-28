'''
Created on 25.12.2015

@author: Tilmann
'''

import json
from mesh import Mesh
from numpy import dot
import transform

import sceneGraph
CONSTRAINT_TYPES = {"rotation":sceneGraph.RotationNode, "no type":None}

class Kuka(object):
    '''
    classdocs
    '''

    def addToSceneGraph(self, component):
        # Add a constant transform node.
        first_node = sceneGraph.GroupNode()
        mesh = sceneGraph.MeshNode()
        mesh.setMesh(self.meshes[component.get("mesh")])
        first_node.addChild(mesh)
        t = transform.translation_matrix(component.get("position",[0,0,0]))
        r = transform.rotation_from_euler_deg(component.get("orientation",[0,0,0]))
        first_node.setLocalTransform(dot(t,r))
        
        # Add all children to the node.
        for child in component.get("children"):
            first_node.addChild(self.addToSceneGraph(child))
        
        # Prepend a chain of IK nodes.
        for constraint in component.get("constraints",()):
            # Get the constraints sceneGraph type.
            constraint_typename = constraint.get("type", "no type")
            constraint_type = CONSTRAINT_TYPES.get(constraint_typename)
            if constraint_type is None:
                print "Invalid constraint type '{0}'.".format(constraint_typename)
                continue
            
            # Insert the constraint into the node chain.
            constraint_node = constraint_type(constraint)
            constraint_node.addChild(first_node)
            first_node = constraint_node
            
            # Make the constraint accessible by name.
            constraint_name = constraint.get("name")
            if constraint_name is None:
                print "Missing constraint name."
            elif constraint_name in self.constraints:
                print "Duplicate constraint name '{0}'.".format(constraint_name)
            else:
                self.constraints[constraint_name] = constraint
        
        return first_node

    def __init__(self):
        '''
        Constructor
        '''
        self.directory = "../resources/robots/Kuka/"
        f = open(self.directory + "config.bot", "r")
        config = json.load(f)
        f.close()
        
        self.meshes = {}
        meshfiles = config.get("files",())
        for meshID in meshfiles:
            self.meshes[meshID] = Mesh(self.directory + meshfiles.get(meshID))
        
        self.constraints = {}
        self.root = self.addToSceneGraph(config.get("root"))
        print self.constraints
    
    def draw(self, matrix):
        self.root.draw(matrix)
