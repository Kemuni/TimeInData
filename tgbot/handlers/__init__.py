from . import start, settings, set_activity

routers_list = [
    start.router,
    settings.router,
    set_activity.router
]

__all__ = [
    "routers_list",
]
