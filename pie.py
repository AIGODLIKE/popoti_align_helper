import bpy
from bpy.types import Menu

from .panel import (set_axis, draw_ground,
                    draw_cursor_active_original,
                    draw_distribution_y, draw_distribution_x,
                    draw_center_align)
from .utils import screen_relevant_direction_3d_axis


class AlignPieMenu(Menu):
    bl_label = 'POPOTI Align Helper'
    bl_idname = 'VIEW3D_MT_PIE_POPOTI_ALIGN_HELPER'

    def draw(self, context):
        layout = self.layout

        pie = layout.menu_pie()
        (x, x_), (y, y_) = direction = screen_relevant_direction_3d_axis(context)
        set_axis(pie, {x_}, 'Align_Left')
        set_axis(pie, {x}, 'Align_Right')
        set_axis(pie, {y_}, 'Align_Down')
        set_axis(pie, {y}, 'Align_Up')

        draw_distribution_y(pie, y)

        col = pie.column(align=True)
        col.scale_y = 1.3
        draw_center_align(col, direction)

        draw_distribution_x(pie, x)

        col = pie.column(align=True)
        col.scale_y = 1.3
        draw_ground(col)
        draw_cursor_active_original(col)


def register():
    bpy.utils.register_class(AlignPieMenu)


def unregister():
    bpy.utils.unregister_class(AlignPieMenu)
