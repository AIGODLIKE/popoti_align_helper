import bpy
from mathutils import Vector, Matrix


def get_sca_matrix(scale):
    scale_mx = Matrix()
    for i in range(3):
        scale_mx[i][i] = scale[i]
    return scale_mx


class LocationSet:
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

    # def align_to_active(self, context, obj):
    #     depsgraph = context.evaluated_depsgraph_get()
    #     act_obj = context.active_object
    #     if not act_obj:
    #         act_obj = context.selected_objects[-1]
    #     if act_obj == obj:
    #         # 不要更改活动物体
    #         return
    #     if self.align_location:
    #         location = act_obj.evaluated_get(depsgraph).matrix_world.to_translation()
    #         self.set_location_axis(obj, location)
    #
    #     if self.align_rotation:
    #         self.set_rotation_euler_axis(obj, act_obj.rotation_euler)
    #
    #     if self.align_scale:
    #         self.set_scale_axis(obj, act_obj.scale)

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
