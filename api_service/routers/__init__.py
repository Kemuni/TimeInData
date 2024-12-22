from . import healthcheck, users

routers_list = [
    healthcheck.router,
    users.router,
]

__all__ = [
    "routers_list",
]

