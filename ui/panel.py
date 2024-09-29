import bpy
from bpy.types import Panel

from ..ops import AlignObject
from ..res.icons import get_icon
from ..utils import screen_relevant_direction_3d_axis

AXIS = ('X', 'Y', 'Z')


def set_axis(layout, axis, icon, center=False):
    row = layout.row()
    op = row.operator(
        AlignObject.bl_idname,
        icon_value=get_icon(icon),
        text='',
    )
    op.align_mode = 'ALIGN'

    if axis == 'CENTER':
        center = True
        axis = ('X', 'Y', 'Z')
    for i in axis:
        value = 'MIN' if len(i) >= 2 else 'MAX'
        if center:
            value = 'CENTER'
        setattr(op, f'align_{i[-1].lower()}_method', value)
    a = {i[-1] for i in axis}
    row.label(text=str(a))
    op.align_mode = 'ALIGN'
    op.align_location = True
    op.align_location_axis = a


def set_text(text: str):
    from ..utils import get_pref
    pref = get_pref()
    if pref.show_text:
        return text
    return ""


def get_center_align(layout, icon):
    operator = layout.operator(AlignObject.bl_idname,
                               icon_value=get_icon(icon),
                               text='',
                               )
    operator.align_mode = 'ALIGN'
    operator.align_location = True
    for i in AXIS:
        setattr(operator, f'align_{i.lower()}_method', 'CENTER')
    return operator


def draw_distribution_x(layout, x):
    op = layout.operator(AlignObject.bl_idname,
                         text=set_text('Distribution'),
                         icon_value=get_icon('Align_Distribution_X'))
    op.align_mode = 'DISTRIBUTION'
    op.distribution_sorted_axis = str(AXIS.index(x[-1]))
    op.align_location_axis = {x[-1]}
    op.align_location = True


def draw_distribution_y(layout, y):
    op = layout.operator(AlignObject.bl_idname,
                         text=set_text('Distribution'),
                         icon_value=get_icon('Align_Distribution_Y'))
    op.align_mode = 'DISTRIBUTION'
    op.distribution_sorted_axis = str(AXIS.index(y[-1]))
    op.align_location_axis = {y[-1]}
    op.align_location = True


def draw_distribution(layout, direction):
    (x, _), (y, _) = direction
    draw_distribution_x(layout, x)
    draw_distribution_y(layout, y)


def draw_center_align(layout, direction):
    (x, _), (y, _) = direction

    get_center_align(layout, 'Align_Center_X').align_location_axis = {y[-1]}
    get_center_align(layout, 'Align_Center_Y').align_location_axis = {x[-1]}


def draw_ground(layout):
    op = layout.operator(AlignObject.bl_idname,
                         text=set_text('Ground'),
                         icon='IMPORT')
    op.align_mode = 'GROUND'
    op.ground_down_mode = 'ALL'
    op.ground_plane_mode = 'GROUND'
    op.align_location_axis = {'Z'}
    op.align_location = True


def draw_fall(layout):
    op = layout.operator(AlignObject.bl_idname,
                         text=set_text('Fall'),
                         icon='AXIS_TOP')
    op.align_mode = 'GROUND'
    op.ground_down_mode = 'ALL'
    op.ground_plane_mode = 'RAY_CASTING'
    op.align_location_axis = {'Z'}
    op.align_location = True


def draw_cursor_active_original(layout):
    draw_world(layout)
    draw_active(layout)
    draw_cursor(layout)


def draw_world(layout):
    op = layout.operator(AlignObject.bl_idname,
                         text=set_text('World Original'),
                         icon='OBJECT_ORIGIN')
    op.align_mode = 'ORIGINAL'
    op.align_location = True


def draw_active(layout):
    op = layout.operator(AlignObject.bl_idname,
                         text=set_text('Active'),
                         icon='RESTRICT_SELECT_OFF')

    op.align_mode = 'ACTIVE'
    op.align_location = True


def draw_cursor(layout):
    op = layout.operator(AlignObject.bl_idname,
                         text=set_text('Cursor'),
                         icon='PIVOT_CURSOR')
    op.align_mode = 'CURSOR'
    op.align_location = True


def draw_right(layout, context):
    direction = screen_relevant_direction_3d_axis(context)
    row = layout.row(align=True)
    column = row.column(align=True)

    column.scale_y = column.scale_x = 1.51495
    draw_center_align(column, direction)

    # three 分布 地面
    col = row.column(align=True)
    draw_distribution(col, direction)
    draw_ground(col)

    # original cursor active original
    col = row.column(align=True)
    draw_cursor_active_original(col)


class ObjectAlignPanel(Panel):
    bl_idname = 'ALIGN_PT_Panel'
    bl_label = 'POPOTI Align Helper'

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Tool'
    bl_options = set()

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def draw(self, context):
        col = self.layout.column(align=True)
        if getattr(context.space_data, 'region_3d', False):
            from ..ops import ObjectAlignByView
            from ..utils import get_pref
            row = col.row(align=True)
            ObjectAlignByView.draw_nine_square_box(row, show_text=False, ops=None)
            draw_right(row, context)
            draw_fall(col)
            if context.selected_objects.__len__() == 0:
                col.label(text="Please select at least one object")


class_tuples = (
    ObjectAlignPanel,
)

register_class, unregister_class = bpy.utils.register_classes_factory(
    class_tuples)


def register():
    register_class()


def unregister():
    unregister_class()
