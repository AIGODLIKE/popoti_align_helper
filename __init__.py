from . import icons, ops, panel, preferences, localdb

bl_info = {
    "name": "POPOTI Align Helper",
    "description": "More friendly alignment based on observation perspective",
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
    localdb,
    preferences,
)


def register():
    for mod in mod_tuple:
        mod.register()


def unregister():
    for mod in mod_tuple:
        mod.unregister()
