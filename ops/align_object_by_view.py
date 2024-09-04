from bpy.types import Operator


class ObjectAlignByView(Operator):
    bl_idname = "object.object_align_by_view"
    bl_label = "Object Align by View"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        return {"FINISHED"}
