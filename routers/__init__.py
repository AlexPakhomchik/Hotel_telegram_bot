from .booking import booking_router
from .staff import staff_router
# from .inventory import inventory_router
# from .housekeeping import housekeeping_router
# from .maintenance import maintenance_router
# from .reports import reports_router

all_routers = [
    booking_router,
    staff_router,
    # inventory_router,
    # housekeeping_router,
    # maintenance_router,
    # reports_router,
]
