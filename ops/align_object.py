import bpy
from bpy.types import Operator
from mathutils import Matrix

from .align.operator_property import OperatorProperty
from .align.to_align import ToAlign
from .align.to_distribution import ToDistribution
from .align.to_ground import ToGround
from .align.to_matrix import get_matrix
from ..utils import translate_lines_text


class UI:
    def draw_align_location(self, layout):
        row = layout.row()
        row.prop(self, 'align_location')
        row = row.row()
        row.active = self.align_location
        row.row().prop(self, 'align_location_axis')

    def draw_original(self, layout: bpy.types.UILayout):
        row = layout.row()
        row.prop(self, 'align_rotation')
        row = row.row()
        row.active = self.align_rotation
        row.prop(self, 'align_rotation_axis')

        row = layout.row()
        row.prop(self, 'align_scale')
        row = row.row()
        row.active = self.align_scale
        row.prop(self, 'align_scale_axis')

        self.draw_align_location(layout)

    def draw_active(self, layout: bpy.types.UILayout):
        self.draw_original(layout)

    def draw_cursor(self, layout: bpy.types.UILayout):
        self.draw_original(layout)

    def draw_distribution(self, layout: bpy.types.UILayout):
        col = layout.column(align=True)
        row = col.row()
        row.label(text='Sort Axis')
        row.prop(self, 'distribution_sorted_axis', expand=True)
        layout.separator()

        row = col.row()
        row.label(text='Location')
        row.prop(self, 'align_location_axis')

        if self.distribution_mode == "ADJUSTMENT":
            layout.prop(self, "distribution_adjustment_value")
        layout.row().prop(self, "distribution_mode", expand=True)

    def draw_ground(self, layout: bpy.types.UILayout):
        col = layout.column(align=True)
        pm = self.ground_plane_mode

        if pm != "RAY_CASTING":
            col.label(text="Down Mode")
            col.row().prop(self, 'ground_down_mode', expand=True)
        else:
            col.prop(self, "ground_ray_casting_rotation")

        col.separator()
        if self.ground_plane_mode == "DESIGNATED_OBJECT":
            c = col.column(align=True)
            c.alert = bool(getattr(bpy.data.objects, "ground_object_name", False))
            c.prop_search(self, 'ground_object_name', bpy.context.scene, 'objects')

        col.label(text="Ground Plane Mode")
        col.prop(self, 'ground_plane_mode', expand=True)
        col.separator(factor=2)

    def draw_align(self, layout: bpy.types.UILayout):
        col = layout.column()

        row = col.row()
        row.label(text='X')
        row.active = ('X' in self.align_location_axis)
        row.prop(self, 'align_x_method', expand=True)

        row = col.row()
        row.label(text='Y')
        row.active = ('Y' in self.align_location_axis)
        row.prop(self, 'align_y_method', expand=True)

        row = col.row()
        row.label(text='Z')
        row.active = ('Z' in self.align_location_axis)
        row.prop(self, 'align_z_method', expand=True)

        layout.separator()
        layout.row().prop(self, 'align_location_axis')


class AlignObject(
    Operator,
    OperatorProperty,
    ToGround,
    ToDistribution,
    ToAlign,
    UI
):
    bl_idname = 'object.tool_kits_fast_align'
    bl_label = 'POPOTI Align Helper'
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def description(cls, context, properties):
        mode = properties.align_mode
        axis = "  ".join([f'{a.upper()}:{getattr(properties, f"align_{a.lower()}_method")}' for a in
                          properties.align_location_axis]) if properties.align_location else []

        key_tips = [
            "",
            "Ctrl: only location",
            "Shift: only rotation",
        ]

        if mode == "ORIGINAL":
            return translate_lines_text("Alignment to the origin (world axis)", *key_tips)
        elif mode == "ACTIVE":
            return translate_lines_text(
                "Aligns the selected object to the active item",
                "if there is no active item, it will be aligned to the first item in the selected list",
                *key_tips
            )
        elif mode == "CURSOR":
            return translate_lines_text("Align selected objects to the cursor", *key_tips)
        elif mode == "ALIGN":
            return translate_lines_text("Calculate the bounding box of all selected objects",
                                        "aligning them according to the selected axes and the alignment of each axis",
                                        axis,
                                        *key_tips,
                                        )
        elif mode == "GROUND":
            plane = properties.ground_plane_mode
            if plane == "GROUND":
                return translate_lines_text("Align to the ground (world Z-axis 0)", *key_tips)
            elif plane == "RAY_CASTING":
                return translate_lines_text(
                    "Project the light down through the center of the object's bounding box",
                    "and if it can be projected onto the object, align the object to the projection point",
                    *key_tips
                )
            # elif plane == "DESIGNATED_OBJECT": #这个选项应该不会用到
        elif mode == "DISTRIBUTION":
            distribution_mode = properties.distribution_mode
            if distribution_mode == "FIXED":
                return translate_lines_text(
                    "Distributed alignment, where a large bounding box is calculated for all objects",
                    "and within the bounding box, "
                    "objects are aligned according to the total length of all "
                    "objects so that each object is equally spaced",
                    *key_tips
                )
            elif distribution_mode == "ADJUSTMENT":
                return translate_lines_text(
                    "Distributed alignment, where the smallest object is fixed at the coordinates",
                    "and the position of each object is arranged "
                    "at a set spacing so that each object is equally spaced",
                    *key_tips
                )
        return "Align Object"

    @classmethod
    def poll(cls, context):
        return context.selected_objects.__len__()

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        run_func = getattr(self, f'draw_{self.align_mode.lower()}', None)
        if run_func:
            run_func(col)
        col.column().prop(self, 'align_mode', expand=True)

    def invoke(self, context, event):
        if event.ctrl or event.shift or event.alt:
            self.align_rotation = event.ctrl
            self.align_scale = event.shift
            self.align_location = event.alt
            self.align_location_axis = self.align_rotation_axis = self.align_scale_axis = {"X", "Y", "Z"}
        return self.execute(context)

    def execute(self, context):
        """
        对齐物体需要数据:
            最大最小点
            边界框
            中心点
            物体尺寸
        """
        run_func = getattr(self, f'align_to_{self.align_mode.lower()}', None)
        if run_func:
            context.view_layer.update()
            context.view_layer.update()
            run_func(context)
            context.view_layer.update()
            context.view_layer.update()
        return {'FINISHED'}

    def align_to_original(self, context):
        for obj in context.selected_objects:
            mat = get_matrix(self, obj.matrix_world, Matrix())
            context.view_layer.update()
            obj.matrix_world = mat
            context.view_layer.update()

    def align_to_active(self, context):
        for obj in context.selected_objects:
            mat = get_matrix(self, obj.matrix_world, context.active_object.matrix_world)
            context.view_layer.update()
            obj.matrix_world = mat
            context.view_layer.update()

    def align_to_cursor(self, context):
        for obj in context.selected_objects:
            mat = get_matrix(self, obj.matrix_world, context.scene.cursor.matrix)
            context.view_layer.update()
            obj.matrix_world = mat
            context.view_layer.update()


class_tuples = (
    AlignObject,
)

register_class, unregister_class = bpy.utils.register_classes_factory(class_tuples)


def register():
    register_class()


def unregister():
    unregister_class()
