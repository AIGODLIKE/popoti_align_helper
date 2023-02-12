import bpy

from .pie import VIEW3D_MT_PIE_POPOTI_ALIGN_HELPER

kmi = None

kc = bpy.context.window_manager.keyconfigs.addon  # 获取按键配置addon的
km = kc.keymaps.new(name='3D View', space_type='VIEW_3D', region_type='WINDOW')


def reg_key():
    global kmi
    kmi = km.keymap_items.new(idname='wm.call_menu_pie',
                              type="A",
                              value='PRESS',
                              ctrl=True,
                              shift=False,
                              alt=True,
                              )
    kmi.show_expanded = True
    kmi.properties.name = VIEW3D_MT_PIE_POPOTI_ALIGN_HELPER.__name__


def un_reg_key():
    km.keymap_items.remove(kmi)


def register():
    reg_key()


def unregister():
    un_reg_key()
