import bpy
from bpy.props import BoolProperty
from bpy.types import AddonPreferences


class AddonProperty(AddonPreferences):
    bl_idname = __package__

    show_text: BoolProperty(name='Show Button Text', default=True)
    show_red: BoolProperty()

    @property
    def pref(self) -> 'AddonPreferences':
        """反回插件属性"""
        from .utils import get_pref
        return get_pref()

    def draw(self, context):
        self.layout.prop(self, 'show_text')
        from rna_keymap_ui import draw_kmi
        from .key import kc, km, kmi

        draw_kmi(km.keymap_items, kc, km, kmi, self.layout, 0)


class_tuple = (
    AddonProperty,
)

register_class, unregister_class = bpy.utils.register_classes_factory(
    class_tuple)


def register():
    register_class()


def unregister():
    unregister_class()
