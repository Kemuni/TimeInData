from . import start, settings, set_activity, errors

routers_list = [
    start.router,
    settings.router,
    set_activity.router,
    errors.router,
]

__all__ = [
    "routers_list",
]
