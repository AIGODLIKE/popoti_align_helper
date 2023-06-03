import bpy
from .operator import OperatorTestCase

DEBUG = False


def run_unittest():
    global DEBUG
    for area in bpy.context.screen.areas:
        if DEBUG and area.type == "VIEW_3D":
            import unittest
            unittest.main(exit=False, module=__package__)
            DEBUG = False
    return 1


def reg_test():
    bpy.app.timers.register(run_unittest, first_interval=1)


def register():
    reg_test()


def unregister():
    if bpy.app.timers.is_registered(run_unittest):
        bpy.app.timers.unregister(run_unittest)
