import bpy
import numpy as np
from bpy.props import BoolProperty, EnumProperty, FloatProperty
from bpy.types import Operator
from mathutils import Vector

from .utils import bound_to_tuple, vertices_co

axis_enum_property = EnumProperty(
    name='Axis to be aligned',
    description='Select the axis to be aligned, multiple choices are allowed',
    items=(('X', 'X', 'Align X Axis'),
           ('Y', 'Y', 'Align Y Axis'),
           ('Z', 'Z', 'Align Z Axis'),),
    options={'ENUM_FLAG'},
    default={'X', 'Y', 'Z'})

align_items = (
    ('MIN', 'Min Point', 'Align to Min Point'),
    ('CENTER', 'Center', 'Center Align'),
    ('MAX', 'Max Point', 'Align to Max Point'),)


class OperatorProperty:
    mode_items = (
        ('ORIGINAL', 'Word Original',
         'Aligning to the world origin is the same as resetting'),
        ('ACTIVE', 'Active', 'Align to Active Object'),
        ('CURSOR', 'Cursor', 'Align to Cursor(Scale reset 1)'),
        ('GROUND', 'Ground', 'Align Ground'),
        ('DISTRIBUTION', 'Distribution', 'Distribution Align'),
        ('ALIGN', 'Align', 'General alignment, you can set the alignment of each axis(maximum, center, minimum)'),
    )
    mode: EnumProperty(items=mode_items)

    distribution_mode: EnumProperty(items={
        ("FIXED", "Fixed", "Fixed the nearest and farthest objects"),
        ("ADJUSTMENT", "Adjustment",
         "Adjust the distance between each object(Fixed active object)"),
    })
    distribution_adjustment_value: FloatProperty(
        name="Distribution interval value", default=1)

    align_location: BoolProperty(name='location', default=True)
    align_rotation: BoolProperty(name='rotate', default=True)
    align_scale: BoolProperty(name='scale', default=False)
    align_location_axis: axis_enum_property
    align_rotation_euler_axis: axis_enum_property
    align_scale_axis: axis_enum_property

    distribution_sorted_axis: EnumProperty(
        name='Distribution sort axis',
        description='Align and sort the selected objects according'
                    ' to the selection axis to obtain the correct movement position',
        items=(('0', 'X', 'Sort distribution by X axis'),
               ('1', 'Y', 'Sort distribution by Y axis'),
               ('2', 'Z', 'Sort distribution by X axis'),), )

    ground_mode: EnumProperty(
        items=(('ALL', 'All Object', ''),
               ('MINIMUM', 'Lowest Object', ''),))

    # ??????????????????????????????
    x_align_func: EnumProperty(name='X', items=align_items, default='CENTER', )
    y_align_func: EnumProperty(name='Y', items=align_items, default='CENTER', )
    z_align_func: EnumProperty(name='Z', items=align_items, default='CENTER', )
    min_co: float  # ???????????????
    max_co: float  # ???????????????
    objs_center_co: float  # ????????????
    data: dict  # ??????
    objs_center_co: Vector
    align_mode_location: Vector

    @property
    def is_fixed_mode(self):
        return self.distribution_mode == "FIXED"

    @property
    def is_adjustment_mode(self):
        return self.distribution_mode == "ADJUSTMENT"

    @property
    def is_distribution_mode(self):
        return self.mode == "DISTRIBUTION"

    @property
    def is_align_mode(self):
        return self.mode == "ALIGN"

    @property
    def is_distribution_fixed_mode(self):  # ??????????????????????????????????????????
        return self.is_fixed_mode and self.is_distribution_mode

    @property
    def is_distribution_adjustment_mode(self):  # ??????????????????????????????????????????
        return self.is_distribution_mode and self.is_adjustment_mode


class AlignUi(OperatorProperty):

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
        col.separator(factor=2)

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


class AlignOps(AlignUi):

    def subtract_location_axis(self, obj, location):
        x, y, z = location
        if 'X' in self.align_location_axis:
            obj.location.x -= x
        if 'Y' in self.align_location_axis:
            obj.location.y -= y
        if 'Z' in self.align_location_axis:
            obj.location.z -= z

    def add_location_axis(self, obj, location):
        x, y, z = location
        if 'X' in self.align_location_axis:
            obj.location.x += x
        else:
            x = 0

        if 'Y' in self.align_location_axis:
            obj.location.y += y
        else:
            y = 0

        if 'Z' in self.align_location_axis:
            obj.location.z += z
        else:
            z = 0

        return x, y, z

    def set_location_axis(self, obj, location):
        x, y, z = location
        if 'X' in self.align_location_axis:
            obj.location.x = x
        if 'Y' in self.align_location_axis:
            obj.location.y = y
        if 'Z' in self.align_location_axis:
            obj.location.z = z

    def set_rotation_euler_axis(self, obj, rotation_euler):
        x, y, z = rotation_euler
        if 'X' in self.align_rotation_euler_axis:
            obj.rotation_euler.x = x
        if 'Y' in self.align_rotation_euler_axis:
            obj.rotation_euler.y = y
        if 'Z' in self.align_rotation_euler_axis:
            obj.rotation_euler.z = z

    def set_scale_axis(self, obj, scale):
        x, y, z = scale
        if 'X' in self.align_scale_axis:
            obj.scale.x = x
        if 'Y' in self.align_scale_axis:
            obj.scale.y = y
        if 'Z' in self.align_scale_axis:
            obj.scale.z = z

    def get_align_func_co(self, func):
        if func == 'MIN':
            return self.min_co
        elif func == 'MAX':
            return self.max_co
        elif func == 'CENTER':
            return self.objs_center_co

    def get_align_obj_mode_co(self, obj):
        x, y, z = self.x_align_func, self.y_align_func, self.z_align_func

        def gc(axis):
            return self.data[obj.name][axis]

        obj_co = Vector((gc(x)[0], gc(y)[1], gc(z)[2]))

        co = obj_co - self.align_mode_location
        return co


class AlignObject(Operator, AlignOps):
    """
    ????????????

    Ctrl    ????????????
    Shift   ????????????
    Alt     ????????????
    ????????????
    """

    bl_idname = 'object.tool_kits_fast_align'
    bl_label = 'POPOTI Align Helper'
    bl_options = {'REGISTER', 'UNDO'}

    def get_object_data(self, context):
        # ????????????????????????key ??????????????????undo??????
        objs = context.selected_objects.copy()

        for obj in objs:
            obj_type = (obj.type in ('FONT', 'OBJECT', 'META', 'SURFACE',
                                     'CURVES', 'LATTICE', 'POINTCLOUD', 'GPENCIL', 'ARMATURE'))
            no_in = obj not in self.data
            mesh = (obj.type == 'MESH')
            key_name = obj.name
            mat = obj.matrix_world

            def gen_data():
                self.data[key_name] = {}

            if (obj_type or mesh) and no_in:
                gen_data()
                data = np.array(bound_to_tuple(obj, matrix=mat)
                                ) if obj_type else vertices_co(obj, matrix=mat)

                a = Vector(np.max(data, axis=0))
                i = Vector(np.min(data, axis=0))
                self.data[key_name]['DIMENSIONS'] = dimensions = a - i

                center = (i + dimensions / 2).freeze()

                self.data[key_name]['CENTER'] = center

                self.data['DATA']['CO_TUPLE'] += [a, i]  # ?????????????????????
                self.data['DATA']['DIMENSIONS'] += dimensions  # ?????????????????????
                self.data[key_name]['MIN'] = i
                self.data[key_name]['MAX'] = a

                if center not in self.data['CENTER']:
                    self.data['CENTER'][center] = []

                self.data['CENTER'][center].append(key_name)
            elif no_in:
                gen_data()
                self.data[key_name]['MIN'] = self.data[key_name]['MAX'] = a = i = obj.location
                self.data['DATA']['CO_TUPLE'] += [a, i]

                dimensions = Vector((0, 0, 0))
                self.data[key_name]['DIMENSIONS'] = dimensions
                self.data[key_name]['CENTER'] = i
                self.data['DATA']['DIMENSIONS'] += dimensions

        '''print('\nprint data')
        for i in self.data:
            a = self.data[i]
            print(i)
            for j in a:
                print(j, '\t', a[j])
            print('\n')'''

    def init_distribution_data(self):
        """
        ?????????????????????
        ???????????????????????????????????????????????????,????????????????????????,??????????????????????????????????????????xyz
        ??????????????????????????????,?????????????????????????????????????????????????????????????????????
        ???????????????????????????????????????(?????????????????????????????????[1:-1])
        ?????????????????????????????????2????????????????????????????????????
        """

        # ????????????????????????????????????
        center_key = int(self.distribution_sorted_axis)
        distribution_center_sorted = sorted(
            self.data['CENTER'].keys(), key=lambda x: x[center_key])

        # ???????????????????????????????????????????????????????????????
        objs = []
        for center in distribution_center_sorted:
            if len(self.data['CENTER'][center]) > 1:

                objs += sorted(self.data['CENTER'][center],
                               key=lambda x: self.data[x]['DIMENSIONS'])
            else:
                objs += self.data['CENTER'][center]

        self.distribution_order = objs

        max_co = self.data[objs[-1]]['MAX']
        min_co = self.data[objs[0]]['MIN']

        dimensions_max_min_co = max_co - min_co  # ????????????????????????????????????????????????????????????
        dimensions = self.data['DATA']['DIMENSIONS']  # ????????????????????????
        self.interval_distance = dimensions_max_min_co - dimensions  # ?????????????????????????????????

        # ??????????????????????????????????????? ???0 ??????
        select_objs_len = bpy.context.selected_objects.__len__()
        objs_len = select_objs_len if select_objs_len == 1 else select_objs_len - 1

        # ????????????????????????????????????
        self.obj_interval = self.interval_distance / objs_len
        return objs

    def init_align_mode_data(self):
        """????????????????????????????????????
        ??????????????????????????????
        """
        gc = self.get_align_func_co
        x, y, z = self.x_align_func, self.y_align_func, self.z_align_func
        self.align_mode_location = Vector((gc(x)[0], gc(y)[1], gc(z)[2]))

    def object_location_set_funcs(self, context):
        mode = self.mode
        distribution = (mode == 'DISTRIBUTION')
        align = (mode == 'ALIGN')

        objs = context.selected_objects.copy()
        if distribution:
            objs = self.init_distribution_data()
        elif align:
            self.init_align_mode_data()

        if distribution and self.distribution_mode == "ADJUSTMENT":
            self.align_to_distribution_adjustment(context)
            return

        for index, obj in enumerate(objs):
            '''
            ?????????????????????objs?????????????????????(?????????)
            ??????objs????????????
            '''
            run_func = getattr(self, f'align_to_{mode.lower()}', None)
            self.index = index  # ???????????????,??????????????????????????????????????????
            if run_func:
                run_func(context, obj)

    def align_to_original(self, context, obj):
        if self.align_location:
            self.set_location_axis(obj, (0, 0, 0))

        if self.align_rotation:
            self.set_rotation_euler_axis(obj, (0, 0, 0))

        if self.align_scale:
            self.set_scale_axis(obj, (1, 1, 1))

    def align_to_active(self, context, obj):
        act_obj = context.active_object
        if not act_obj:
            act_obj = context.selected_objects[-1]

        if self.align_location:
            self.set_location_axis(obj, act_obj.location)

        if self.align_rotation:
            self.set_rotation_euler_axis(obj, act_obj.rotation_euler)

        if self.align_scale:
            self.set_scale_axis(obj, act_obj.scale)

    def align_to_cursor(self, context, obj):
        cursor = context.scene.cursor

        if self.align_location:
            self.set_location_axis(obj, cursor.location)

        if self.align_rotation:
            self.set_rotation_euler_axis(obj, cursor.rotation_euler)

        if self.align_scale:
            self.set_scale_axis(obj, (1, 1, 1))

    def align_to_distribution(self, context, obj_name):

        if self.align_location:

            order = self.distribution_order
            dl = order.__len__()
            data = self.data[obj_name]

            if order.index(obj_name) in (0, dl - 1):
                self.tmp_co = data['MAX']
                # ????????????????????????????????????????????????
            else:
                obj = bpy.data.objects[obj_name]

                '''
                # if self.distribution_func == 'spacing':
                    # ??????????????????'''

                obj_lo = data['MIN']
                location = self.obj_interval - (obj_lo - self.tmp_co)
                self.tmp_co = data['MAX'] + Vector(self.add_location_axis(obj, location))

    def align_to_ground(self, context, obj):
        if self.align_location:
            if self.ground_mode == 'ALL':
                self.subtract_location_axis(obj, self.data[obj.name]['MIN'])
            else:
                self.subtract_location_axis(obj, self.min_co)

    def align_to_align(self, context, obj):
        location = self.get_align_obj_mode_co(obj)
        if self.align_location:
            self.subtract_location_axis(obj, location)

    def align_to_distribution_adjustment(self, context):
        active_obj = context.active_object

        objs = self.distribution_order
        active_index = objs.index(active_obj.name)
        active_data = self.data[active_obj.name]
        value = self.distribution_adjustment_value

        self.tmp_co = active_data['MIN']
        for obj in objs[:active_index][::-1]:
            data = self.data[obj]

            obj = bpy.data.objects[obj]

            obj_lo = data['MAX']
            location = Vector((-value, -value, -value)) - \
                       (obj_lo - self.tmp_co)
            self.add_location_axis(obj, location)
            self.tmp_co = data['MIN'] + Vector(location)

        self.tmp_co = active_data['MAX']
        for obj_name in objs[active_index + 1:]:
            data = self.data[obj_name]

            obj = bpy.data.objects[obj_name]

            obj_lo = data['MIN']
            location = Vector((value, value, value)) - (obj_lo - self.tmp_co)
            self.add_location_axis(obj, location)
            self.tmp_co = data['MAX'] + Vector(location)

        print(self)

    @classmethod
    def poll(cls, context):
        return context.selected_objects.__len__()

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        run_func = getattr(self, f'draw_{self.mode.lower()}', None)
        if run_func:
            run_func(col)

        col.column().prop(self, 'mode', expand=True)

    def invoke(self, context, event):
        self.data = {'DATA': {'CO_TUPLE': [],
                              'DIMENSIONS': Vector()},
                     'CENTER': {}
                     }
        self.get_object_data(bpy.context)

        self.min_co = np.min(self.data['DATA']['CO_TUPLE'], axis=0)
        self.max_co = np.max(self.data['DATA']['CO_TUPLE'], axis=0)

        self.objs_max_min_co = self.max_co - self.min_co  # ???????????????????????????????????????
        self.objs_center_co = (self.min_co + self.max_co) / 2

        if event.ctrl or event.shift or event.alt:
            self.align_rotation = event.ctrl
            self.align_scale = event.shift
            self.align_location = event.alt
        return self.execute(context)

    def execute(self, context):
        """
        ????????????????????????:
            ???????????????
            ?????????
            ?????????
            ????????????

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
