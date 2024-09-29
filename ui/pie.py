import bpy
from bpy.types import Menu

from ..ops import ObjectAlignByView as view
from .panel import (
    draw_ground,
    draw_distribution_y,
    draw_distribution_x,
    draw_center_align,
    draw_fall
)
from ..utils import screen_relevant_direction_3d_axis


class AlignPieMenu(Menu):
    bl_label = 'POPOTI Align Helper'
    bl_idname = 'VIEW3D_MT_PIE_POPOTI_ALIGN_HELPER'

    def draw(self, context):
        layout = self.layout
        item = view._item_
        pie = layout.menu_pie()
        item(pie, 'Align_Left', False, ops=False)
        item(pie, 'Align_Right', False, ops=False)
        item(pie, 'Align_Down', False, ops=False)
        item(pie, 'Align_Up', False, ops=False)

        direction = screen_relevant_direction_3d_axis(context)
        (x, x_), (y, y_) = direction
        draw_distribution_y(pie, y)

        col = pie.column(align=True)
        col.scale_y = 1.3
        draw_center_align(col, direction)

        draw_distribution_x(pie, x)

        col = pie.column(align=True)
        col.scale_y = 1.6
        draw_fall(col)
        draw_ground(col)


def register():
    bpy.utils.register_class(AlignPieMenu)


def unregister():
    bpy.utils.unregister_class(AlignPieMenu)
