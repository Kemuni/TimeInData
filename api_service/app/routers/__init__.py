from . import healthcheck, users, notifications

routers_list = [
    healthcheck.router,
    users.router,
    notifications.router,
]

__all__ = [
    "routers_list",
]

