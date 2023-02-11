from os.path import basename, realpath, dirname

import bpy
from bpy.props import BoolProperty
from bpy.types import AddonPreferences

G_ADDON_NAME = basename(dirname(realpath(__file__)))


class Preferences:
    @staticmethod
    def pref_() -> 'AddonPreferences':
        return bpy.context.preferences.addons[AddonProperty.bl_idname].preferences

    @property
    def pref(self) -> 'AddonPreferences':
        """反回插件属性"""
        return Preferences.pref_()


class AddonProperty(Preferences, AddonPreferences):
    bl_idname = G_ADDON_NAME

    show_text: BoolProperty(name='Show Button Text', default=True)
    show_red: BoolProperty()

    def draw(self, context):
        self.layout.prop(self, 'show_text')


class_tuple = (
    AddonProperty,
)

register_class, unregister_class = bpy.utils.register_classes_factory(
    class_tuple)


def register():
    register_class()


def unregister():
    unregister_class()
