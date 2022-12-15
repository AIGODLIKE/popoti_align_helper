from os.path import join, dirname

import bpy.utils

from . import ops, preferences, panel

bl_info = {
    "name": "Align Object",
    "description": "对齐物体",
    "author": "AIGODLIKE Community(BlenderCN辣椒,小萌新)",
    "version": (1, 0),
    "blender": (3, 4, 0),
    "location": "Tool Panel",
    "support": "COMMUNITY",
    "category": "Add Mesh",
}
name = bl_info['name']

mod_tuple = (
    ops,
    panel,
    preferences,
)
register_module, unregister_module = bpy.utils.register_submodule_factory(mod_tuple)


def register():
    register_module()


def unregister():
    unregister_module()
