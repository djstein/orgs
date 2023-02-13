from django.urls import path
from ninja import NinjaAPI

from ..api import router as organization_router

api = NinjaAPI()
api.add_router("/organizations/", organization_router)
urlpatterns = (path("api/", api.urls),)
