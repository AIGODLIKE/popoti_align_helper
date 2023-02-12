import bpy

kmi = None

kc = bpy.context.window_manager.keyconfigs.addon  # 获取按键配置addon的
km = kc.keymaps.new(name='3D View', space_type='VIEW_3D', region_type='WINDOW')


def reg_key():
    global kmi
    "VIEW3D_MT_PIE_POPOTI_ALIGN_HELPER"
    kmi = km.keymap_items.new(idname='wm.call_menu_pie',
                              type="A",
                              value='PRESS',
                              ctrl=True,
                              shift=False,
                              alt=True,
                              )


def un_reg_key():
    ...


def register():
    reg_key()


def unregister():
    un_reg_key()
