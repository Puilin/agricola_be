from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Account)
admin.site.register(Player)
admin.site.register(PlayerBoardStatus)
admin.site.register(BoardPosition)
admin.site.register(FencePosition)
admin.site.register(Resource)
admin.site.register(PlayerResource)
admin.site.register(File)
admin.site.register(ResourceImg)
admin.site.register(Card)
admin.site.register(SubFacilityCard)
admin.site.register(JobCard)
admin.site.register(MainFacilityCard)
