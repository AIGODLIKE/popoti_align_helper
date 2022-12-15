import bpy
from bpy.types import Panel

from .icons import get_icon
from .utils import screen_relevant_direction_3d_axis

align_operator = 'object.tool_kits_fast_align'


# one
def set_axis(layout, axis, icon, center=False):
    op = layout.operator(
        align_operator,
        icon_value=get_icon(icon),
        text='',
    )
    op.mode = 'ALIGN'

    if axis == 'CENTER':
        center = True
        axis = ('X', 'Y', 'Z')
    for i in axis:
        value = 'MIN' if len(i) >= 2 else 'MAX'
        if center:
            value = 'CENTER'
        setattr(op, i[-1].lower() + '_align_func', value)

    op.align_location_axis = {i[-1] for i in axis}


class ObjectAlignPanel(Panel):
    bl_idname = 'ALIGN_PT_Panel'
    bl_label = 'POPOTI对齐助手'

    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        layout = self.layout
        layout.operator(align_operator)
        (x, x_), (y, y_) = screen_relevant_direction_3d_axis(context)

        sp = layout.split(align=True)
        axis = ('X', 'Y', 'Z')

        col = sp.column(align=True)
        col.alert = True
        row = col.row(align=True)
        set_axis(row, {x_, y}, 'Align_Left_Up')
        set_axis(row, {y}, 'Align_Up')
        set_axis(row, {x, y}, 'Align_Right_Up')
        row = col.row(align=True)
        set_axis(row, {x_}, 'Align_Left')
        set_axis(row, 'CENTER', 'Align_Center')
        set_axis(row, {x}, 'Align_Right')
        row = col.row(align=True)
        set_axis(row, {x_, y_}, 'Align_Left_Down')
        set_axis(row, {y_}, 'Align_Down')
        set_axis(row, {x, y_}, 'Align_Right_Down')

        # two
        col = sp.column(align=True)

        col.scale_y = 1.5

        def get_center_align(icon):
            op = col.operator(align_operator,
                              icon_value=get_icon(icon),
                              text='',
                              )
            op.mode = 'ALIGN'
            op.align_location = True
            for i in axis:
                setattr(op, i.lower() + '_align_func', 'CENTER')
            return op

        get_center_align('Align_Center_X').align_location_axis = {y[-1]}
        get_center_align('Align_Center_Y').align_location_axis = {x[-1]}

        # three 分布 地面
        col = sp.column(align=True)
        op = col.operator(align_operator,
                          text='Distribution',
                          icon_value=get_icon('Align_Distribution_X'))
        op.mode = 'DISTRIBUTION'
        op.distribution_sorted_axis = str(axis.index(x[-1]))
        op.align_location_axis = {x[-1]}
        op.align_location = True

        op = col.operator(align_operator,
                          text='Distribution',
                          icon_value=get_icon('Align_Distribution_Y'))
        op.mode = 'DISTRIBUTION'
        op.distribution_sorted_axis = str(axis.index(y[-1]))
        op.align_location_axis = {y[-1]}
        op.align_location = True

        op = col.operator(align_operator,
                          text='Ground',
                          icon='IMPORT')
        op.mode = 'GROUND'
        op.ground_mode = 'MINIMUM'
        op.align_location_axis = {'Z'}
        op.align_location = True

        # original cursor active original
        col = sp.column(align=True)
        op = col.operator(align_operator,
                          text='original',
                          icon='OBJECT_ORIGIN')
        op.mode = 'ORIGINAL'
        op = col.operator(align_operator,
                          text='Active',
                          icon='RESTRICT_SELECT_OFF')

        op.mode = 'ACTIVE'
        op = col.operator(align_operator,
                          text='Cursor',
                          icon='PIVOT_CURSOR')
        op.mode = 'CURSOR'


class_tuples = (
    ObjectAlignPanel,
)

register_class, unregister_class = bpy.utils.register_classes_factory(
    class_tuples)


def register():
    register_class()


def unregister():
    unregister_class()
