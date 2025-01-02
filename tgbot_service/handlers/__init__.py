from . import start, settings, set_activity, errors

routers_list = [
    start.router,
    *settings.routers_list,
    set_activity.router,
    errors.router,
]

__all__ = [
    "routers_list",
]
