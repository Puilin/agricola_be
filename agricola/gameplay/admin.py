from django.contrib import admin
from .models import Account, Player, PlayerBoardStatus, BoardPosition, FencePosition, Resource, PlayerResource

# Register your models here.
admin.site.register(Account)
admin.site.register(Player)
admin.site.register(PlayerBoardStatus)
admin.site.register(BoardPosition)
admin.site.register(FencePosition)
admin.site.register(Resource)
admin.site.register(PlayerResource)