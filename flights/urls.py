from django.urls import path, include
from rest_framework import routers

from user.urls import urlpatterns

router = routers.DefaultRouter()
router.register("",)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "flight"



