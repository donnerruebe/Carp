'''
Created on 25.12.2015

@author: Tilmann
'''

import json
from mesh import Mesh
import numpy as np
import transform

import sceneGraph

# TODO: Should this variable be in sceneGraph?
# Would it be acceptable to just turn the classes' names into the "joint" strings of the config file?
# Or maybe the other way around?
JOINT_TYPES = {"fixed":sceneGraph.FixedJointNode,
              "revolute":sceneGraph.RevoluteJointNode,
              "prismatic":sceneGraph.PrismaticJointNode}

class Kuka(object):
    def addToSceneGraph(self, component):
        # Instantiate a node of appropriate type.
        type_name = component.get("joint", "fixed")
        NodeType = JOINT_TYPES.get(type_name)
        if NodeType is None:
            print("Invalid node type: '{0}'".format(type_name))
            NodeType = JOINT_TYPES["fixed"]
        node = NodeType(component)
        
        # Add a mesh (or None) to the node.
        node.setMesh(self.meshes.get(component.get("mesh")))
        
        # Set the node's base transform.
        t = transform.translation_matrix(component.get("position",[0,0,0]))
        r = transform.rotation_from_euler_deg(component.get("orientation",[0,0,0]))
        node.setBaseTransform(np.dot(t,r))
        
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
    
    #def ikMove(self, toolname, distance, angular_distance):
    
    def ik(self, toolname, target_position):
        # TODO: Take a target orientation into consideration.
        # Get the current tool position.
        tool = self.named_nodes.get(toolname)
        if tool is None:
            print("Invalid tool name: '{0}'".format(toolname))
            return
        tool_position = transform.translation_from_matrix(tool.getGlobalTransform())
        
        # Count the degrees of freedom in the tool's kinematic chain.
        kinematic_chain = tool.getKinematicChain()
        chain_mobility = 0
        for joint in kinematic_chain:
            chain_mobility += joint.getMobility() # NOTE: We could pack the mobility into the kinematic_chain to save some getMobility calls.
        
        # Construct the Jacobian at the current tool position.
        output_dimensions = 6 # position & orientation
        jacobian = np.zeros(shape=(output_dimensions, chain_mobility))
        current_column = 0
        for joint in kinematic_chain:
            joint_mobility = joint.getMobility()
            if joint_mobility == 0:
                continue
            derivatives = joint.getDerivatives(tool_position)
            expected_shape = (output_dimensions, joint_mobility)
            if derivatives.shape != expected_shape:
                print("Result of 'getDerivatives' has invalid shape: received {0}, expected {1}".format(derivatives.shape, expected_shape))
                return
            jacobian[:,current_column:current_column+joint_mobility] = derivatives
            current_column += joint_mobility
        
        # Use the pseudoinverse of the jacobian to estimate the required parameter changes.
        inverse_jacobian = np.linalg.pinv(jacobian, 0.01) # NOTE: pinv's second parameter gives us extra stability at the cost of accuracy.
        delta_worldspace = np.append(target_position - tool_position, [0,0,0]) # TODO: The [0,0,0] is the desired change in orientation.
        delta_parameters = np.dot(inverse_jacobian, delta_worldspace)
        delta_parameters /= 10 # TEMPORARY: Make many small steps instead of one big one to improve convergence.
        
        # Update the parameters of the joints
        current_index = 0
        for joint in kinematic_chain:
            joint_mobility = joint.getMobility()
            joint.changeParameters(delta_parameters[current_index:current_index+joint_mobility])
            current_index += joint_mobility