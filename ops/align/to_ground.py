import bpy
import numpy as np
from mathutils import Vector, Euler

from .operator_property import VALID_OBJ_TYPE
from .to_matrix import get_loc_matrix, get_rot_matrix, get_sca_matrix
from ...utils import bound_to_tuple, vertices_co


class ToGround:
    def align_to_ground(self, context):
        dep = context.evaluated_depsgraph_get()
        if self.ground_plane_mode == "RAY_CASTING":
            self.align_to_ground_ray_casting(context, dep)
        else:
            to_z = 0  # 只使用z轴数据
            if self.ground_plane_mode == "DESIGNATED_OBJECT":
                """使用一个物体作为地面
                这个时候需要对准的是这个物体的最高Z轴
                """
                if not self.ground_object_name:
                    return
                if self.ground_object_name not in context.scene.objects:
                    return

                ground_obj = context.scene.objects[self.ground_object_name]
                ground_obj_bound_box = get_count_bound_box(ground_obj)
                to_z = max([c.z for c in ground_obj_bound_box])
            # 计算每一个物体到0的偏移并移动
            min_z = None
            for obj in context.selected_objects:
                bound_box = get_count_bound_box(obj)
                z = _get_min_z_(bound_box)  # 物体的最低Z轴

                if self.ground_down_mode == "ALL":
                    context.view_layer.update()
                    l = get_loc_matrix(Vector((0, 0, to_z - z))) @ get_loc_matrix(obj.location)
                    r = get_rot_matrix(obj.rotation_euler)
                    s = get_sca_matrix(obj.scale)

                    obj.matrix_world = l @ r @ s
                    context.view_layer.update()
                elif self.ground_down_mode == "MINIMUM":
                    # 计算出最小的z轴坐标,移动到指定的位置
                    if min_z is None:
                        min_z = z
                    elif z < min_z:
                        min_z = z
            if self.ground_down_mode == "MINIMUM" and min_z is not None:
                for obj in context.selected_objects:
                    context.view_layer.update()
                    l = get_loc_matrix(Vector((0, 0, to_z - min_z))) @ get_loc_matrix(obj.location)
                    r = get_rot_matrix(obj.rotation_euler)
                    s = get_sca_matrix(obj.scale)
                    obj.matrix_world = l @ r @ s
                    context.view_layer.update()

    def align_to_ground_ray_casting(self, context, dep):
        for obj in context.selected_objects:
            context.view_layer.update()
            if self.ground_ray_casting_rotation:
                self.ray_casting_rotation(context, obj, dep)
            else:
                point = _get_bound_box_center_point_(get_count_bound_box(obj))
                result, location, normal, index, o, matrix = context.scene.ray_cast(
                    dep,
                    point + Vector((0, 0, -0.5)),  # 偏移个0.5避免重叠
                    Vector((0, 0, -1))
                )
                if result:
                    context.view_layer.update()
                    loc = get_loc_matrix(obj.location)
                    rot = get_rot_matrix(obj.rotation_euler)
                    sca = get_sca_matrix(obj.scale)
                    obj.matrix_world = loc @ rot @ sca
                    context.view_layer.update()

                    point = _get_bound_box_center_point_(get_count_bound_box(obj))
                    result, location, normal, index, o, matrix = context.scene.ray_cast(
                        dep,
                        point + Vector((0, 0, -0.5)),  # 偏移个0.5避免重叠
                        Vector((0, 0, -1))
                    )
                    if result:
                        ot = get_loc_matrix(obj.matrix_world.translation)
                        diff = location - Vector((0, 0, (ot.inverted() @ point).z))

                        context.view_layer.update()
                        loc = get_loc_matrix(diff)
                        rot = get_rot_matrix(obj.rotation_euler)
                        sca = get_sca_matrix(obj.scale)
                        obj.matrix_world = loc @ rot @ sca
                        context.view_layer.update()

            context.view_layer.update()

    @staticmethod
    def ray_casting_rotation(context, obj, dep):
        """使用光线投射旋转
        使用法向来确认旋转
        两次投射确认旋转没问题
        """
        center_point = _get_bound_box_center_point_(get_count_bound_box(obj))
        result, location, normal, index, o, matrix = context.scene.ray_cast(
            dep,
            center_point + Vector((0, 0, -0.5)),  # 偏移个0.5避免重叠
            Vector((0, 0, -1))
        )
        if result:
            # 如果没投射到就不会对齐
            rot = get_rot_matrix(Euler(normal, 'XYZ'))

            loc = get_loc_matrix(obj.location)
            sca = get_sca_matrix(obj.scale)
            obj.matrix_world = loc @ rot @ sca

            rot = get_rot_matrix(obj.rotation_euler)
            ot = get_loc_matrix(obj.matrix_world.translation)
            center_point = _get_bound_box_center_point_(get_count_bound_box(obj))
            loc = get_loc_matrix(location - Vector((0, 0, (ot.inverted() @ center_point).z)))
            sca = get_sca_matrix(obj.scale)
            obj.matrix_world = loc @ rot @ sca


def get_count_bound_box(obj: bpy.types.Object) -> list[Vector]:
    """
    获取变换计算后的边界框
    计算旋转缩放和位置
    """
    # 计算变换后的边框并找到最小的Z轴
    mat = obj.matrix_world
    if obj.type in VALID_OBJ_TYPE:
        if obj.type == "MESH":
            data = vertices_co(obj, matrix=mat)
        else:
            data = np.array(bound_to_tuple(obj, matrix=mat))
        min_c = np.min(data, axis=0)
        max_c = np.max(data, axis=0)
        return _from_vector_get_bound_box_([Vector(min_c), Vector(max_c)])
    bound_box = [mat @ Vector(b) for b in obj.bound_box]
    return bound_box


def _get_min_z_(vector_list: list[Vector]) -> float:
    return min([c.z for c in vector_list])


def _from_vector_get_bound_box_(cbb: list[Vector]) -> list[Vector]:
    """获取变换后的边界框"""
    xl = [c[0] for c in cbb]
    yl = [c[1] for c in cbb]
    zl = [c[2] for c in cbb]
    max_x, min_x = max(xl), min(xl)
    max_y, min_y = max(yl), min(yl)
    max_z, min_z = max(zl), min(zl)
    return [
        Vector((max_x, min_y, min_z)),
        Vector((max_x, min_y, max_z)),
        Vector((max_x, max_y, max_z)),
        Vector((max_x, max_y, min_z)),
        Vector((min_x, min_y, min_z)),
        Vector((min_x, min_y, max_z)),
        Vector((min_x, max_y, max_z)),
        Vector((min_x, max_y, min_z)),
    ]


def _get_bound_box_center_point_(bound_box: list[Vector]) -> Vector:
    """获取中点"""
    return (Vector(bound_box[0]) + Vector(bound_box[7])) / 2  # 中点


def _get_bound_box_bottom_points_(bound_box: list[Vector]) -> list[Vector]:
    """获取物体边界框底部的5个点"""
    a = Vector(bound_box[0])
    b = Vector(bound_box[7])
    m = (a + b) / 2  # 中点
    return [a, b, Vector(bound_box[3]), Vector(bound_box[4]), m]
