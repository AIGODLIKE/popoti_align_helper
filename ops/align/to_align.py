from mathutils import Vector

from .measure import MeasureObjects
from .to_matrix import get_loc_matrix, get_sca_matrix, get_rot_matrix


class ToAlign:
    def align_to_align(self, context):
        dep = context.evaluated_depsgraph_get()
        dep_objs = [obj.evaluated_get(dep) for obj in context.selected_objects]
        measures = MeasureObjects(dep_objs)
        to_loc = self.__mix_loc__([measures.min, measures.center, measures.max])
        for m in measures:
            obj = m.__object__
            rot = get_rot_matrix(obj.rotation_euler)
            sca = get_sca_matrix(obj.scale)

            bp = m.min_bound_box_point
            to = to_loc - self.__mix_loc__([bp, Vector(), bp * -1])

            loc = get_loc_matrix(self.__get_distribution_loc__(to, obj.location))

            context.view_layer.update()
            context.scene.objects[m.name].matrix_world = loc @ rot @ sca
            context.view_layer.update()

    def __mix_loc__(self, matrix_items):
        items = ["MIN", "CENTER", "MAX", ]
        x = items.index(self.align_x_method)
        y = items.index(self.align_y_method)
        z = items.index(self.align_z_method)
        return Vector((
            matrix_items[x].x,
            matrix_items[y].y,
            matrix_items[z].z
        ))
