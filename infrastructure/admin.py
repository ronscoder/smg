from django.contrib import admin
from .models import Feeder, DTR
# Register your models here.
admin.site.index_title = ""
admin.site.site_header = "SGM OFFICE ADMIN" 
admin.site.site_title = "SGM ADMIN"
class DTRAdmin(admin.ModelAdmin):
  list_filter = ['feeder', 'capacity_kva']
  list_per_page = 5
admin.site.register(Feeder)
admin.site.register(DTR, DTRAdmin)
