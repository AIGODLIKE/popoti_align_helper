from . import icons, panel, preferences, localdb, ops, test, key, pie

bl_info = {
    "name": "POPOTI Align Helper",
    "description": "More friendly alignment based on observation perspective",
    "author": "AIGODLIKE Community(BlenderCN辣椒,小萌新)",
    "version": (1, 1),
    "blender": (3, 0, 0),
    "location": "Tool Panel",
    "support": "COMMUNITY",
    "category": "3D View",
}

mod_tuple = (
    pie,
    key,
    ops,
    test,
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
