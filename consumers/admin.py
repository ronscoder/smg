from django.contrib import admin
admin.site.index_title = ""
admin.site.site_header = "SGM OFFICE ADMIN" 
admin.site.site_title = "SGM ADMIN"
from .models import Consumer, ConsumerHistory, UnauthConsumer, Raid, CashFlow, SolarConsumer, EnergyAssessment, LoadSurvey, ConsumerInfo, Staff, StaffAssignment, ConsumerGroup, Tariff, TemporaryConnection, Todo, Meter, Complaint, Log,ComplaintLog, HistoryLog, HistoryWork, ConsumerWork, RaidGroup

class ConsumerGroupAdmin(admin.ModelAdmin):
  autocomplete_fields = ['consumer']
  #list_display = ['id', 'group_name']

class ConsumerGroupInline(admin.TabularInline):
  model = ConsumerGroup.consumer.through
  extra = 0

class CashFlowInline(admin.TabularInline):
  model = CashFlow
  extra = 0
class ConsumerHistoryInline(admin.StackedInline):
    model = ConsumerHistory
    extra = 0
class HistoryLogInline(admin.StackedInline):
  model = HistoryLog
  extra = 0
class HistoryWorkInline(admin.StackedInline):
  model = HistoryWork
  extra = 0
class ConsumerHistoryAdmin(admin.ModelAdmin):
  inlines = [HistoryLogInline, HistoryWorkInline]
  list_filter = ['tags',]
  #exclude = ['cash_flows']
class SolarConsumerInline(admin.StackedInline):
  model = SolarConsumer
  extra = 0
class SolarConsumerAdmin(admin.ModelAdmin):
  autocomplete_fields = ['consumer']
class RaidInline(admin.StackedInline):
    model = Raid
    extra = 0
#class ConsumerInfoAdmin(admin.ModelAdmin):
class ConsumerInfoInline(admin.TabularInline):
  model = ConsumerInfo.consumers.through
  extra = 0
class ConsumerWorkAdmin(admin.ModelAdmin):
  autocomplete_fields = ['consumer']
class ConsumerWorkInline(admin.StackedInline):
  model = ConsumerWork
  extra = 0
class ConsumerAdmin(admin.ModelAdmin):
    inlines = [ConsumerGroupInline, ConsumerHistoryInline,RaidInline, ConsumerWorkInline]
    search_fields = ['name','consumer_id','meter_no', 'address']
    list_filter = ['tags', 'phase']
    list_per_page = 10
class RaidEnergyAssessmentInline(admin.TabularInline):
  model = Raid.energy_assessments.through
  extra = 0
class RaidGroupInline(admin.TabularInline):
  #model = RaidGroup
  #extra = 0
  pass
class RaidAdmin(admin.ModelAdmin):
  search_fields = ['consumer__consumer_id', 'consumer__name', 'consumer__meter_no', 'consumer__address']
  inlines = [RaidEnergyAssessmentInline,] #RaidGroupInline] #CashFlowInline, ]
  list_filter = ['tags', 'date', 'theft', 'is_disconnected', 'action']
  date_hierarchy = 'date'
  exclude = ['energy_assessments']
  list_per_page = 5

class LoadSurveyAdmin(admin.ModelAdmin):
  #inlines = [LoadEnergyAssessmentIntInline]
  readonly_fields = ('day_units',)

class LoadSurveyInline(admin.TabularInline):
  model = EnergyAssessment.load_surveys.through
  #model = LoadSurvey
  extra = 0
class EnergyAssessmentAdmin(admin.ModelAdmin):
  inlines = [LoadSurveyInline, ]
  readonly_fields = ('day_counts','no_months','total_kw','total_units', 'energy_charge','demand_charge','penalised_energy_charge')
  exclude = ["load_surveys"]

class CashFlowAdmin(admin.ModelAdmin):
  date_hierarchy='txn_date'
  list_filter =['internal']

class UnauthConsumerAdmin(admin.ModelAdmin):
  inlines = [RaidInline]
  
class MeterAdmin(admin.ModelAdmin):
  autocomplete_fields = ['consumer']
  list_filter = ['prioritized', ]

admin.site.register(Consumer, ConsumerAdmin)
admin.site.register(ConsumerHistory, ConsumerHistoryAdmin)
admin.site.register(UnauthConsumer, UnauthConsumerAdmin)
admin.site.register(Raid, RaidAdmin)
admin.site.register(SolarConsumer, SolarConsumerAdmin)
admin.site.register(EnergyAssessment, EnergyAssessmentAdmin)
admin.site.register(LoadSurvey, LoadSurveyAdmin)
admin.site.register(CashFlow, CashFlowAdmin)
admin.site.register(ConsumerInfo)
admin.site.register(Staff)
admin.site.register(StaffAssignment)
admin.site.register(ConsumerGroup, ConsumerGroupAdmin)
#admin.site.register(ConsumerSelection)
admin.site.register(Tariff)
admin.site.register(TemporaryConnection)
admin.site.register(Todo)
admin.site.register(Meter, MeterAdmin)

class ComplaintLogInline(admin.TabularInline):
  model = ComplaintLog
  extra = 0

class LogAdmin(admin.ModelAdmin):
  pass
  
class ComplaintAdmin(admin.ModelAdmin):
  inlines = [ComplaintLogInline]
  autocomplete_fields = ['consumer']
  list_filter = ['is_resolved']
  #exclude = ["logs"]
  
admin.site.register(Log, LogAdmin) 
admin.site.register(Complaint, ComplaintAdmin)
admin.site.register(ConsumerWork, ConsumerWorkAdmin)
class RaidGroupAdmin(admin.ModelAdmin):
  filter_vertical = ["raids"]

admin.site.register(RaidGroup, RaidGroupAdmin)