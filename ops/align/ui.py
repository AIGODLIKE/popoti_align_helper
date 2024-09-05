import bpy


class UI:
    # draw UI
    def draw_align_location(self, layout):
        row = layout.row()
        row.prop(self, 'align_location')
        row = row.row()
        row.active = self.align_location
        row.row().prop(self, 'align_location_axis')

    def draw_original(self, layout: bpy.types.UILayout):
        row = layout.row()
        row.prop(self, 'align_rotation')
        row = row.row()
        row.active = self.align_rotation
        row.prop(self, 'align_rotation_euler_axis')

        row = layout.row()
        row.prop(self, 'align_scale')
        row = row.row()
        row.active = self.align_scale
        row.prop(self, 'align_scale_axis')

        self.draw_align_location(layout)

    def draw_active(self, layout: bpy.types.UILayout):
        self.draw_original(layout)

    def draw_cursor(self, layout: bpy.types.UILayout):
        self.draw_original(layout)

    def draw_distribution(self, layout: bpy.types.UILayout):
        row = layout.row()
        row.label(text='Sort Axis')
        row.prop(self, 'distribution_sorted_axis', expand=True)
        layout.separator()
        self.draw_align_location(layout)
        if self.is_adjustment_mode:
            layout.prop(self, "distribution_adjustment_value")
        layout.row().prop(self, "distribution_mode", expand=True)

    def draw_ground(self, layout: bpy.types.UILayout):
        col = layout.column()

        col.row().prop(self, 'ground_mode', expand=True)
        # col.prop(self, 'align_to_ground_object') TODO ground object
        # col.prop_search(self, 'ground_object_name', bpy.data, 'objects')
        # col.separator(factor=2)

        row = col.row()
        row.prop(self, 'align_location')
        row = row.row()
        row.active = self.align_location
        row.prop(self, 'align_location_axis', expand=True)

    def draw_align(self, layout: bpy.types.UILayout):
        col = layout.column()

        row = col.row()
        row.label(text='X')
        row.active = ('X' in self.align_location_axis)
        row.prop(self, 'x_align_func', expand=True)

        row = col.row()
        row.label(text='Y')
        row.active = ('Y' in self.align_location_axis)
        row.prop(self, 'y_align_func', expand=True)

        row = col.row()
        row.label(text='Z')
        row.active = ('Z' in self.align_location_axis)
        row.prop(self, 'z_align_func', expand=True)

        layout.separator()
        self.draw_align_location(layout)
