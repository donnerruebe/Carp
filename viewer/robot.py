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
JOINT_TYPES = {"fixed":sceneGraph.FixedJoint,
              "revolute":sceneGraph.RevoluteJoint,
              "prismatic":sceneGraph.PrismaticJoint,
              "screw":sceneGraph.ScrewJoint}

class Robot(object):
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
        position = component.get("position",[0,0,0])
        orientation = component.get("orientation",[0,0,0])
        scale = component.get("scale",1)
        node.setBaseTransform(transform.rotation_translation_scale_matrix(orientation, position, scale))
        
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

    def __init__(self, directory, filename):
        f = open(directory + filename, "r")
        config = json.load(f)
        f.close()
        
        # TODO: Store meshes in a resource manager to allow robots to share them.
        self.meshes = {}
        meshfiles = config.get("files",())
        for meshID in meshfiles:
            self.meshes[meshID] = Mesh(directory + meshfiles.get(meshID))
        
        self.named_nodes = {}
        self.root = self.addToSceneGraph(config.get("root"))
    
    def draw(self):
        self.root.draw()
    
    def update(self, time, transfrom):
        self.root.recursiveUpdate(time, transfrom)
    
    #def ikMove(self, toolname, distance, angular_distance):
    
    def ik(self, toolname, target_position, target_orientation):
        care_about_orientation = True
        
        # Get the current tool position and orientation.
        tool = self.named_nodes.get(toolname)
        if tool is None:
            print("Invalid tool name: '{0}'".format(toolname))
            return
        tool_transform = tool.getGlobalTransform()
        tool_position = transform.translation_from_matrix(tool_transform)
        
        # Count the degrees of freedom in the tool's kinematic chain.
        kinematic_chain = tool.getKinematicChain() # TODO: Allow using only a sub-chain. (Or use weights?)
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
        
        # Figure out the difference between the tool state and the target state
        if care_about_orientation:
            target_rotation_matrix = transform.rotation_from_euler_deg(target_orientation)
            relative_rotation = np.identity(4)
            relative_rotation[:3,:3] = np.dot(target_rotation_matrix[:3,:3], tool_transform[:3,:3].transpose())
            for i in range(3):
                relative_rotation[:3,i] /= np.linalg.norm(relative_rotation[:3,i]) # transform.rotation_from_matrix cannot handle scaling.
            (angle, axis, _) = transform.rotation_from_matrix(relative_rotation)
            orientation_change = axis * angle
        position_change = target_position - tool_position
        
        # Use the pseudoinverse of the jacobian to estimate the required parameter changes.
        if care_about_orientation:
            inverse_jacobian = np.linalg.pinv(jacobian, 0.01) # NOTE: pinv's second parameter gives us extra stability at the cost of accuracy.
            delta_worldspace = np.append(position_change, orientation_change)
        else:
            inverse_jacobian = np.linalg.pinv(jacobian[:3,:], 0.01) # NOTE: pinv's second parameter gives us extra stability at the cost of accuracy.
            delta_worldspace = position_change
        delta_parameters = np.dot(inverse_jacobian, delta_worldspace)
        delta_parameters /= 10 # TEMPORARY: Make many small steps instead of one big one to improve convergence.
        
        # Update the parameters of the joints
        current_index = 0
        for joint in kinematic_chain:
            joint_mobility = joint.getMobility()
            joint.changeParameters(delta_parameters[current_index:current_index+joint_mobility])
            current_index += joint_mobility