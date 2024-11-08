import bpy
from bpy.props import BoolProperty
from bpy.types import AddonPreferences
from mathutils import Vector, Euler, Matrix


def get_kmi_operator_properties(kmi: 'bpy.types.KeyMapItem') -> dict:
    """获取kmi操作符的属性
    """
    properties = kmi.properties
    prop_keys = dict(properties.items()).keys()
    dictionary = {i: getattr(properties, i, None) for i in prop_keys}
    del_key = []
    for item in dictionary:
        prop = getattr(properties, item, None)
        typ = type(prop)
        if prop:
            if typ == Vector:
                # 属性阵列-浮点数组
                dictionary[item] = dictionary[item].to_tuple()
            elif typ == Euler:
                dictionary[item] = dictionary[item][:]
            elif typ == Matrix:
                dictionary[item] = tuple(i[:] for i in dictionary[item])
            elif typ == bpy.types.bpy_prop_array:
                dictionary[item] = dictionary[item][:]
            elif typ in (str, bool, float, int, set, list, tuple):
                ...
            elif typ.__name__ in [
                'TRANSFORM_OT_shrink_fatten',
                'TRANSFORM_OT_translate',
                'TRANSFORM_OT_edge_slide',
                'NLA_OT_duplicate',
                'ACTION_OT_duplicate',
                'GRAPH_OT_duplicate',
                'TRANSFORM_OT_translate',
                'OBJECT_OT_duplicate',
                'MESH_OT_loopcut',
                'MESH_OT_rip_edge',
                'MESH_OT_rip',
                'MESH_OT_duplicate',
                'MESH_OT_offset_edge_loops',
                'MESH_OT_extrude_faces_indiv',
            ]:  # 一些奇怪的操作符属性,不太好解析也用不上
                ...
                del_key.append(item)
            else:
                print('emm 未知属性,', typ, dictionary[item])
                del_key.append(item)
    for i in del_key:
        dictionary.pop(i)
    return dictionary


class AddonProperty(AddonPreferences):
    bl_idname = __package__

    show_text: BoolProperty(name='Show Button Text', default=True)

    @property
    def pref(self) -> 'AddonPreferences':
        """反回插件属性"""
        from .utils import get_pref
        return get_pref()

    def draw(self, context):
        self.layout.prop(self, 'show_text')
        from rna_keymap_ui import draw_kmi
        from .key import keymaps

        kc = bpy.context.window_manager.keyconfigs.user
        for km, kmi in keymaps:
            km = kc.keymaps.get(km.name)
            if km:
                kmi = km.keymap_items.get(kmi.idname, get_kmi_operator_properties(kmi))
                if kmi:
                    draw_kmi(["USER", "ADDON", "DEFAULT"], kc, km, kmi, self.layout, 0)


class_tuple = (
    AddonProperty,
)

register_class, unregister_class = bpy.utils.register_classes_factory(class_tuple)


def register():
    register_class()


def unregister():
    unregister_class()
