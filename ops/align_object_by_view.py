import bpy
from bpy.props import EnumProperty
from bpy.types import Operator

from ..utils import screen_relevant_direction_3d_axis


class ObjectAlignByView(Operator):
    bl_idname = 'object.object_align_by_view'
    bl_label = 'Object Align by View'
    bl_options = {'REGISTER', 'UNDO'}

    align_mode: EnumProperty(
        name="Align Mode",
        items=[
            ("Align_Left_Up", "Left Up", ""),
            ("Align_Up", "Up", ""),
            ("Align_Right_Up", "Right Up", ""),
            ("Align_Left", "Left", ""),
            ("Align_Center", "Center", ""),
            ("Align_Right", "Right", ""),
            ("Align_Left_Down", "Left Down", ""),
            ("Align_Down", "Down", ""),
            ("Align_Right_Down", "Right Down", ""),
        ]
    )

    @classmethod
    def poll(cls, context):
        return context.selected_objects.__len__()

    def draw(self, context):
        ObjectAlignByView.draw_nine_square_box(self.layout, True, self)

    @staticmethod
    def draw_nine_square_box(layout: bpy.types.UILayout, show_text=False, ops=None):
        """绘制对齐九宫格"""
        col = layout.column(align=True)
        args = dict(
            show_text=show_text,
            ops=ops
        )

        row = col.row(align=True)
        ObjectAlignByView._item_(row, 'Align_Left_Up', **args)
        ObjectAlignByView._item_(row, 'Align_Up', **args)
        ObjectAlignByView._item_(row, 'Align_Right_Up', **args)

        row = col.row(align=True)
        ObjectAlignByView._item_(row, 'Align_Left', **args)
        ObjectAlignByView._item_(row, 'Align_Center', **args)
        ObjectAlignByView._item_(row, 'Align_Right', **args)

        row = col.row(align=True)
        ObjectAlignByView._item_(row, 'Align_Left_Down', **args)
        ObjectAlignByView._item_(row, 'Align_Down', **args)
        ObjectAlignByView._item_(row, 'Align_Right_Down', **args)

    @staticmethod
    def _item_(layout: bpy.types.Operator, identifier, show_text, ops):
        from ..res.icons import get_icon
        text = identifier.replace('Align_', '').replace('_', ' ') if show_text else ''
        if ops:
            layout.context_pointer_set('ops', ops)
            o = layout.operator('wm.context_set_enum',
                                icon_value=get_icon(identifier),
                                text=text)
            o.data_path = 'ops.align_mode'
            o.value = identifier
        else:
            layout.operator(
                ObjectAlignByView.bl_idname,
                icon_value=get_icon(identifier),
                text=text
            ).align_mode = identifier

    def execute(self, context):
        context.view_layer.update()
        (x, x_), (y, y_) = screen_relevant_direction_3d_axis(context)
        axis_items = {
            'Align_Left_Up': {x_, y},
            'Align_Up': {y},
            'Align_Right_Up': {x, y},
            'Align_Left': {x_},
            'Align_Right': {x},
            'Align_Left_Down': {x_, y_},
            'Align_Down': {y_},
            'Align_Right_Down': {x, y_},

            'Align_Center': {'X', 'Y', 'Z'}
        }
        axis = axis_items[self.align_mode]
        args = dict(align_mode='ALIGN')

        for i in axis:
            value = 'MIN' if len(i) >= 2 else 'MAX'
            if self.align_mode == 'Align_Center':
                value = 'CENTER'
            args[f'align_{i[-1].lower()}_method'] = value
        args['align_location_axis'] = {i[-1] for i in axis}
        args['align_location'] = True

        context.view_layer.update()
        bpy.ops.object.tool_kits_fast_align(**args)
        context.view_layer.update()
        return {'FINISHED'}
