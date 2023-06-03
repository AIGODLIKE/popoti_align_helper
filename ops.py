import bpy
import numpy as np
from bpy.props import (
    BoolProperty,
    EnumProperty,
    FloatProperty,
    StringProperty
)
from bpy.types import Operator
from mathutils import Vector

from .utils import bound_to_tuple, vertices_co


class Data:
    ENUM_DISTRIBUTION_SORTED_AXIS = [
        ('0', 'X', 'Sort distribution by X axis'),
        ('1', 'Y', 'Sort distribution by Y axis'),
        ('2', 'Z', 'Sort distribution by X axis'), ]
    ENUM_GROUND_MODE = [('ALL', 'All Object', ''),
                        ('MINIMUM', 'Lowest Object', ''), ]
    ENUM_ALIGN_MODE = [
        ('ORIGINAL', 'World Original',
         'Aligning to the world origin is the same as resetting'),
        ('ACTIVE', 'Active', 'Align to Active Object'),
        ('CURSOR', 'Cursor', 'Align to Cursor(Scale reset 1)'),
        ('GROUND', 'Ground', 'Align Ground'),
        ('DISTRIBUTION', 'Distribution', 'Distribution Align'),
        ('ALIGN',
         'Align',
         'General alignment, you can set the alignment of each axis'
         '(maximum, center, minimum)'),
    ]
    ENUM_DISTRIBUTION_MODE = [
        ("FIXED", "Fixed", "Fixed the nearest and farthest objects"),
        ("ADJUSTMENT", "Adjustment",
         "Adjust the distance between each object(Fixed active object)"), ]
    ENUM_ALIGN_FUNC = [
        ('MIN', 'Min Point', 'Align to Min Point'),
        ('CENTER', 'Center', 'Center Align'),
        ('MAX', 'Max Point', 'Align to Max Point'),
    ]

    ENUM_AXIS = [('X', 'X', 'Align X Axis'),
                 ('Y', 'Y', 'Align Y Axis'),
                 ('Z', 'Z', 'Align Z Axis'),
                 ]
    VALID_OBJ_TYPE = ('FONT', 'OBJECT', 'META', 'SURFACE',
                      'CURVES', 'LATTICE', 'POINTCLOUD', 'GPENCIL', 'ARMATURE')


axis_enum_property = EnumProperty(
    name='Axis to be aligned',
    description='Select the axis to be aligned, multiple choices are allowed',
    items=Data.ENUM_AXIS,
    options={'ENUM_FLAG'},
    default={'X', 'Y', 'Z'})


class TempProp:
    min_co: Vector  # 最小的坐标
    max_co: Vector  # 最大的坐标
    objs_max_min_co: 'list[Vector]'
    objs_center_co: Vector  # 中心坐标
    data: dict  # 数据
    align_mode_location: Vector
    index: int


class OperatorProperty(TempProp):
    align_mode: EnumProperty(items=Data.ENUM_ALIGN_MODE)

    distribution_mode: EnumProperty(
        items=Data.ENUM_DISTRIBUTION_MODE,
        default='FIXED'
    )
    distribution_adjustment_value: FloatProperty(
        name="Distribution interval value", default=1)

    align_location: BoolProperty(name='Location', default=True)
    align_rotation: BoolProperty(name='Rotate', default=True)
    align_scale: BoolProperty(name='Scale', default=False)
    align_location_axis: axis_enum_property
    align_rotation_euler_axis: axis_enum_property
    align_scale_axis: axis_enum_property

    distribution_sorted_axis: EnumProperty(
        name='Distribution sort axis',
        description='Align and sort the selected objects according'
                    ' to the selection axis to obtain the correct movement '
                    'position',
        items=Data.ENUM_DISTRIBUTION_SORTED_AXIS)

    ground_mode: EnumProperty(
        items=Data.ENUM_GROUND_MODE)
    align_to_ground_object: BoolProperty(name='Align To Ground Object')
    ground_object_name: StringProperty(
        name='To Object',
        description='Align To Ground Object')

    # 每个一个轴的对齐方式
    x_align_func: EnumProperty(name='X', items=Data.ENUM_ALIGN_FUNC,
                               default='CENTER', )
    y_align_func: EnumProperty(name='Y', items=Data.ENUM_ALIGN_FUNC,
                               default='CENTER', )
    z_align_func: EnumProperty(name='Z', items=Data.ENUM_ALIGN_FUNC,
                               default='CENTER', )

    @property
    def is_fixed_mode(self):
        return self.distribution_mode == "FIXED"

    @property
    def is_adjustment_mode(self):
        return self.distribution_mode == "ADJUSTMENT"

    @property
    def is_distribution_mode(self):
        return self.align_mode == "DISTRIBUTION"

    @property
    def is_align_mode(self):
        return self.align_mode == "ALIGN"

    @property
    def is_ground_mode(self):
        return self.align_mode == "GROUND"

    @property
    def is_distribution_fixed_mode(self):  # 是分布模式并且是固定间距模式
        return self.is_fixed_mode and self.is_distribution_mode

    @property
    def is_distribution_adjustment_mode(self):  # 是分布模式并且是固定间距模式
        return self.is_distribution_mode and self.is_adjustment_mode

    @property
    def is_align_to_ground_object(self) -> bool:
        ground = self.ground_object and self.is_ground_mode
        return self.align_to_ground_object and ground

    @property
    def ground_object(self) -> bpy.types.Object:
        name = self.ground_object_name
        if name:
            return bpy.data.objects.get(name, None)


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


class GetLocation(AlignUi,
                  Operator, ):

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

    def invoke_init_object_location(self, context):
        # 无法使用物体作为key 因为操作符有undo操作,只能将name作为key

        for obj in context.selected_objects.copy():
            is_valid_obj_type = (obj.type in Data.VALID_OBJ_TYPE)
            obj_not_in_data = obj not in self.data
            is_mesh = (obj.type == 'MESH')
            obj_name = obj.name
            mat = obj.matrix_world

            def gen_data():
                self.data[obj_name] = {}

            if (is_valid_obj_type or is_mesh) and obj_not_in_data:
                gen_data()
                if is_valid_obj_type:
                    data = np.array(bound_to_tuple(obj, matrix=mat))
                else:
                    data = vertices_co(obj, matrix=mat)

                loc_max = Vector(np.max(data, axis=0))
                loc_min = Vector(np.min(data, axis=0))
                dimensions = loc_max - loc_min
                self.data[obj_name]['DIMENSIONS'] = dimensions

                center = (loc_min + dimensions / 2).freeze()

                self.data[obj_name]['CENTER'] = center

                self.data['DATA']['CO_TUPLE'] += [loc_max, loc_min]
                # 添加最大最小点
                self.data['DATA']['DIMENSIONS'] += dimensions
                # 添加物体的尺寸
                self.data[obj_name]['MIN'] = loc_min
                self.data[obj_name]['MAX'] = loc_max

                if center not in self.data['CENTER']:
                    self.data['CENTER'][center] = []

                self.data['CENTER'][center].append(obj_name)
            elif obj_not_in_data:
                self.init_not_int_data_object(gen_data, obj, obj_name)

    def init_not_int_data_object(self, gen_data, obj, obj_name):
        gen_data()
        loc = obj.location.copy().freeze()
        center = loc_max = loc_min = loc
        self.data[obj_name]['MIN'] = self.data[obj_name]['MAX'] = loc

        self.data['DATA']['CO_TUPLE'] += [loc_max, loc_min]

        dimensions = Vector((0, 0, 0))
        self.data[obj_name]['DIMENSIONS'] = dimensions
        self.data[obj_name]['CENTER'] = center
        self.data['DATA']['DIMENSIONS'] += dimensions

        if center not in self.data['CENTER']:
            self.data['CENTER'][center] = []

        self.data['CENTER'][center].append(obj_name)

    def init_align_mode_data(self):
        """获取所选轴对齐方式的坐标
        就是需要对齐到的坐标
        """
        gc = self.get_align_func_co
        x, y, z = self.x_align_func, self.y_align_func, self.z_align_func
        self.align_mode_location = Vector((gc(x)[0], gc(y)[1], gc(z)[2]))


class SetLocation(GetLocation):

    def object_location_set_funcs(self, context):
        align_mode = self.align_mode
        is_distribution_mode = (align_mode == 'DISTRIBUTION')
        is_align_mode = (align_mode == 'ALIGN')

        objs = context.selected_objects.copy()
        if is_distribution_mode:
            objs = self.init_distribution_data()
        elif is_align_mode:
            self.init_align_mode_data()

        if is_distribution_mode and self.distribution_mode == "ADJUSTMENT":
            self.align_to_distribution_adjustment(context)
            return

        for index, obj in enumerate(objs):
            '''
            如果是分布对齐objs就是物体的名称(作为键)
            否则objs就是物体
            '''
            run_func = getattr(self, f'align_to_{align_mode.lower()}', None)
            self.index = index  # 分布对齐用,查找当前物体需要对齐到的目标
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
                # 是第一个或最后一个物体，不用操作
            else:
                obj = bpy.data.objects[obj_name]

                '''
                # if self.distribution_func == 'spacing':
                    # 分布间隔对齐'''

                obj_lo = data['MIN']
                location = self.obj_interval - (obj_lo - self.tmp_co)
                co = Vector(self.add_location_axis(obj, location))
                self.tmp_co = data['MAX'] + co

    def align_to_ground(self, context, obj):
        if self.align_location:

            if self.ground_mode == 'ALL':
                location = self.data[obj.name]['MIN']
            else:
                location = self.min_co

            if self.is_align_to_ground_object:
                self.align_to_ground_ray_cast(obj, location)
                return
            self.subtract_location_axis(obj, location)

    def align_to_align(self, context, obj):
        location = self.get_align_obj_mode_co(obj)
        if self.align_location:
            self.subtract_location_axis(obj, location)

    def align_to_distribution_adjustment(self, context):
        active_obj = context.active_object
        objs = self.distribution_order

        if active_obj and (active_obj.name not in objs):
            self.report({'INFO'}, 'Not Selected Active Object')
            active_index = -1
            active_data = self.data[objs[0]]
        else:
            active_index = objs.index(active_obj.name)
            active_data = self.data[active_obj.name]

        value = self.distribution_adjustment_value

        self.tmp_co = active_data['MIN']
        for obj in objs[:active_index][::-1]:
            data = self.data[obj]

            obj = bpy.data.objects[obj]

            obj_lo = data['MAX']
            v = (obj_lo - self.tmp_co)
            location = Vector((-value, -value, -value)) - v

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

    def init_distribution_data(self):
        """
        如果是分布对齐
        需要先算一下每一个物体的中心点排序,按中心点大小来排,可以让使用者选择进行排序的轴xyz
        排序好之后要再排一次,以解决两个中心点在同一个位置的情况避免排序错误
        然后再对每一个物体进行移动(两端的物体不会进行移动[1:-1])
        如果所选物体的数量小于2，也没关系切出来是个空的
        """

        # 使用选定的轴进行一次排序
        center_key = int(self.distribution_sorted_axis)
        distribution_center_sorted = sorted(
            self.data['CENTER'].keys(), key=lambda x: x[center_key])

        # 再排一次序，对比出中点一至的多个物体的次序
        objs = []
        for center in distribution_center_sorted:
            if len(self.data['CENTER'][center]) > 1:

                objs += sorted(self.data['CENTER'][center],
                               key=lambda x: self.data[x]['DIMENSIONS'])
            else:
                objs += self.data['CENTER'][center]
        print('objs', objs, distribution_center_sorted)
        self.distribution_order = objs

        max_co = self.data[objs[-1]]['MAX']
        min_co = self.data[objs[0]]['MIN']

        dimensions_max_min_co = max_co - min_co  # 中心点第一个和最后一个物体的最大最小坐标
        dimensions = self.data['DATA']['DIMENSIONS']  # 物体的总尺寸长度
        self.interval_distance = dimensions_max_min_co - dimensions  #
        # 所有物体应间隔的总长度

        # 如果所选只有一个物体则不减 除0 错误
        select_objs_len = bpy.context.selected_objects.__len__()
        if select_objs_len == 1:
            objs_len = select_objs_len
        else:
            objs_len = select_objs_len - 1

        # 每个物体之间应间隔的距离
        self.obj_interval = self.interval_distance / objs_len
        return objs

    def align_to_ground_ray_cast(self, obj, location):
        dep = bpy.context.evaluated_depsgraph_get()
        ray_obj = self.ground_object.evaluated_get(dep)
        direction = Vector((0, 0, -1))
        try:
            (result, loc, normal, index) = ray_obj.ray_cast(location, direction)
            print(obj.name, loc, location)
            if result:
                self.subtract_location_axis(obj, location - loc)
        except RuntimeError:
            ...


class AlignObject(SetLocation):
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
