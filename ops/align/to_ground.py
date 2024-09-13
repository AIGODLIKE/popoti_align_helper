import bpy
from mathutils import Vector, Matrix, Euler

from .to_matrix import get_loc_matrix, get_rot_matrix, get_sca_matrix


class ToGround:
    def align_to_ground(self, context):
        print("align_to_ground")
        print(
            self.ground_down_mode,
            self.ground_plane_mode,
            self.ground_object_name,
        )
        dep = context.evaluated_depsgraph_get()
        if self.ground_plane_mode == "RAY_CASTING":
            self.align_to_ground_ray_casting(context, dep)
        else:
            matrix = Matrix()

            if self.ground_plane_mode == "DESIGNATED_OBJECT":
                if self.ground_object_name not in context.scene.objects:
                    return
                obj = context.scene.objects[self.ground_object_name]
                mp = obj.bound_box[2]
                matrix = obj.matrix_world @ Matrix.Translation(mp)
            to_z = matrix.translation.z  # 只使用z轴数据
            # 计算每一个物体到0的偏移并移动
            print(to_z)
            min_z = None
            for obj in context.selected_objects:
                z = get_bound_box_count_point(obj.evaluated_get(dep)).z + obj.location.z  # 需工偏移的位置

                if self.ground_down_mode == "ALL":
                    context.view_layer.update()
                    obj.matrix_world @= get_loc_matrix(Vector((0, 0, to_z - z)))
                    context.view_layer.update()
                elif self.ground_down_mode == "MINIMUM":
                    # 计算出最小的z轴坐标,移动到指定的位置
                    if min_z is None:
                        min_z = z
                    elif z < min_z:
                        min_z = z
            if self.ground_down_mode == "MINIMUM" and min_z is not None:
                for obj in context.selected_objects:
                    z = get_bound_box_count_point(obj.evaluated_get(dep)).z + obj.location.z  # 需工偏移的位置
                    context.view_layer.update()
                    obj.matrix_world @= get_loc_matrix(Vector((0, 0, to_z - min_z)))
                    context.view_layer.update()

    def align_to_ground_ray_casting(self, context, dep):
        for obj in context.selected_objects:
            e_obj = obj.evaluated_get(dep)
            translate_location: Vector = None

            rot = get_rot_matrix(e_obj.rotation_euler)

            if self.ground_ray_casting_rotation:
                # 使用法向来确认旋转
                point = get_bound_box_count_point(e_obj)
                result, location, normal, index, o, matrix = context.scene.ray_cast(
                    dep,
                    point + e_obj.location + Vector((0, 0, -0.5)),  # 偏移个0.5避免重叠
                    Vector((0, 0, -1))
                )
                if result:
                    translate_location = location - point
                    rot = get_rot_matrix(Euler(normal, 'XYZ'))
            else:
                # 每个物体检测5个点,找高度最高的那一个点
                for point in get_bound_box_bottom_points(e_obj):
                    result, location, normal, index, o, matrix = context.scene.ray_cast(
                        dep,
                        point + e_obj.location + Vector((0, 0, -0.5)),  # 偏移个0.5避免重叠
                        Vector((0, 0, -1))
                    )
                    if result:
                        l = location - point
                        if translate_location is None:
                            translate_location = l
                        elif l.z > translate_location.z:
                            translate_location = l

            if translate_location:
                context.view_layer.update()
                loc = get_loc_matrix(translate_location)
                sca = get_sca_matrix(e_obj.scale)
                obj.matrix_world = loc @ rot @ sca
                context.view_layer.update()


def get_bound_box_bottom_points(obj: bpy.types.Object) -> list[Vector]:
    """获取物体边界框底部的5个点"""
    a = Vector(obj.bound_box[0])
    b = Vector(obj.bound_box[7])
    m = (a + b) / 2  # 中点
    return [a, b, Vector(obj.bound_box[3]), Vector(obj.bound_box[4]), m]


def get_bound_box_count_point(obj: bpy.types.Object) -> Vector:
    a = Vector(obj.bound_box[0])
    b = Vector(obj.bound_box[7])
    m = (a + b) / 2  # 中点
    return m
