import bpy
import numpy as np
from bpy.props import BoolProperty, EnumProperty
from bpy.types import Operator
from mathutils import Vector

from .utils import bound_to_tuple, vertices_co

axis_enum_property = EnumProperty(
    name='需要对齐的轴',
    description='选择需要进行对齐的轴,可多选',
    items=(('X', 'X', '对齐X轴'),
           ('Y', 'Y', '对齐Y轴'),
           ('Z', 'Z', '对齐Z轴'),),
    options={'ENUM_FLAG'},
    default={'X', 'Y', 'Z'})

align_func = (
    ('MIN', '最小点', '对齐到最小点'),
    ('CENTER', '居中', '居中对齐'),
    ('MAX', '最大点', '对齐到最大点'),)


class OperatorProperty:
    """
    distribution_func: EnumProperty(
        name='分布方式',
        description='分布物体方式',
        items=(
            ('spacing',     '间隔',     '统一每个物体间隔'),
            *align_func,),
    )"""

    mode_items = (
        ('ORIGINAL', '世界原点', '对齐到世界原点,和重置功能相同'),
        ('ACTIVE', '活动项', '对齐到活动物体'),
        ('CURSOR', '游标', '对齐到游标(缩放将重置为1)'),
        ('GROUND', '地面', '对齐到地面'),
        ('DISTRIBUTION', '分布', '分布对齐'),
        ('ALIGN', '对齐', '常规对齐,可以设置每个轴的对齐方式(最大,居中,最小)'),
    )
    mode: EnumProperty(items=mode_items)

    align_location: BoolProperty(name='位置', default=True)
    align_rotation: BoolProperty(name='旋转', default=True)
    align_scale: BoolProperty(name='缩放', default=False)
    align_location_axis: axis_enum_property
    align_rotation_euler_axis: axis_enum_property
    align_scale_axis: axis_enum_property

    distribution_sorted_axis: EnumProperty(
        name='分布排序轴',
        description='按选择轴对所选物体进行对齐并排序,以获取正确的移动位置',
        items=(('0', 'X', '按X轴排序1分布'),
               ('1', 'Y', '按Y轴排序1分布'),
               ('2', 'Z', '按Z轴排序1分布'),), )

    ground_mode: EnumProperty(
        items=(('ALL', '所有物体', ''),
               ('MINIMUM', '最低物体', ''),))

    # 每个一个轴的对齐方式
    x_align_func: EnumProperty(name='X', items=align_func, default='CENTER', )
    y_align_func: EnumProperty(name='Y', items=align_func, default='CENTER', )
    z_align_func: EnumProperty(name='Z', items=align_func, default='CENTER', )
    min_co: float  # 最小的坐标
    max_co: float  # 最大的坐标
    objs_center_co: float  # 中心坐标
    data: dict  # 数据
    objs_center_co: Vector
    align_mode_location: Vector


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
        row.label(text='排序轴')
        row.prop(self, 'distribution_sorted_axis', expand=True)
        layout.separator()
        self.draw_align_location(layout)

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
        if 'Y' in self.align_location_axis:
            obj.location.y += y
        if 'Z' in self.align_location_axis:
            obj.location.z += z

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
        """获取对齐的方法需要对齐到的坐标

        Args:
            func (_type_): _description_

        Returns:
            _type_: _description_
        """
        if func == 'MIN':
            return self.min_co
        elif func == 'MAX':
            return self.max_co
        elif func == 'CENTER':
            return self.objs_center_co

    def get_align_obj_mode_co(self, obj):
        """获取对齐的对齐方法每一个物体需要移动多少距离

        Args:
            obj (_type_): _description_
        """
        x, y, z = self.x_align_func, self.y_align_func, self.z_align_func

        def gc(axis):
            return self.data[obj.name][axis]

        obj_co = Vector((gc(x)[0], gc(y)[1], gc(z)[2]))

        co = obj_co - self.align_mode_location
        return co


class AlignObject(Operator, AlignOps):
    """
    对齐物体

    Ctrl    对齐旋转
    Shift   对齐缩放
    Alt     对齐位置
    可组合按
    """

    bl_idname = 'object.tool_kits_fast_align'
    bl_label = '物体对齐'
    bl_options = {'REGISTER', 'UNDO'}

    def get_object_data(self, context):
        # 无法使用物体作为key 因为操作符有undo操作
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

                self.data['DATA']['CO_TUPLE'] += [a, i]  # 添加最大最小点
                self.data['DATA']['DIMENSIONS'] += dimensions  # 添加物体的尺寸
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

        self.distribution_order = objs

        max_co = self.data[objs[-1]]['MAX']
        min_co = self.data[objs[0]]['MIN']

        dimensions_max_min_co = max_co - min_co  # 中心点第一个和最后一个物体的最大最小坐标
        dimensions = self.data['DATA']['DIMENSIONS']  # 物体的总尺寸长度
        self.interval_distance = dimensions_max_min_co - dimensions  # 所有物体应间隔的总长度

        # 如果所选只有一个物体则不减 除0 错误
        select_objs_len = bpy.context.selected_objects.__len__()
        objs_len = select_objs_len if select_objs_len == 1 else select_objs_len - 1

        # 每个物体之间应间隔的距离
        self.obj_interval = self.interval_distance / objs_len
        return objs

    def init_align_mode_data(self):
        """获取所选轴对齐方式的坐标
        就是需要对齐到的坐标
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

        for index, obj in enumerate(objs):
            '''
            如果是分布对齐objs就是物体的名称(作为键)
            否则objs就是物体
            '''
            run_func = getattr(self, f'align_to_{mode.lower()}', None)
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

    def align_to_distribution(self, obj_name):

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
                self.add_location_axis(obj, location)
                self.tmp_co = data['MAX'] + Vector(location)

    def align_to_ground(self, obj):
        if self.align_location:
            if self.ground_mode == 'ALL':
                self.subtract_location_axis(obj, self.data[obj.name]['MIN'])
            else:
                self.subtract_location_axis(obj, self.min_co)

    def align_to_align(self, context, obj):
        location = self.get_align_obj_mode_co(obj)
        if self.align_location:
            self.subtract_location_axis(obj, location)

    # ops----

    def __init__(self):
        self.data = {'DATA': {'CO_TUPLE': [],
                              'DIMENSIONS': Vector()},
                     'CENTER': {}
                     }
        self.get_object_data(bpy.context)

        self.min_co = np.min(self.data['DATA']['CO_TUPLE'], axis=0)
        self.max_co = np.max(self.data['DATA']['CO_TUPLE'], axis=0)

        self.objs_max_min_co = self.max_co - self.min_co  # 所有所选物体的最大最小坐标
        self.objs_center_co = (self.min_co + self.max_co) / 2

    @classmethod
    def poll(cls, context):
        return context.selected_objects.__len__()

    def draw(self, context):
        layout = self.layout
        col = layout.column()

        run_func = getattr(self, f'draw_{self.mode.lower()}', None)
        if run_func:
            run_func(col)

        col.row().prop(self, 'mode', expand=True)

    def invoke(self, context, event):
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
