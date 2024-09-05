from mathutils import Vector, Matrix

"""
https://machin3.io/
"""

def get_loc_matrix(location):
    return Matrix.Translation(location)

def get_rot_matrix(rotation):
    return rotation.to_matrix().to_4x4()

def get_sca_matrix(scale):
    scale_mx = Matrix()
    for i in range(3):
        scale_mx[i][i] = scale[i]
    return scale_mx

def compensate_children(obj, oldmx, newmx):
    deltamx = newmx.inverted_safe() @ oldmx
    children = [c for c in obj.children]

    for c in children:
        pmx = c.matrix_parent_inverse
        c.matrix_parent_inverse = deltamx @ pmx

class ToActive:
    def align_to_active(self, context, obj):
        print("align_to_active Emm",)
        act_obj = context.active_object
        if not act_obj:
            act_obj = context.selected_objects[-1]
        if act_obj == obj:
            # 不要更改活动物体
            return

        amx = act_obj.matrix_world
        aloc, arot, asca = amx.decompose()
        alocx, alocy, alocz = aloc

        omx = obj.matrix_world
        oloc, orot, osca = omx.decompose()
        olocx, olocy, olocz = oloc

        if self.align_location:
            locx = alocx if  'X' in self.align_location_axis else olocx
            locy = alocy if  'Y' in self.align_location_axis else olocy
            locz = alocz if  'Z' in self.align_location_axis else olocz
            loc = get_loc_matrix(Vector((locx, locy, locz)))
        else:
            loc = get_loc_matrix(oloc)

        rot = orot.to_matrix().to_4x4()

        sca = get_sca_matrix(osca)

        if obj.children and context.scene.tool_settings.use_transform_skip_children:
            compensate_children(obj, omx, loc @ rot @ sca)

        obj.matrix_world = loc @ rot @ sca