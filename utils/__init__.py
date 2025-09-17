from time import time

import bpy
import numpy as np
from mathutils import Vector


def np_matrix_dot(np_co, matrix):
    np_co = np.insert(np_co, 3, 1, axis=1).T  # 对numpy数据插入一位数并进行转置
    np_co[:] = np.dot(matrix, np_co)  # 点乘得到变换后的点位置
    np_co /= np_co[3, :]  # 除一下第四位
    np_co = np_co.T  # 再转置一下
    np_co = np_co[:, :3]  # 取前三位坐标数据
    return np_co


def _get_mesh(data: object):
    """获取物体网格数据,可直接输入物体或是网格
    如果不是网格物体则会反回错误

    """
    if type(data) == bpy.types.Mesh:
        data.update()
        obj = data
    elif (type(data) == bpy.types.Object) and (data.type == 'MESH'):
        data.update_from_editmode()
        obj = data.data
    else:
        obj = Exception(f'物体{data}不是一个网格物体')
    return obj


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

def get_pref():
    """获取偏好"""
    from .. import __package__ as base_package
    return bpy.context.preferences.addons[base_package].preferences


def translate_lines_text(*args, split="\n"):
    from bpy.app.translations import pgettext_iface
    return split.join([pgettext_iface(line) for line in args])
