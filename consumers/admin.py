from django.contrib import admin

from .models import Consumer, ConsumerHistory, UnauthConsumer, Raid, CashFlow, SolarConsumer, EnergyAssessment, LoadSurvey, ConsumerInfo, Staff, StaffAssignment, ConsumerGroup, Tariff

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
class ConsumerHistoryAdmin(admin.ModelAdmin):
  inlines = [CashFlowInline]
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
class ConsumerAdmin(admin.ModelAdmin):
    inlines = [ConsumerGroupInline, ConsumerHistoryInline,RaidInline]
    search_fields = ['name','consumer_id','meter_no', 'address']
    list_filter = ['tags', 'phase']
    list_per_page = 10
class RaidEnergyAssessmentInline(admin.TabularInline):
  model = Raid.energy_assessments.through
  extra = 0
class RaidAdmin(admin.ModelAdmin):
    inlines = [RaidEnergyAssessmentInline, CashFlowInline, ]
    list_filter = ['tags', 'date', 'theft', 'is_disconnected']
    date_hierarchy = 'date'
    exclude = ['energy_assessments']

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

class UnauthConsumerAdmin(admin.ModelAdmin):
  inlines = [RaidInline]
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