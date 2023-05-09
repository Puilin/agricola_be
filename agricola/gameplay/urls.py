from django.urls import path, include
from rest_framework.routers import DefaultRouter
<<<<<<< HEAD

=======
>>>>>>> yh.hong
from . import views

router = DefaultRouter()
router.register(r'account', views.AccountViewSet)
<<<<<<< HEAD
router.register(r'player', views.PlayerViewSet)
router.register(r'playerboardstatus', views.PlayerBoardStatusViewSet)
router.register(r'boardposition', views.BoardPositionViewSet)
router.register(r'fenceposition', views.FencePositionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
=======

urlpatterns = [
    path('', include(router.urls)),
]
>>>>>>> yh.hong
