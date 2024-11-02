from chronogram.handlers.inbox import inbox_router
from chronogram.handlers.timecapsule import timecapsule_router
from chronogram.handlers.admin_panel import admin_router
from chronogram.handlers.settings import settings_router
from chronogram.handlers.common import common_router
from chronogram.handlers.payments import payments_router
from chronogram.handlers.delete_everything import delete_router
from chronogram.handlers.general import general_router


from chronogram.handlers import routers


def test_proper_routers_order():
    """For the bot to function as expected, routers should be included into dispatcher in a certain order"""

    for i, router in enumerate((general_router, settings_router, payments_router, inbox_router, admin_router,
                                delete_router, timecapsule_router, common_router)):
        assert i == routers.index(router)
