import random
import unittest

import bpy


def clear_scene():
    """清理场景"""
    new = bpy.data.scenes.new("new")
    for sc in bpy.data.scenes:
        if sc != new:
            bpy.data.scenes.remove(sc)
    bpy.ops.outliner.orphans_purge(
        do_local_ids=True,
        do_linked_ids=True,
        do_recursive=True)


class OperatorTestCase(unittest.TestCase):

    def setUp(self):
        print('清理场景')
        clear_scene()
        for _ in range(10):
            bpy.ops.mesh.primitive_monkey_add()

        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.randomize_transform(random_seed=random.randint(0, 114),
                                           use_delta=False,
                                           loc=(10, 10, 10),
                                           rot=(1, 1, 1
                                                ))

    def test_operator(self):
        import itertools
        mode = ('ACTIVE', 'CURSOR', 'GROUND', 'DISTRIBUTION', 'ALIGN',)
        bl = (True, False)
        ax_items = ('X', 'Y', 'Z', '')
        axis = (set(i) for i in itertools.product(ax_items, ax_items, ax_items))
        num = {'0', '1', '2'}
        align = ('MIN', 'CENTER', 'MAX',)

        items = (mode, ('FIXED', 'ADJUSTMENT',), (0, 1, 2),
                 bl, bl, bl,
                 axis, axis, axis,
                 num,
                 ('ALL', 'MINIMUM',),
                 align, align, align)

        for item in itertools.product(*items):
            print("item", item)
            a, b, c, d, e, f, g, h, i, j, k, i, m, s = item
            self.assertEqual(
                bpy.ops.object.tool_kits_fast_align(
                    mode=a,
                    distribution_mode=b,
                    distribution_adjustment=c,
                    align_location=d,
                    align_rotation=e,
                    align_scale=f,
                    align_location_axis=g,
                    align_rotation_axis=h,
                    align_scale_axis=i,
                    distribution_sorted_axis=j,
                    ground_mode=k,
                    align_x_method=i,
                    align_y_method=m,
                    align_z_method=s,
                ),
                {"FINISHED"}
            )

    def test_property(self):
        from ..preferences import Preferences
        pref = Preferences.pref_()
        pref.show_text = True
        self.assertEqual(pref.show_text, True)
