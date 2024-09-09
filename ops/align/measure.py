import bpy
from mathutils import Vector


class Measure:
    __obj__: bpy.types.Object

    def __init__(self, obj):
        self.__obj__ = obj

    @property
    def name(self):
        return self.__obj__.name

    @property
    def bound_box(self) -> list[Vector]:
        return [Vector(i) for i in self.__obj__.bound_box]

    @property
    def dimensions(self) -> Vector:
        """物体尺寸"""
        return Vector()

    @property
    def center_co(self) -> Vector:
        """中心"""
        return Vector()

    @property
    def max_co(self) -> Vector:
        return Vector()

    @property
    def min_co(self) -> Vector:
        return Vector()


class MeasureObjects:
    __objs__: list[bpy.types.Object]

    def __init__(self, objects):
        self.__objs__ = objects

    @property
    def max_co(self) -> Vector:
        return Vector()

    @property
    def min_co(self) -> Vector:
        return Vector()
