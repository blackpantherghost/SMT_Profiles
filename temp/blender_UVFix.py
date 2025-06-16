import bpy
import bmesh
from bpy.props import BoolProperty

def get_overlap_faces(obj):
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.uv.select_all(action='DESELECT')
    bpy.context.tool_settings.use_uv_select_sync = False
    bpy.ops.uv.select_overlap()

    bm = bmesh.from_edit_mesh(obj.data)
    uv_layer = bm.loops.layers.uv.verify()
    bm.faces.ensure_lookup_table()

    overlap_face_indices = [
        face.index for face in bm.faces
        if any(loop[uv_layer].select for loop in face.loops)
    ]
    return overlap_face_indices

def pin_non_overlapping(obj, overlap_face_indices):
    bm = bmesh.from_edit_mesh(obj.data)
    uv_layer = bm.loops.layers.uv.verify()
    bm.faces.ensure_lookup_table()

    for face in bm.faces:
        if face.index not in overlap_face_indices:
            for loop in face.loops:
                loop[uv_layer].pin_uv = True

    bmesh.update_edit_mesh(obj.data)

def unwrap_overlaps(obj, overlap_face_indices):
    bm = bmesh.from_edit_mesh(obj.data)
    uv_layer = bm.loops.layers.uv.verify()
    bm.faces.ensure_lookup_table()

    # Deselect all faces
    for face in bm.faces:
        face.select_set(False)

    # Select overlapping faces using their indices
    for face_index in overlap_face_indices:
        face = bm.faces[face_index]
        face.select_set(True)

    # Commit changes before using bpy.ops
    bmesh.update_edit_mesh(obj.data, loop_triangles=False, destructive=False)

    # Clear pins and unwrap selected
    bpy.ops.uv.pin(clear=True)
    bpy.ops.uv.unwrap(method='ANGLE_BASED', margin=0.001)


def select_uv_vertices_only(obj, overlap_face_indices):
    bm = bmesh.from_edit_mesh(obj.data)
    uv_layer = bm.loops.layers.uv.verify()
    bm.faces.ensure_lookup_table()

    # Deselect all
    for face in bm.faces:
        for loop in face.loops:
            loop[uv_layer].select = False

    # Select only overlapping
    for idx in overlap_face_indices:
        face = bm.faces[idx]
        for loop in face.loops:
            loop[uv_layer].select = True

    bmesh.update_edit_mesh(obj.data)

def pack_selected_uvs(obj):
    bpy.ops.uv.select_all(action='SELECT')  # Select everything
    bpy.context.tool_settings.use_uv_select_sync = False

    # Show progress in status bar
    wm = bpy.context.window_manager
    wm.progress_begin(0, 100)
    wm.progress_update(20)

    try:
        # for face in bm.faces:
        #     face.select_set(True)
        bpy.ops.mesh.select_all(action='SELECT')

        bpy.ops.uv.pack_islands(margin=0.001, pin=True)  # Keep pinned UVs in place
        wm.progress_update(100)
    except Exception as e:
        print("Packing failed:", e)
    finally:
        wm.progress_end()

# Detect & Fix Operator
class UV_OT_DetectAndFix(bpy.types.Operator):
    bl_idname = "uv.detect_and_fix"
    bl_label = "Detect & Fix UVs"
    bl_description = "Detect overlapping UVs and fix if enabled"
    bl_options = {'REGISTER', 'UNDO'}

    fix_uvs: BoolProperty(name="Fix UVs", default=True)
    show_status: BoolProperty(name="Show Status Only", default=False)

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Select a mesh object")
            return {'CANCELLED'}

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.context.tool_settings.use_uv_select_sync = False
        overlap_faces = get_overlap_faces(obj)

        if not overlap_faces:
            self.report({'INFO'}, "No overlapping UVs found")
            return {'FINISHED'}

        pin_non_overlapping(obj, overlap_faces)

        if self.show_status:
            select_uv_vertices_only(obj, overlap_faces)
            self.report({'INFO'}, "UV overlap detected. Vertices selected.")
            return {'FINISHED'}

        if self.fix_uvs:
            unwrap_overlaps(obj, overlap_faces)
            self.report({'INFO'}, "Overlapping UVs unwrapped.")
            return {'FINISHED'}

        return {'CANCELLED'}

# Pack UVs Operator
class UV_OT_PackSelected(bpy.types.Operator):
    bl_idname = "uv.pack_selected_uvs"
    bl_label = "Pack Overlapping UVs"
    bl_description = "Pack UVs while keeping pinned islands fixed"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        obj = context.active_object
        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "Select a mesh object")
            return {'CANCELLED'}

        bpy.ops.object.mode_set(mode='EDIT')
        bpy.context.tool_settings.use_uv_select_sync = False

        self.report({'INFO'}, "Packing UVs (pinned kept in place)...")
        pack_selected_uvs(obj)
        self.report({'INFO'}, "Packing complete.")
        return {'FINISHED'}


# UI Panel
class UV_PT_CustomPanel(bpy.types.Panel):
    bl_label = "Auto UV Fixer"
    bl_idname = "UV_PT_custom_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'

    def draw(self, context):
        layout = self.layout
        layout.label(text="UV Overlap Tools")
        layout.operator("uv.detect_and_fix", text="Detect Only").fix_uvs = False
        layout.operator("uv.detect_and_fix", text="Fix Overlaps").fix_uvs = True
        layout.operator("uv.detect_and_fix", text="Show Status Only").show_status = True
        layout.separator()
        layout.operator("uv.pack_selected_uvs", text="Pack Selected Overlaps")

# Register
classes = [
    UV_OT_DetectAndFix,
    UV_OT_PackSelected,
    UV_PT_CustomPanel
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
