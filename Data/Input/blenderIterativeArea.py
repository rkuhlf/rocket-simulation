import bpy
import bmesh
from mathutils import Vector
from math import ceil

# 3D tri area ABC is half the length of AB cross product AC 
def tri_area( co1, co2, co3 ):
    return (co2 - co1).cross( co3 - co1 ).length / 2.0

def rename(old_name, new_name):
    current_active = bpy.context.view_layer.objects.active
    
    bpy.context.view_layer.objects.active = bpy.data.objects[old_name]
    bpy.context.object.name = new_name
    
    bpy.context.view_layer.objects.active = current_active

generated_count = 0
def new_base_cube():
    """Returns reference to an object; copy of base cube"""
    global generated_count

    base_cube = bpy.data.objects['Base Cube']
    bpy.context.view_layer.objects.active = base_cube

    bpy.ops.object.duplicate_move(OBJECT_OT_duplicate={"linked":False, "mode":'TRANSLATION'}, TRANSFORM_OT_translate={"value":(0, 0, 0), "orient_type":'GLOBAL', "orient_matrix":((0, 0, 0), (0, 0, 0), (0, 0, 0)), "orient_matrix_type":'GLOBAL', "constraint_axis":(False, False, False), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_target":'CLOSEST', "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "release_confirm":False, "use_accurate":False, "use_automerge_and_split":False})

    new_name = f'Generated Copy of Base Cube {generated_count}'
    # Assuming that there are not already any copies of base cube
    rename('Base Cube.001', new_name)
    generated_count += 1

    new_cube = bpy.data.objects[new_name]

    return new_cube


def extrude_selected(extrude_length=0.1):
    bpy.ops.mesh.extrude_region_shrink_fatten(
        MESH_OT_extrude_region={"use_normal_flip": False,
                                "use_dissolve_ortho_edges": False,
                                "mirror": False},
        TRANSFORM_OT_shrink_fatten={"value": extrude_length, 
                                    "use_even_offset": False,
                                    "mirror": False,
                                    "use_proportional_edit": False,
                                    "proportional_edit_falloff": 'SMOOTH',
                                    "proportional_size": 1,
                                    "use_proportional_connected": False,
                                    "use_proportional_projected": False,
                                    "snap": False,
                                    "snap_target": 'CLOSEST',
                                    "snap_point": (0, 0, 0),
                                    "snap_align": False,
                                    "snap_normal": (0, 0, 0),
                                    "release_confirm": False,
                                    "use_accurate": False})

def get_coil_area(radius):
    # Get the object
    obj = bpy.context.object

    # Construct bmesh
    bm = bmesh.new()
    bm.from_mesh( obj.data )

    # Triangulate it so that we can calculate tri areas
    bmesh.ops.triangulate( bm, faces = bm.faces )

    # Ensure faces access
    bm.faces.ensure_lookup_table()
    
    
    total = 0

    # enumerate the faces
    for face in bm.faces:
        # Get the face area (can also be 'face.calc_area()')
        face_area = tri_area( *(v.co for v in face.verts) )
        # Get corresponding uv area
        # uv_area = tri_area( *(Vector( (*l[uv_loop].uv, 0) ) for l in face.loops) )
        # print( face.index, face_area)#, uv_area )
        total += face_area

    print(total)

def watertight_boolean():
    bpy.ops.object.editmode_toggle()
    
    # Create massive cube that is exactly as tall as the coil. The difference will prevent extrusion on ends
    
    # Difference it with coil, with self-intersection turned on
    
    # Create an equally massive cube. Difference it with the other to create final coil
    
    # Select all of the new faces
    
    bpy.ops.object.editmode_toggle()

def generate_new_coil():
    pass

if __name__ == "__main__":
    # The object you want to extrude must be named coil, and there must be a base cube with the correct height that limits the coil
    # The coil should not technically be in a helix shape. I do not think that rocket fuel grains are actually in a helix shape
    coil = bpy.data.objects['Coil']
    
    
    name = 'Scripted'

    m = base_cube.modifiers.new(name, 'BOOLEAN')
    m.object = coil
    
    bpy.ops.object.modifier_apply(modifier=name)
    

    
    
   total_extrusion = 0
   
   target_extrusion = 1
   extrusion_fineness = 0.01
   
   for _ in range(ceil(target_extrusion / extrusion_fineness)):
       print("Extruded by " + str(total_extrusion) + ", area is now ",
               end="")
       print_selected_area()
       
       extrude_selected(extrusion_fineness)
       total_extrusion += extrusion_fineness
       watertight_boolean()
       bpy.ops.wm.save_mainfile()