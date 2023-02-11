from time import time as _time

import bpy
import numpy as _np
from mathutils import Vector


def np_matrix_dot(np_co, matrix):
    np_co = _np.insert(np_co, 3, 1, axis=1).T  # 对numpy数据插入一位数并进行转置
    np_co[:] = _np.dot(matrix, np_co)  # 点乘得到变换后的点位置
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

    st = _time()
    try:
        data = _get_mesh(data)
        vertices = data.vertices
        v_l = vertices.__len__()
        np_co = _np.zeros(v_l * 3, dtype=_np.float32)

        vertices.foreach_get('co', np_co)
    except Exception as e:
        print(f'获取错误:{data} 不是有效的网格或物体数据 {e.args}')

    else:
        np_co = np_co.reshape((v_l, 3))

        if matrix:
            np_co = np_matrix_dot(np_co, matrix)
        if debug:
            print(f'获取{data}顶点数据,共用时{_time() - st}s')
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


def screen_relevant_direction_3d_axis(context, *, return_type=None):
    """获取基于视图的3D空间3D轴的相对视图XY轴对应轴
    Args:
        context (_type_): _description_
        return_type (_type_, optional): _description_. Defaults to None.

    Returns:
        tuple(x轴,y轴): 轴分别有一个正向和负向
    """
    from math import pi
    from mathutils import Vector
    from bpy_extras.view3d_utils import location_3d_to_region_2d
    area = context.area
    region_3d = context.space_data.region_3d
    origin = location_3d_to_region_2d(area, region_3d, Vector())  # 原点

    ox = Vector((1, 0))
    oy = Vector((0, 1))
    data = {'x': {'angle': 360},
            'y': {'angle': 360},
            }

    for index, axis in enumerate(('X', 'Y', 'Z')):
        # 循环测试这三个轴
        av = Vector()
        av[index] = 1
        loc2d = location_3d_to_region_2d(area, region_3d, av)  # 获取轴在屏幕上的点
        if not loc2d or not origin:
            return ("X", "-X"), ("Y", "-Y")

        v_2d = loc2d - origin

        if v_2d == Vector((0, 0)):
            # print(axis, '轴平行于视图', v_2d, '== Vector((0, 0))', loc2d, '\n')
            continue

        def get_and_set_axis(o: Vector, screen_axis, axis_):
            """判断此轴与屏幕空间的轴的角度是不是最小并设置"""
            angle = (180 * o.angle(v_2d)) / pi
            angle_ = 180 - angle

            i_ = '-' + axis_
            if angle <= data[screen_axis]['angle']:
                data[screen_axis]['angle'] = angle
                data[screen_axis]['axis'] = (axis_, i_)
            if angle_ <= data[screen_axis]['angle']:
                data[screen_axis]['angle'] = angle_
                data[screen_axis]['axis'] = (i_, axis_)

        get_and_set_axis(ox, 'x', axis)
        get_and_set_axis(oy, 'y', axis)
    if return_type:
        return data

    return data['x']['axis'], data['y']['axis']
