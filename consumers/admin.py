from django.contrib import admin

from .models import Consumer, ConsumerHistory, UnauthConsumer, Raid, CashFlow, SolarConsumer, EnergyAssessment, LoadSurvey#,LoadEnergyAssessmentInt

#class EnergyAssessmentAdmin(admin.ModelAdmin):
  

class ConsumerHistoryInline(admin.StackedInline):
    model = ConsumerHistory
    extra = 0
class RaidCashFlowInline(admin.TabularInline):
   model = Raid.cash_flows.through
   extra = 0
class ConsumerHistoryAdmin(admin.ModelAdmin):
  #inlines = [CashFlowInline]
  list_filter = ['tags',]
class SolarConsumerInline(admin.StackedInline):
  model = SolarConsumer
  extra = 0
class RaidInline(admin.StackedInline):
    model = Raid
    extra = 0
class ConsumerAdmin(admin.ModelAdmin):
    inlines = [ConsumerHistoryInline,RaidInline]
    search_fields = ['name','consumer_id','meter_no', 'address']
    list_filter = ['tags', 'phase']
    list_per_page = 10
    
class RaidAdmin(admin.ModelAdmin):
    inlines = [RaidCashFlowInline, ]
    list_filter = ['tags', 'date', 'theft']
    date_hierarchy = 'date'
    exclude = ['cash_flows']
'''
class LoadEnergyAssessmentIntInline(admin.TabularInline):
  model = LoadEnergyAssessmentInt
  extra = 0
'''
class LoadSurveyAdmin(admin.ModelAdmin):
  #inlines = [LoadEnergyAssessmentIntInline]
  readonly_fields = ('day_units',)

class LoadSurveyInline(admin.TabularInline):
  model = EnergyAssessment.load_surveys.through
  #model = LoadSurvey
  extra = 0
class EnergyAssessmentAdmin(admin.ModelAdmin):
  inlines = [LoadSurveyInline, ]
  readonly_fields = ('day_counts','total_kw','total_units', 'energy_charge','demand_charge','penalised_energy_charge')
  exclude = ["load_surveys"]

admin.site.register(Consumer, ConsumerAdmin)
admin.site.register(ConsumerHistory, ConsumerHistoryAdmin)
admin.site.register(UnauthConsumer)
admin.site.register(Raid, RaidAdmin)
admin.site.register(SolarConsumer)
admin.site.register(EnergyAssessment, EnergyAssessmentAdmin)
admin.site.register(LoadSurvey, LoadSurveyAdmin)