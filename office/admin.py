from django.contrib import admin
from .models import Work, WorkProgress, Progress
#from consumers.models import ConsumerWork

admin.site.index_title = ""
admin.site.site_header = "SGM OFFICE ADMIN" 
admin.site.site_title = "SGM ADMIN"
class ProgressAdmin(admin.ModelAdmin):
  pass

class ProgressInline(admin.TabularInline):
  model = WorkProgress
  extra = 0
  
class WorkAdmin(admin.ModelAdmin):
  inlines = [ProgressInline]
  list_filter = ['priority','status']
  list_per_page = 10
  
admin.site.register(Progress, ProgressAdmin)
admin.site.register(Work, WorkAdmin)