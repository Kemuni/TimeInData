from . import start, settings, set_activity, errors, data_summary

routers_list = [
    errors.router,
    start.router,
    *settings.routers_list,
    set_activity.router,
    data_summary.router
]

__all__ = [
    "routers_list",
]
