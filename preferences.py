import bpy
from bpy.types import AddonPreferences

from functools import cache


class Preferences:
    import preferences
    addon = preferences.AddonProperty

    @staticmethod
    def _static_pref(string=False) -> 'addon':
        """
        反回插件属性并缓存
        每一次开关插件都需要清除缓存
        静态方法
        """

    @cache
    def _pref() -> 'addon':
        """缓存偏好设置"""
        return Preferences._static_pref()

    @property
    def pref(self) -> 'addon':
        """反回插件属性"""
        return Preferences._pref()


class AddonProperty(Preferences, AddonPreferences):
    bl_idname = name

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
