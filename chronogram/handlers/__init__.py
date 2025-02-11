from .inbox import inbox_router
from .timecapsule import timecapsule_router
from .admin_panel import admin_router
from .settings import settings_router
from .common import common_router
from .payments import payments_router
from .delete_everything import delete_router
from .general import general_router


routers = (general_router, settings_router, payments_router, inbox_router, admin_router, delete_router,
           timecapsule_router, common_router)
