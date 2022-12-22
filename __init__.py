
from . import icons, ops, panel, preferences

bl_info = {
    "name": "POPOTI对齐助手",
    "description": "更友好的基于观察视角的对齐",
    "author": "AIGODLIKE Community(BlenderCN辣椒,小萌新)",
    "version": (1, 0),
    "blender": (3, 0, 0),
    "location": "Tool Panel",
    "support": "COMMUNITY",
    "category": "3D View",
}

mod_tuple = (
    ops,
    icons,
    panel,
    preferences,
)


def register():
    for mod in mod_tuple:
        mod.register()


def unregister():
    for mod in mod_tuple:
        mod.unregister()
