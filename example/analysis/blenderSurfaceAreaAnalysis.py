import bpy
import bmesh
from mathutils import Vector
from math import ceil

# 3D tri area ABC is half the length of AB cross product AC 
def tri_area( co1, co2, co3 ):
    return (co2 - co1).cross( co3 - co1 ).length / 2.0


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

def print_selected_area():
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
    

if __name__ == "__main__":
    print_selected_area()
    # total_extrusion = 0
    
    # target_extrusion = 1
    # extrusion_fineness = 0.01
    
    # for _ in range(ceil(target_extrusion / extrusion_fineness)):
    #     print("Extruded by " + str(total_extrusion) + ", area is now ",
    #             end="")
    #     print_selected_area()
        
    #     extrude_selected(extrusion_fineness)
    #     total_extrusion += extrusion_fineness
    #     watertight_boolean()
    #     bpy.ops.wm.save_mainfile()