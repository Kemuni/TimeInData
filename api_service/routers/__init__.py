from api_service.routers import users, healthcheck

routers_list = [
    healthcheck.router,
    users.router,
]

__all__ = [
    "routers_list",
]

