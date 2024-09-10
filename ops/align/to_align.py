from .measure import MeasureObjects
from .to_matrix import get_loc_matrix, get_sca_matrix, get_rot_matrix


class ToAlign:
    def align_to_align(self, context):
        dep = context.evaluated_depsgraph_get()
        dep_objs = [obj.evaluated_get(dep) for obj in context.selected_objects]
        measures = MeasureObjects(dep_objs)

        to_loc = measures.align_mode_loc(self)
        for m in measures:
            obj = m.__object__
            rot = get_rot_matrix(obj.rotation_euler)
            sca = get_sca_matrix(obj.scale)
            
            loc = get_loc_matrix(self.__get_distribution_loc__(to_loc - m.min_bound_box_point, obj.location))

            context.view_layer.update()
            context.scene.objects[m.name].matrix_world = loc @ rot @ sca
            context.view_layer.update()
