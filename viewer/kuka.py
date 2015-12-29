'''
Created on 25.12.2015

@author: Tilmann
'''

import json
from mesh import Mesh
from numpy import dot
import transform

import sceneGraph

# TODO: Should this variable be in sceneGraph?
# Would it be acceptable to just turn the classes' names into the "type" strings of the config file?
# Or maybe the other way around?
NODE_TYPES = {"static":sceneGraph.StaticNode, "joint":sceneGraph.JointNode, "linear":sceneGraph.LinearNode}

class Kuka(object):
    def addToSceneGraph(self, component):
        # Instantiate a node of appropriate type.
        type_name = component.get("type", "static")
        NodeType = NODE_TYPES.get(type_name)
        if NodeType is None:
            print("Invalid node type: '{0}'".format(type_name))
            NodeType = NODE_TYPES["static"]
        node = NodeType(component)
        
        # Add a mesh (or None) to the node.
        node.setMesh(self.meshes.get(component.get("mesh")))
        
        # Set the node's base transform.
        t = transform.translation_matrix(component.get("position",[0,0,0]))
        r = transform.rotation_from_euler_deg(component.get("orientation",[0,0,0]))
        node.setBaseTransform(dot(t,r))
        
        # Try to add the node to a dictionary for lookup by name.
        name = component.get("name")
        if name is None:
            pass
        elif name in self.named_nodes:
            print("Duplicate node name: '{0}'".format(name))
        else:
            self.named_nodes[name] = node
        
        # Add the children.
        for child in component.get("children",()):
            node.addChild(self.addToSceneGraph(child))
        
        return node

    def __init__(self):
        self.directory = "../resources/robots/Kuka/"
        f = open(self.directory + "config.bot", "r")
        config = json.load(f)
        f.close()
        
        self.meshes = {}
        meshfiles = config.get("files",())
        for meshID in meshfiles:
            self.meshes[meshID] = Mesh(self.directory + meshfiles.get(meshID))
        
        self.named_nodes = {}
        self.root = self.addToSceneGraph(config.get("root"))
    
    def draw(self):
        self.root.draw()
    
    def update(self, time, transfrom):
        self.root.recursiveUpdate(time, transfrom)
    
    def ik(self, toolname, target):
        # Get the tool position.
        tool = self.named_nodes.get(toolname)
        if tool is None:
            print("Invalid tool name: '{0}'".format(toolname))
            return
        tool_position = transform.translation_from_matrix(tool.getGlobalTransform())
        # Construct the Jacobian at the tool position.
        # TODO: We need a decent way to extract the kinematic chain from the scene graph.
        