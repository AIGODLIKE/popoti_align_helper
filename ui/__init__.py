from . import panel, pie


def register():
    panel.register()
    pie.register()


def unregister():
    panel.unregister()
    pie.unregister()
