# version = 0.1.1
from math import pi


def __orthogonal_views__(context):
    """检测正交视图"""
    from mathutils import Quaternion
    region_3d = context.space_data.region_3d
    v = 0.7071067690849304
    orthogonal_view_items = {  # 正交视图处理
        Quaternion((v, v, -0.0, -0.0)).freeze(): (('X', '-X'), ('Z', '-Z')),  # 前
        Quaternion((0.0, -0.0, v, v)).freeze(): (('-X', 'X'), ('Z', '-Z')),  # 后
        Quaternion((0.5, 0.5, -0.5, -0.5)).freeze(): (("-Y", "Y"), ("Z", "-Z")),  # 左
        Quaternion((0.5, 0.5, 0.5, 0.5)).freeze(): (('Y', '-Y'), ('Z', '-Z')),  # 右
        Quaternion((1.0, -0.0, -0.0, -0.0)).freeze(): (('X', '-X'), ('Y', '-Y')),  # 上
        Quaternion((0.0, 1.0, -0.0, -0.0)).freeze(): (('X', '-X'), ('-Y', 'Y')),  # 下
    }
    for key, value in orthogonal_view_items.items():
        if region_3d.view_rotation == key:
            return value
    return None


def screen_relevant_direction_3d_axis(context):
    """获取基于视图的3D空间3D轴的相对视图XY轴对应轴

    Args:
        context (_type_): _description_
    Returns:
        tuple(x轴,y轴): 轴分别有一个正向和负向
    bpy.context.screen.areas[0].spaces[0].region_3d.view_location
    return ("X", "-X"), ("Y", "-Y")
    """
    from mathutils import Vector
    from bpy_extras.view3d_utils import location_3d_to_region_2d

    if orthogonal := __orthogonal_views__(context):
        return orthogonal

    area = context.area
    region_3d = context.space_data.region_3d

    view_location = region_3d.view_location
    view_distance = region_3d.view_distance
    offset = view_distance * .2

    origin_2d = location_3d_to_region_2d(area, region_3d, view_location)  # 原点

    data = {"x": {"angle": 360, "distance": 99999},
            "y": {"angle": 360, "distance": 99999},
            }

    for index, axis in enumerate(("X", "Y", "Z")):
        negative_axis = "-" + axis
        for pn in (True, False):  # 正负轴 # positive and negative
            axis_loc = view_location.copy()
            if pn:
                axis_loc[index] += offset
            else:
                axis_loc[index] -= offset

            axis_2d = location_3d_to_region_2d(area, region_3d, axis_loc)  # 获取轴在屏幕上的点
            axis_v = axis_2d - origin_2d

            if axis_v == Vector((0, 0)):  # 在正交视图不会出现这种情况，但使用shift+ 4 6会触发
                print(axis, "轴平行于视图", axis_v, "== Vector((0, 0))", axis_2d, "\n")
                continue

            for screen_axis, screen_v in (("x", origin_2d + Vector((9999, 0))),
                                          ("y", origin_2d + Vector((0, 9999)))):
                angle = (180 * screen_v.angle(axis_v)) / pi

                distance = (screen_v - axis_v).length

                prev_angle = data[screen_axis]["angle"]
                prev_distance = data[screen_axis]["distance"]

                if prev_angle > angle and prev_distance > distance:
                    data[screen_axis]["distance"] = distance
                    data[screen_axis]["angle"] = angle
                    data[screen_axis]["axis"] = (axis, negative_axis) if pn else (negative_axis, axis)
    return data["x"]["axis"], data["y"]["axis"]
