import bpy
import bmesh
from mathutils import Vector

# Extrude selected faces along normals

# Find area

# 3D tri area ABC is half the length of AB cross product AC 
def tri_area( co1, co2, co3 ):
    return (co2 - co1).cross( co3 - co1 ).length / 2.0

# Get the object
obj = bpy.context.object

# Construct bmesh
bm = bmesh.new()
bm.from_mesh( obj.data )

# Triangulate it so that we can calculate tri areas
bmesh.ops.triangulate( bm, faces = bm.faces )

# Ensure faces access
bm.faces.ensure_lookup_table()

# Get the uv map
#uv_loop = bm.loops.layers.uv['UVMap']

total = 0

# enumerate the faces
for face in bm.faces:
    print(face.select)
    
    # Get the face area (can also be 'face.calc_area()')
    face_area = tri_area( *(v.co for v in face.verts) )
    # Get corresponding uv area
#    uv_area = tri_area( *(Vector( (*l[uv_loop].uv, 0) ) for l in face.loops) )
    print( face.index, face_area)#, uv_area )
    total += face_area
    
print(total)