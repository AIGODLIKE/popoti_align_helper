import bpy

from .ui.pie import AlignPieMenu

keymaps = []


def reg_key():
    kc = bpy.context.window_manager.keyconfigs.addon  # 获取按键配置addon的
    km = kc.keymaps.new(name='Object Mode', space_type='EMPTY', region_type='WINDOW')
    kmi = km.keymap_items.new(idname='wm.call_menu_pie',
                              type="A",
                              value='PRESS',
                              ctrl=True,
                              shift=False,
                              alt=True,
                              )
    kmi.properties.name = AlignPieMenu.bl_idname
    kmi.show_expanded = True

    keymaps.append((km, kmi))


def un_reg_key():
    for km, kmi in keymaps:
        km.keymap_items.remove(kmi)
    keymaps.clear()


def register():
    reg_key()


def unregister():
    un_reg_key()
