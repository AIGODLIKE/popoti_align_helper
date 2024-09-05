import bpy
from bpy.props import EnumProperty, FloatProperty, BoolProperty, StringProperty


def __get_v__(self, key, default):
    key = f"{self.align_mode}_{key}"
    if key in self:
        return self[key]
    else:
        return default


def __set_v__(self, key, value):
    self[f"{self.align_mode}_{key}"] = value


ENUM_DISTRIBUTION_SORTED_AXIS = [
    ('0', 'X', 'Sort distribution by X axis'),
    ('1', 'Y', 'Sort distribution by Y axis'),
    ('2', 'Z', 'Sort distribution by X axis'), ]
ENUM_GROUND_MODE = [('ALL', 'All Object', ''),
                    ('MINIMUM', 'Lowest Object', ''), ]
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
    ("ADJUSTMENT", "Adjustment",
     "Adjust the distance between each object(Fixed active object)"), ]
ENUM_ALIGN_FUNC = [
    ('MIN', 'Min Point', 'Align to Min Point'),
    ('CENTER', 'Center', 'Center Align'),
    ('MAX', 'Max Point', 'Align to Max Point'),
]

ENUM_AXIS = [('X', 'X', 'Align X Axis'),
             ('Y', 'Y', 'Align Y Axis'),
             ('Z', 'Z', 'Align Z Axis'),
             ]
VALID_OBJ_TYPE = ('FONT', 'OBJECT', 'META', 'SURFACE',
                  'CURVES', 'LATTICE', 'POINTCLOUD', 'GPENCIL', 'ARMATURE')

axis_enum_property = dict(
    name='Axis to be aligned',
    description='Select the axis to be aligned, multiple choices are allowed',
    items=ENUM_AXIS,
    options={'ENUM_FLAG'})

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
        key = f"{self.align_mode}_Location Axis"
        if self.align_mode == "GROUND" and key not in self:
            # 地面默认只开Z
            return 4
        return __get_v__(self, "Location Axis", default=default_xyz_enum)

    align_location_axis: EnumProperty(
        get=__get_lx__,
        set=lambda self, value: __set_v__(self, "Location Axis", value),
        **axis_enum_property
    )
    align_rotation_euler_axis: EnumProperty(
        get=lambda self: __get_v__(self, "Rotation Euler Axis", default=default_xyz_enum),
        set=lambda self, value: __set_v__(self, "Rotation Euler Axis", value),
        **axis_enum_property
    )
    align_scale_axis: EnumProperty(
        get=lambda self: __get_v__(self, "Scale Axis", default=default_xyz_enum),
        set=lambda self, value: __set_v__(self, "Scale Axis", value),
        **axis_enum_property
    )

    distribution_sorted_axis: EnumProperty(
        name='Distribution sort axis',
        description='Align and sort the selected objects according'
                    ' to the selection axis to obtain the correct movement '
                    'position',
        items=ENUM_DISTRIBUTION_SORTED_AXIS)

    ground_mode: EnumProperty(
        items=ENUM_GROUND_MODE)
    align_to_ground_object: BoolProperty(name='Align To Ground Object')
    ground_object_name: StringProperty(
        name='To Object',
        description='Align To Ground Object')

    # 每个一个轴的对齐方式
    x_align_func: EnumProperty(name='X', items=ENUM_ALIGN_FUNC,
                               default='CENTER', )
    y_align_func: EnumProperty(name='Y', items=ENUM_ALIGN_FUNC,
                               default='CENTER', )
    z_align_func: EnumProperty(name='Z', items=ENUM_ALIGN_FUNC,
                               default='CENTER', )

    @property
    def is_fixed_mode(self):
        return self.distribution_mode == "FIXED"

    @property
    def is_adjustment_mode(self):
        return self.distribution_mode == "ADJUSTMENT"

    @property
    def is_distribution_mode(self):
        return self.align_mode == "DISTRIBUTION"

    @property
    def is_align_mode(self):
        return self.align_mode == "ALIGN"

    @property
    def is_ground_mode(self):
        return self.align_mode == "GROUND"

    @property
    def is_distribution_fixed_mode(self):  # 是分布模式并且是固定间距模式
        return self.is_fixed_mode and self.is_distribution_mode

    @property
    def is_distribution_adjustment_mode(self):  # 是分布模式并且是固定间距模式
        return self.is_distribution_mode and self.is_adjustment_mode

    @property
    def is_align_to_ground_object(self) -> bool:
        ground = self.ground_object and self.is_ground_mode
        return self.align_to_ground_object and ground

    @property
    def ground_object(self) -> bpy.types.Object:
        name = self.ground_object_name
        if name:
            return bpy.data.objects.get(name, None)
