from bpy.props import EnumProperty, FloatProperty, BoolProperty, StringProperty


def __get_v__(self, key, default):
    key = f"{self.align_mode}_{key}"
    if key in self:
        return self[key]
    else:
        return default


def __set_v__(self, key, value):
    k = f"{self.align_mode}_{key}"
    self[k] = value


ENUM_DISTRIBUTION_SORTED_AXIS = [
    ('0', 'X', 'Sort distribution by X axis'),
    ('1', 'Y', 'Sort distribution by Y axis'),
    ('2', 'Z', 'Sort distribution by X axis'),
]
ENUM_GROUND_DOWN_MODE = [
    ('ALL', 'All Object', ''),
    ('MINIMUM', 'Lowest Object', ''),
]
ENUM_GROUND_PLANE_MODE = [
    ('GROUND', 'Ground', 'Align To Ground'),
    ('DESIGNATED_OBJECT', 'Object', 'Align to Designated Object Z'),
    ('RAY_CASTING', 'Fall', 'Align To Z Ray Casting Object'),
]
ENUM_ALIGN_MODE = [
    ('ORIGINAL', 'World Original',
     'Aligning to the world origin is the same as resetting'),
    ('ACTIVE', 'Active', 'Align to Active Object'),
    ('CURSOR', 'Cursor', 'Align to Cursor(Scale reset 1)'),
    ('GROUND', 'Ground', 'Align Ground'),
    ('DISTRIBUTION', 'Distribution', 'Distribution Align'),
    ('ALIGN',
     'Align',
     'General alignment, you can set the alignment of each axis'
     '(maximum, center, minimum)'),
]
ENUM_DISTRIBUTION_MODE = [
    ("FIXED", "Fixed", "Fixed the nearest and farthest objects"),
    ("ADJUSTMENT", "Adjustment", "Adjust the distance between each object(Fixed active object)"),
]

ENUM_AXIS = [
    ('X', 'X', 'Align X Axis'),
    ('Y', 'Y', 'Align Y Axis'),
    ('Z', 'Z', 'Align Z Axis'),
]

VALID_OBJ_TYPE = ('FONT', 'OBJECT', 'META', 'SURFACE',
                  'CURVES', 'LATTICE', 'POINTCLOUD', 'GPENCIL', 'ARMATURE', 'MESH')

axis_enum_property = dict(
    name='Axis to be aligned',
    description='Select the axis to be aligned, multiple choices are allowed',
    items=ENUM_AXIS,
    options={'ENUM_FLAG', "SKIP_SAVE"})

align_method_enum_property = dict(
    items=[
        ('MIN', 'Min Point', 'Align to Min Point'),
        ('CENTER', 'Center', 'Center Align'),
        ('MAX', 'Max Point', 'Align to Max Point'),
    ],
    default='CENTER',
)

default_xyz_enum = 263


class OperatorProperty:
    align_mode: EnumProperty(items=ENUM_ALIGN_MODE)

    distribution_mode: EnumProperty(
        items=ENUM_DISTRIBUTION_MODE,
        default='FIXED'
    )
    distribution_adjustment_value: FloatProperty(
        name="Distribution interval value", default=1)

    align_location: BoolProperty(
        name='Location',
        get=lambda self: __get_v__(self, "Location", default=True),
        set=lambda self, value: __set_v__(self, "Location", value))
    align_rotation: BoolProperty(
        name='Rotate',
        get=lambda self: __get_v__(self, "Rotate", default=True),
        set=lambda self, value: __set_v__(self, "Rotate", value))
    align_scale: BoolProperty(
        name='Scale',
        get=lambda self: __get_v__(self, "Scale", default=False),
        set=lambda self, value: __set_v__(self, "Scale", value))

    def __get_lx__(self):
        key = f"{self.align_mode}_align_location_axis"
        if key not in self:
            if self.align_mode == "GROUND":
                # 地面默认只开Z
                return 4
            return default_xyz_enum
        return __get_v__(self, "align_location_axis", default=default_xyz_enum)

    align_location_axis: EnumProperty(
        get=__get_lx__,
        set=lambda self, value: __set_v__(self, "align_location_axis", value),
        **axis_enum_property
    )
    align_rotation_axis: EnumProperty(
        get=lambda self: __get_v__(self, "rotation_euler_axis", default=default_xyz_enum),
        set=lambda self, value: __set_v__(self, "rotation_euler_axis", value),
        **axis_enum_property
    )
    align_scale_axis: EnumProperty(
        get=lambda self: __get_v__(self, "scale_axis", default=default_xyz_enum),
        set=lambda self, value: __set_v__(self, "scale_axis", value),
        **axis_enum_property
    )

    distribution_sorted_axis: EnumProperty(
        name='Distribution sort axis',
        description='Align and sort the selected objects according'
                    ' to the selection axis to obtain the correct movement '
                    'position',
        items=ENUM_DISTRIBUTION_SORTED_AXIS)

    ground_down_mode: EnumProperty(items=ENUM_GROUND_DOWN_MODE, name="Down Mode")
    ground_plane_mode: EnumProperty(items=ENUM_GROUND_PLANE_MODE, name="Ground Plane Mode")
    ground_object_name: StringProperty(
        name='To Object',
        description='Align To Ground Object')
    ground_ray_casting_rotation: BoolProperty(name="Ray Casting Rotation", default=True)

    # 每个一个轴的对齐方式
    align_x_method: EnumProperty(name='X', **align_method_enum_property)
    align_y_method: EnumProperty(name='Y', **align_method_enum_property)
    align_z_method: EnumProperty(name='Z', **align_method_enum_property)
