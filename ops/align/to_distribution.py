from mathutils import Vector

from .measure import MeasureObjects
from .to_matrix import get_rot_matrix, get_loc_matrix, get_sca_matrix


class ToDistribution:

    @staticmethod
    def active_distribution_index(items, context) -> int:
        names = [i.name for i in items]
        if context.active_object and context.active_object.name in names:
            active_name = context.active_object.name
        else:
            active_name = names[0]
        return names.index(active_name)

    def align_to_distribution(self, context):
        dep = context.evaluated_depsgraph_get()
        dep_objs = [obj.evaluated_get(dep) for obj in context.selected_objects]
        measures = MeasureObjects(dep_objs)

        if len(dep_objs) < 2:
            return

        offset = measures.min.copy()

        items = measures.sort_by_axis(int(self.distribution_sorted_axis))

        if self.distribution_mode == "FIXED":
            for item in items:
                obj = item.__object__
                rot = get_rot_matrix(obj.rotation_euler)
                sca = get_sca_matrix(obj.scale)

                loc = get_loc_matrix(self.__mix_two_loc__(offset - item.min_bound_box_point, obj.location))

                context.view_layer.update()
                context.scene.objects[item.name].matrix_world = loc @ rot @ sca
                context.view_layer.update()

                offset += measures.fixed_offset + item.dimensions
        elif self.distribution_mode == "ADJUSTMENT":

            dav = self.distribution_adjustment_value
            dv = Vector((dav, dav, dav))

            active_index = self.active_distribution_index(items, context)
            active = items[active_index]

            # -负 前-|-正 后-
            for (orientation, offset, items) in (
                    ["positive", active.max.copy(), items[active_index + 1:]],  # 正 后
                    ["negative", active.min.copy(), list(reversed(items[:active_index]))],  # 负 前
            ):
                is_negative = orientation == "negative"
                for item in items:
                    obj = item.__object__
                    rot = get_rot_matrix(obj.rotation_euler)
                    sca = get_sca_matrix(obj.scale)

                    if is_negative:
                        loc_a = offset - dv - item.max_bound_box_point
                        offset = loc_a + item.min_bound_box_point
                    else:
                        loc_a = offset + dv - item.min_bound_box_point
                        offset = loc_a + item.max_bound_box_point
                    loc = get_loc_matrix(self.__mix_two_loc__(loc_a, obj.location))

                    context.view_layer.update()
                    context.scene.objects[item.name].matrix_world = loc @ rot @ sca
                    context.view_layer.update()

    def __mix_two_loc__(self, a, b):
        x = "X" in self.align_location_axis
        y = "Y" in self.align_location_axis
        z = "Z" in self.align_location_axis
        return Vector((
            a.x if x else b.x,
            a.y if y else b.y,
            a.z if z else b.z,
        ))
