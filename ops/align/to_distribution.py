from mathutils import Vector

from .measure import MeasureObjects
from .to_matrix import get_rot_matrix, get_loc_matrix, get_sca_matrix


class ToDistribution:

    def align_to_distribution(self, context):
        dep = context.evaluated_depsgraph_get()
        dep_objs = [obj.evaluated_get(dep) for obj in context.selected_objects]
        measures = MeasureObjects(dep_objs)
        if len(dep_objs) < 2:
            return
        offset = measures.min.copy()
        for m in measures.sort_by_axis(int(self.distribution_sorted_axis)):
            obj = m.__object__
            rot = get_rot_matrix(obj.rotation_euler)
            sca = get_sca_matrix(obj.scale)

            loc = get_loc_matrix(self.__get_distribution_loc__(offset - m.min_bound_box_point, obj.location))

            context.view_layer.update()
            context.scene.objects[m.name].matrix_world = loc @ rot @ sca
            context.view_layer.update()

            if self.distribution_mode == "FIXED":
                offset += measures.fixed_offset + m.dimensions
            elif self.distribution_mode == "ADJUSTMENT":
                dav = self.distribution_adjustment_value
                offset += m.dimensions + Vector((dav, dav, dav))

    def __get_distribution_loc__(self, a, b):
        x = "X" in self.align_location_axis
        y = "Y" in self.align_location_axis
        z = "Z" in self.align_location_axis
        return Vector((
            a.x if x else b.x,
            a.y if y else b.y,
            a.z if z else b.z,
        ))
