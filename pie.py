import bpy
from bpy.types import Menu

from .panel import set_axis
from .utils import screen_relevant_direction_3d_axis


class VIEW3D_MT_PIE_POPOTI_ALIGN_HELPER(Menu):
    bl_label = "Select Mode"

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()
        (x, x_), (y, y_) = screen_relevant_direction_3d_axis(context)
        set_axis(pie, {x_}, 'Align_Left')
        set_axis(pie, {x}, 'Align_Right')
        set_axis(pie, {y_}, 'Align_Down')
        set_axis(pie, {y}, 'Align_Up')
        pie.column().label(text="a")
        pie.column().label(text="b")
        pie.column().label(text="c")
        pie.column().label(text="d")


def register():
    bpy.utils.register_class(VIEW3D_MT_PIE_POPOTI_ALIGN_HELPER)


def unregister():
    bpy.utils.unregister_class(VIEW3D_MT_PIE_POPOTI_ALIGN_HELPER)
