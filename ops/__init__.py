import bpy

from .align_object import AlignObject
from .align_object_by_view import ObjectAlignByView

register_classes, unregister_classes = bpy.utils.register_classes_factory((
    ObjectAlignByView,
    AlignObject
))


def register():
    register_classes()


def unregister():
    unregister_classes()
