from . import start, settings

routers_list = [
    start.router,
    settings.router,
]

__all__ = [
    "routers_list",
]
