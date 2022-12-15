import os
import enum
import bpy
from functools import cache
from os.path import join, dirname
from bpy.props import BoolProperty

previews_icons = bpy.utils.previews.new()  # 用于存所有的缩略图


class ICON:
    icons = {}
    thumbnail_suffix = ['.png', '.jpg']  # 缩略图后缀列表

    def load_icon(self, icon_path) -> 'bpy.types.ImagePreview':
        if icon_path and (icon_path not in previews_icons):
            icon = previews_icons.load(
                icon_path,
                icon_path,
                'IMAGE',
            )
            self.icons[icon_path] = icon
            return icon

    @staticmethod
    def clear_icon():
        global previews_icons

        if previews_icons:
            bpy.utils.previews.remove(previews_icons)
            ICON.icons.clear()
            previews_icons = None

    @staticmethod
    def new_icon():
        global previews_icons

        if not previews_icons:
            previews_icons = bpy.utils.previews.new()

    @staticmethod
    def _get_none_icon():
        global previews_icons
        if 'NONE' not in previews_icons:
            none_path = join(dirname(dirname(__file__)),
                             'rsc/icons/asset_none.png')
            previews_icons.load('NONE', none_path, 'IMAGE')

    @staticmethod
    def preload_icons():
        '''预加载图标
        在启动blender或是启用插件时加载图标
        '''
        ICON._get_none_icon()
        for item in PREF._all_asset_items():
            item.load_icon(item.icon_path)
