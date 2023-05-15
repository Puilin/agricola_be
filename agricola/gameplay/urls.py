from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'account', views.AccountViewSet)
router.register(r'player', views.PlayerViewSet)
router.register(r'playerboardstatus', views.PlayerBoardStatusViewSet)
router.register(r'boardposition', views.BoardPositionViewSet)
router.register(r'fenceposition', views.FencePositionViewSet)
router.register(r'periodcard', views.PeriodCardViewSet)
router.register(r'activationcost', views.ActivationCostViewSet)
router.register(r'file', views.FileViewSet)
router.register(r'resourceimg', views.ResourceImgViewSet)
router.register(r'actionbox', views.ActionBoxViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
