from time import time

import bpy
import numpy as np
from mathutils import Vector

from .operator_property import VALID_OBJ_TYPE
from ...utils import _get_mesh


def bound_to_tuple(obj, matrix=None) -> tuple:
    """
    :param matrix:矩阵
    :param obj:输入一个物体,反回物体的边界框列表
    :type obj:bpy.types.Object
    :return tuple:
    """
    if matrix:
        return tuple(matrix @ Vector(i[:]) for i in obj.bound_box)
    else:
        return tuple(i[:] for i in obj.bound_box)


def np_matrix_dot(np_co, matrix):
    np_co = np.insert(np_co, 3, 1, axis=1).T  # 对numpy数据插入一位数并进行转置
    np_co[:] = np.dot(matrix, np_co)  # 点乘得到变换后的点位置
    np_co /= np_co[3, :]  # 除一下第四位
    np_co = np_co.T  # 再转置一下
    np_co = np_co[:, :3]  # 取前三位坐标数据
    return np_co


def vertices_co(data, *, matrix=None, debug=False):
    """从object.data获取物体的顶点坐标并反回numpy数据
    Args:
        data (_bpy.types.Object, _bpy.data.meshes):输入一个网格或物体
        matrix (bool):输入一个矩阵用于点乘每一个点,如果不输入则不进行点乘操作
        debug (bool):打印获取数据的时间,计算将会消耗一些性能
    Returns:
        numpy.array: 反回所有顶点坐标的np阵列
    """

    st = time()
    try:
        data = _get_mesh(data)
        vertices = data.vertices
        v_l = vertices.__len__()
        np_co = np.zeros(v_l * 3, dtype=np.float32)

        vertices.foreach_get('co', np_co)
    except Exception as e:
        print(f'获取错误:{data} 不是有效的网格或物体数据 {e.args}')

    else:
        np_co = np_co.reshape((v_l, 3))

        if matrix:
            np_co = np_matrix_dot(np_co, matrix)
        if debug:
            print(f'获取{data}顶点数据,共用时{time() - st}s')
        return np_co


class ToDistribution:

    def align_to_distribution(self, context):
        self.init_distribution(context)


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

    def init_distribution(self, context):
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
