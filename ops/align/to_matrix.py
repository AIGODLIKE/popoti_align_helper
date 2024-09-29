import bpy

from mathutils import Vector, Matrix, Euler


def get_loc_matrix(location: Vector) -> Matrix:
    return Matrix.Translation(location)


def get_rot_matrix(rotation: Euler) -> Matrix:
    return rotation.to_matrix().to_4x4()


def get_sca_matrix(scale: Vector):
    scale_mx = Matrix()
    for i in range(3):
        scale_mx[i][i] = scale[i]
    return scale_mx


def get_matrix(
        ops: "AlignObject",
        obj_matrix: Matrix,
        to: Matrix,
) -> Matrix:
    lo, ro, so = obj_matrix.decompose()

    lx, ly, lz = lo
    rx, ry, rz = ro.to_euler('XYZ')
    sx, sy, sz = so

    loc_t, rot_t, sc_t = to.decompose()
    tx, ty, tz = loc_t
    rot_x, rot_y, rot_z = rot_t.to_euler('XYZ')
    tsx, tsy, tsz = sc_t

    if ops.align_location:
        x = "X" in ops.align_location_axis
        y = "Y" in ops.align_location_axis
        z = "Z" in ops.align_location_axis
        loc = get_loc_matrix(Vector((
            tx if x else lx,
            ty if y else ly,
            tz if z else lz
        )))
    else:
        loc = get_loc_matrix(lo)

    if ops.align_rotation:
        x = "X" in ops.align_rotation_axis
        y = "Y" in ops.align_rotation_axis
        z = "Z" in ops.align_rotation_axis
        rot = get_rot_matrix(
            Euler((
                rot_x if x else rx,
                rot_y if y else ry,
                rot_z if z else rz
            ), 'XYZ')
        )
    else:
        rot = get_rot_matrix(ro.to_euler('XYZ'))

    if ops.align_scale:
        x = "X" in ops.align_scale_axis
        y = "Y" in ops.align_scale_axis
        z = "Z" in ops.align_scale_axis

        scale = get_sca_matrix(Vector((
            tsx if x else sx,
            tsy if y else sy,
            tsz if z else sz
        )))
    else:
        scale = get_sca_matrix(so)
    return loc @ rot @ scale


def to_matrix(
        ops: "AlignObject",
        objects: list[bpy.types.Object],
        to: Matrix
):
    """
    对齐到

    地面
    原点
    活动项
    游标

    都用这个方法
    """
    for obj in objects:
        mat = get_matrix(ops, obj.matrix_world, to)
        obj.matrix_world = mat
