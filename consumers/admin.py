from django.contrib import admin

from .models import Consumer, ConsumerHistory, UnauthConsumer, Raid

class ConsumerHistoryInline(admin.StackedInline):
    model = ConsumerHistory
    extra = 0
    
class ConsumerHistoryAdmin(admin.ModelAdmin):
    list_filter = ['tags',]

class RaidInline(admin.StackedInline):
    model = Raid
    extra = 0
class ConsumerAdmin(admin.ModelAdmin):
    inlines = [ConsumerHistoryInline,RaidInline]
    search_fields = ['name','consumer_id','meter_no', 'address']
    list_filter = ['tags', 'phase']
    list_per_page = 10
    
class RaidAdmin(admin.ModelAdmin):
    list_filter = ['tags', 'date', 'theft']
    date_hierarchy = 'date'

admin.site.register(Consumer, ConsumerAdmin)
admin.site.register(ConsumerHistory, ConsumerHistoryAdmin)
admin.site.register(UnauthConsumer)
admin.site.register(Raid, RaidAdmin)
