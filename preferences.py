from os.path import basename, realpath

import bpy
from bpy.types import AddonPreferences

G_ADDON_NAME = basename(realpath(__file__))


class Preferences:
    @staticmethod
    def _pref() -> 'AddonPreferences':
        return bpy.context.preferences.addons[AddonProperty.bl_idname].preferences

    @property
    def pref(self) -> 'AddonPreferences':
        """反回插件属性"""
        return Preferences._pref()


class AddonProperty(Preferences, AddonPreferences):
    bl_idname = G_ADDON_NAME

    def draw(self, context):
        ...


class_tuple = (
    AddonProperty,
)

register_class, unregister_class = bpy.utils.register_classes_factory(
    class_tuple)


def register():
    register_class()


def unregister():
    unregister_class()
