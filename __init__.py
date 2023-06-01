from . import icons, panel, preferences, localdb, ops, test, key, pie

bl_info = {
    "name": "POPOTI Align Helper",
    "description": "More friendly alignment based on observation perspective",
    "author": "AIGODLIKE社区,小萌新",
    "version": (1, 2, 0),
    "blender": (3, 0, 0),
    "location": "Tool Panel",
    "support": "COMMUNITY",
    "category": "辣椒出品",
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
