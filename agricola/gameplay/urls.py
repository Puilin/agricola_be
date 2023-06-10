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
router.register(r'activationcost', views.ActivationCostViewSet),
router.register(r'jobcard', views.JobCardViewSet),
router.register(r'subfacilitycard', views.SubFacilityCardViewSet),
router.register(r'file', views.FileViewSet),
router.register(r'card', views.CardViewSet),
router.register(r'resourceimg', views.ResourceImgViewSet)
router.register(r'actionbox', views.ActionBoxViewSet)
router.register(r'jobcard', views.JobCardViewSet)
router.register(r'familyposition', views.FamilyPositionViewSet)
router.register(r'gamestatus', views.GameStatusViewSet)
router.register(r'playerresource', views.PlayerResourceViewSet)
router.register(r'resource', views.ResourceViewSet)
router.register(r'mainfacilitycard', views.MainFacilityCardViewSet)
router.register(r'playercard', views.PlayerCardViewSet)
router.register(r'penposition', views.PenPositionViewSet)
router.register(r'fstplayer', views.FstPlayerViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
