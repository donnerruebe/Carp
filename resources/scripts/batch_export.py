# exports each selected object into its own file

import bpy
import os
from struct import pack

# export to blend file location
basedir = os.path.dirname(bpy.data.filepath)

if not basedir:
    raise Exception("Blend file is not saved")

scene = bpy.context.scene

obj_active = scene.objects.active
selection = bpy.context.selected_objects

bpy.ops.object.select_all(action='DESELECT')

for obj in selection:
    if obj.type == 'MESH':
        mesh = obj.data
        
        num_verts = len(mesh.vertices)
        if num_verts == 0:
            continue
        
        name = bpy.path.clean_name(obj.name) + '.mesh'
        fn = os.path.join(basedir, name)
        f = open(fn, 'wb')
        
        # write number of vertices and triangles
        num_tris = 0
        for poly in mesh.polygons:
            num_tris += len(poly.vertices) - 2
        f.write(pack('2I', num_verts, num_tris))
        
        '''# write triangle data
        for poly in mesh.polygons:
            print("Polygon", poly.index, "from loop index", poly.loop_start, "and length", poly.loop_total)
            for loop_index in poly.loop_indices: # <-- python Range object with the proper indices already set
                loop = mesh.loops[loop_index] # The loop entry this polygon point refers to
                vertex = mesh.vertices[loop.vertex_index] # The vertex data that loop entry refers to
                f.write(pack('I', num_tris))
                print("\tLoop index", loop.index, "points to vertex index", loop.vertex_index, "at position", vertex.co)
                for j,uv_layer in enumerate(mesh.uv_layers):
                    print("\t\tUV Map", j, "has coordinates", uv_layer.data[loop.index].uv, "for this loop index")'''
        
        # write vertex data
        for vert in mesh.vertices:
            f.write(pack('3f', vert.co.x, vert.co.y, vert.co.z))
            f.write(pack('3f', vert.normal.x, vert.normal.y, vert.normal.z))
        
        # write triangle data
        for poly in mesh.polygons:
            uv_layer = mesh.uv_layers.active.data
            for i in range(0, len(poly.vertices) - 2):
                f.write(pack('3I', poly.vertices[0], poly.vertices[i+1], poly.vertices[i+2]))
                uv0 = uv_layer[poly.loop_indices[0]].uv
                uv1 = uv_layer[poly.loop_indices[i+1]].uv
                uv2 = uv_layer[poly.loop_indices[i+2]].uv
                f.write(pack('6f', uv0.x, uv0.y, uv1.x, uv1.y, uv2.x, uv2.y))
        
        f.close()
        print("written:", fn)


scene.objects.active = obj_active

for obj in selection:
    obj.select = True
