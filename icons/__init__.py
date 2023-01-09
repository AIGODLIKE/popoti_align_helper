import os
from os.path import dirname, join

import bpy.utils.previews

previews_icons = bpy.utils.previews.new()  # 用于存所有的缩略图
thumbnail_suffix = ['.png', '.jpg']  # 缩略图后缀列表


def get_icon(name='None'):
    """
    load icon
    :param name:
    :return:
    """
    return previews_icons[name].icon_id


def preload_icons():
    """预加载图标
    在启动blender或是启用插件时加载图标
    """

    folder_path = dirname(__file__)
    for file in os.listdir(folder_path):
        icon_path = join(folder_path, file)
        is_file = os.path.isfile(icon_path)
        is_icon = file[-4:] in thumbnail_suffix
        if is_icon and is_file:
            previews_icons.load(
                file[:-4],
                icon_path,
                'IMAGE',
            )


def register():
    preload_icons()


def unregister():
    previews_icons.clear()


if __name__ == "__main__":
    register()
