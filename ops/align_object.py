import bpy
import numpy as np
from bpy.types import Operator
from mathutils import Vector

from .align.location_get import LocationGet
from .align.location_set import LocationSet
from .align.operator_property import OperatorProperty
from .align.temp_property import TempProperty
from .align.to_active import ToActive

class UI:
    # draw UI
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
        row.prop(self, 'align_rotation_euler_axis')

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
        row = layout.row()
        row.label(text='Sort Axis')
        row.prop(self, 'distribution_sorted_axis', expand=True)
        layout.separator()
        self.draw_align_location(layout)
        if self.is_adjustment_mode:
            layout.prop(self, "distribution_adjustment_value")
        layout.row().prop(self, "distribution_mode", expand=True)

    def draw_ground(self, layout: bpy.types.UILayout):
        col = layout.column()

        col.row().prop(self, 'ground_mode', expand=True)
        # col.prop(self, 'align_to_ground_object') TODO ground object
        # col.prop_search(self, 'ground_object_name', bpy.data, 'objects')
        # col.separator(factor=2)

        row = col.row()
        row.prop(self, 'align_location')
        row = row.row()
        row.active = self.align_location
        row.prop(self, 'align_location_axis', expand=True)

    def draw_align(self, layout: bpy.types.UILayout):
        col = layout.column()

        row = col.row()
        row.label(text='X')
        row.active = ('X' in self.align_location_axis)
        row.prop(self, 'x_align_func', expand=True)

        row = col.row()
        row.label(text='Y')
        row.active = ('Y' in self.align_location_axis)
        row.prop(self, 'y_align_func', expand=True)

        row = col.row()
        row.label(text='Z')
        row.active = ('Z' in self.align_location_axis)
        row.prop(self, 'z_align_func', expand=True)

        layout.separator()
        self.draw_align_location(layout)


class AlignObject(
    Operator,
    LocationGet,
    LocationSet,
    OperatorProperty,
    TempProperty,
    ToActive,
    UI
):
    """
    对齐物体
    Ctrl    对齐旋转
    Shift   对齐缩放
    Alt     对齐位置
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

    def invoke(self, context, event):
        self.data = {'DATA': {'CO_TUPLE': [],
                              'DIMENSIONS': Vector()},
                     'CENTER': {}
                     }
        self.invoke_init_object_location(bpy.context)

        self.min_co = np.min(self.data['DATA']['CO_TUPLE'], axis=0)
        self.max_co = np.max(self.data['DATA']['CO_TUPLE'], axis=0)

        self.objs_max_min_co = self.max_co - self.min_co  # 所有所选物体的最大最小坐标
        self.objs_center_co = (self.min_co + self.max_co) / 2

        if event.ctrl or event.shift or event.alt:
            self.align_rotation = event.ctrl
            self.align_scale = event.shift
            self.align_location = event.alt
        return self.execute(context)

    def execute(self, context):
        """
        对齐物体需要数据:
            最大最小点
            边界框
            中心点
            物体尺寸
        """
        self.object_location_set_funcs(context)
        return {'FINISHED'}


class_tuples = (
    AlignObject,
)

register_class, unregister_class = bpy.utils.register_classes_factory(
    class_tuples)


def register():
    register_class()


def unregister():
    unregister_class()
