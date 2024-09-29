from . import icons, localdb


def register():
    icons.register()
    localdb.register()


def unregister():
    icons.unregister()
    localdb.unregister()
