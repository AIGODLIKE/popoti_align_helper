from mathutils import Vector


class TempProperty:
    """操作符运行时的临时属性"""
    min_co: Vector  # 最小的坐标
    max_co: Vector  # 最大的坐标
    objs_max_min_co: 'list[Vector]'
    objs_center_co: Vector  # 中心坐标
    data: dict  # 数据
    align_mode_location: Vector
    index: int
