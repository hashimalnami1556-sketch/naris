bl_info = {
    "name": "NARIS Production Bridge",
    "author": "NARIS Studios",
    "version": (1, 0, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > NARIS",
    "description": "NARIS asset naming, metadata, LOD and validation helpers.",
    "category": "3D View",
}

import bpy

class NARIS_OT_setup_asset(bpy.types.Operator):
    bl_idname = "naris.setup_asset"
    bl_label = "Setup NARIS Asset"
    def execute(self, context):
        obj = context.active_object
        if obj is None:
            self.report({'ERROR'}, "Select an object first")
            return {'CANCELLED'}
        if not obj.get("naris_asset_id"):
            obj["naris_asset_id"] = obj.name
        obj["naris_category"] = "Character"
        obj["naris_export"] = "GLB,FBX"
        obj["naris_version"] = "1.0"
        obj["naris_engine_target"] = "Unity 6"
        obj["naris_lod0"] = 1.0
        obj["naris_lod1"] = 0.60
        obj["naris_lod2"] = 0.30
        obj["naris_collision"] = f"{obj.name}_COL"
        self.report({'INFO'}, "NARIS metadata added")
        return {'FINISHED'}

class NARIS_OT_validate(bpy.types.Operator):
    bl_idname = "naris.validate"
    bl_label = "Validate NARIS Asset"
    def execute(self, context):
        obj = context.active_object
        if obj is None:
            self.report({'ERROR'}, "No active object")
            return {'CANCELLED'}
        required = ["naris_asset_id", "naris_category", "naris_export", "naris_version", "naris_engine_target"]
        missing = [key for key in required if not obj.get(key)]
        if missing:
            self.report({'ERROR'}, "Missing: " + ", ".join(missing))
        else:
            self.report({'INFO'}, f"VALID NARIS ASSET: {obj.get('naris_asset_id')}")
        return {'FINISHED'}

class NARIS_PT_panel(bpy.types.Panel):
    bl_label = "NARIS Production Bridge"
    bl_idname = "NARIS_PT_production_bridge"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "NARIS"
    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        if obj:
            box = layout.box()
            box.label(text=f"Asset: {obj.get('naris_asset_id', 'Not configured')}")
            box.label(text="Category: " + str(obj.get('naris_category', '—')))
            box.label(text="Engine: " + str(obj.get('naris_engine_target', '—')))
            layout.operator("naris.setup_asset", icon='OBJECT_DATA')
            layout.operator("naris.validate", icon='CHECKMARK')
        else:
            layout.label(text="Select an object first.")

classes = (NARIS_OT_setup_asset, NARIS_OT_validate, NARIS_PT_panel)
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
if __name__ == "__main__":
    register()
