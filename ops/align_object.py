import bpy
import numpy as np
from bpy.types import Operator
from mathutils import Vector

from .align.location_get import LocationGet
from .align.location_set import LocationSet
from .align.operator_property import OperatorProperty
from .align.temp_property import TempProperty
from .align.to_active import ToActive
from .align.ui import UI


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
