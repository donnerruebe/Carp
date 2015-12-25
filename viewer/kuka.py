'''
Created on 25.12.2015

@author: Tilmann
'''

import json
from sceneGraph import GroupNode, MeshNode
from mesh import Mesh
import translation

class Kuka(object):
    '''
    classdocs
    '''

    def addToSceneGraph(self, component):
        node = GroupNode()
        mesh = MeshNode()
        mesh.setMesh(self.meshes[component.get("mesh")])
        node.addNode(mesh)
        t = translation.translation_matrix(component.get("position",[0,0,0]))
        node.setDefaultMatrix(t)
        r = translation.rotation_from_euler(component.get("orientation",[0,0,0]))
        node.setMatrix(r)
        print node.getMatrix()
        for child in component.get("children"):
            node.addNode(self.addToSceneGraph(child))
        return node

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
        
        self.root = self.addToSceneGraph(config.get("root"))
    
    def draw(self, matrix):
        self.root.draw(matrix)
