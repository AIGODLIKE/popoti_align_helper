import bpy
from bpy.types import AddonPreferences

from functools import cache


class Preferences:
    import preferences
    addon = preferences.AddonProperty

    @staticmethod
    def _static_pref(string=False) -> 'addon':
        """
        ���ز�����Բ�����
        ÿһ�ο��ز������Ҫ�������
        ��̬����
        """

    @cache
    def _pref() -> 'addon':
        """����ƫ������"""
        return Preferences._static_pref()

    @property
    def pref(self) -> 'addon':
        """���ز������"""
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
