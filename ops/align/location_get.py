import bpy
import numpy as np
from mathutils import Vector

from .operator_property import VALID_OBJ_TYPE
from ...utils import bound_to_tuple, vertices_co


class LocationGet:

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
        dep = bpy.context.evaluated_depsgraph_get()

        for obj in context.selected_objects.copy():
            obj = obj.evaluated_get(dep)
            is_valid_obj_type = (obj.type in VALID_OBJ_TYPE)
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
