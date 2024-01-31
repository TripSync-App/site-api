from .DiscussionRoutes import discussion_router
from .MessageRoutes import message_router
from .UserRoutes import user_router
from .VacationRoutes import vacation_router

__all__ = ["vacation_router", "user_router", "discussion_router", "message_router"]
