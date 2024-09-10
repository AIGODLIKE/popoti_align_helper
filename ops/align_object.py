import bpy
from bpy.types import Operator
from mathutils import Matrix

from .align.operator_property import OperatorProperty
from .align.to_align import ToAlign
from .align.to_distribution import ToDistribution
from .align.to_ground import ToGround
from .align.to_matrix import get_matrix


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

        if self.is_adjustment_mode:
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

        # row = col.row()
        # row.prop(self, 'align_location')
        # row = row.row()
        # row.active = self.align_location
        # row.prop(self, 'align_location_axis', expand=True)

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
        self.draw_align_location(layout)


class AlignObject(
    Operator,
    OperatorProperty,
    ToGround,
    ToDistribution,
    ToAlign,
    UI
):
    """
    对齐物体
    # Ctrl    对齐旋转
    # Shift   对齐缩放
    # Alt     对齐位置
    可组合按
    """

    bl_idname = 'object.tool_kits_fast_align'
    bl_label = 'POPOTI Align Helper'
    bl_options = {'REGISTER', 'UNDO'}

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

    def cancel(self, context):
        print("calcel")

    def invoke(self, context, event):
        print("invoke")
        if event.ctrl:
            self.align_rotation = True
        if event.shift:
            self.align_scale = True
        if event.alt:
            self.align_location = True
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
            run_func(context)
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
