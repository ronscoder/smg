from django.contrib import admin
admin.site.index_title = ""
admin.site.site_header = "SGM OFFICE ADMIN" 
admin.site.site_title = "SGM ADMIN"
from .models import Consumer, ConsumerHistory, UnauthConsumer, Raid, CashFlow, SolarConsumer, EnergyAssessment, LoadSurvey, ConsumerInfo, Staff, StaffAssignment, ConsumerGroup, Tariff, TemporaryConnection, Todo, DefectiveMeter, Complaint, Log,ComplaintLog, HistoryLog, ConsumerWork, RaidGroup, MultiConsumer, RaidGrouping, ConsumerGrouping, ConsumerNA, RaidObservation, State, Progress, RaidCashFlow, DefectiveMeterCashFlow, RaidProgress
from nested_admin import NestedModelAdmin, NestedStackedInline, NestedTabularInline
from django_admin_multi_select_filter.filters import MultiSelectFieldListFilter as mfilter, MultiSelectRelatedFieldListFilter as msrf
from more_admin_filters import MultiSelectFilter as MSF
class ConsumerGroupingAdmin(admin.ModelAdmin):
  search_fields = ['consumer__' + x for x in ['name', 'meter_no', 'consumer_id']]
  autocomplete_fields = ['consumer']
  list_filter = ['group__group_name', 'group__group_code']
  list_per_page = 10
  list_display = ['group__id','group__group_code','group__group_name', 'consumer__consumer_id', 'consumer__name', 'consumer__address']
  
class ConsumerGroupAdmin(admin.ModelAdmin):
  pass
  #autocomplete_fields = ['consumer']
  #filter_vertical = ['consumer']
  list_display = ['id','group_code', 'group_name', 'status']

class ConsumerGroupingInline(admin.TabularInline):
  model = ConsumerGrouping
  extra = 0

class CashFlowInline(admin.TabularInline):
  model = CashFlow
  extra = 0
class ConsumerHistoryInline(admin.StackedInline):
    model = ConsumerHistory
    extra = 0
class HistoryLogAdmin(admin.ModelAdmin):
  list_display = ['history', 'log', 'log__status']
#admin.site.register(HistoryLog, HistoryLogAdmin)
class HistoryLogInline(admin.StackedInline):
  model = HistoryLog
  extra = 0

class HistoryCashflowInline(admin.StackedInline):
  model = ConsumerHistory.cash_flows.through
  extra=0
class ConsumerHistoryAdmin(admin.ModelAdmin):
  inlines = [HistoryLogInline, HistoryCashflowInline]
  list_filter = [('tags__name', MSF),]
  list_per_page = 10
  exclude = ['cash_flows']
  list_display = ['__str__',]
class SolarConsumerInline(admin.StackedInline):
  model = SolarConsumer
  extra = 0
class SolarConsumerAdmin(admin.ModelAdmin):
  autocomplete_fields = ['consumer']
class RaidInline(admin.StackedInline):
    model = Raid
    extra = 0
    show_change_link = True
#class ConsumerInfoAdmin(admin.ModelAdmin):
class ConsumerInfoInline(admin.TabularInline):
  model = ConsumerInfo.consumers.through
  extra = 0
class ConsumerWorkAdmin(admin.ModelAdmin):
  autocomplete_fields = ['consumer']
  list_display = ['work__status','work','consumer']
  #list_filter = []
class ConsumerWorkInline(admin.StackedInline):
  model = ConsumerWork
  extra = 0
class MultiConsumerInline(admin.TabularInline):
  model = MultiConsumer
  fk_name = 'consumer'
  extra = 0
  show_change_link = True
class MultiConsumerBInline(admin.TabularInline):
  model = MultiConsumer
  fk_name = 'consumer_b'
  extra = 0
  show_change_link = True
class ConsumerAdmin(admin.ModelAdmin):
    inlines = [ConsumerGroupingInline, ConsumerHistoryInline,RaidInline, ConsumerWorkInline, MultiConsumerInline,MultiConsumerBInline]
    search_fields = ['name','consumer_id','meter_no', 'address']
    list_filter = ['tags', 'phase', ]
    list_per_page = 10
    list_display = ['consumer_id', 'name', 'address', 'meter_no', 'phase']
class RaidEnergyAssessmentInline(admin.StackedInline):
  model = Raid.energy_assessments.through
  extra = 0
class RaidGroupingInline(admin.TabularInline):
  model = RaidGrouping
  extra = 0
class RaidGroupingAdmin(admin.ModelAdmin):
  search_fields = ['raid__consumer__' + x for x in ['name', 'meter_no', 'consumer_id']]
  list_per_page = 10
  list_display = ['group__name', 'observations', 'raid__action', 'raid__consumer__name', 'raid__consumer__address', 'raid__consumer__meter_no', 'raid__comment', 'raid__info']
  def observations(self, obj):
    return ", ".join([x.text for x in obj.raid.observations.all()])
  list_filter = ['group__name', 'raid__action']
class RaidCashflowInline(admin.StackedInline):
  model = RaidCashFlow
  extra=0
class RaidGroupInline(admin.TabularInline):
  model = RaidGrouping
  extra = 0
class RaidProgressInline(admin.TabularInline):
  model = RaidProgress
  extra = 0

class RaidAdmin(admin.ModelAdmin):
  def formfield_for_foreignkey(self, db_field, request, **kwargs):
    print('field name', db_field.name)
    if db_field.name == "raid_groups":
      print('good there')
      kwargs["queryset"] = RaidGroup.objects.exclude(freezed=True)
    return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
  def formfield_for_manytomany(self, db_field, request, **kwargs):
    print('field name', db_field.name)
    if db_field.name == "raid_groups":
      print('good here')
      kwargs["queryset"] = RaidGroup.objects.exclude(freezed=True)
      print(kwargs)
    return super().formfield_for_manytomany(db_field, request, **kwargs)
  search_fields = ['consumer__consumer_id', 'consumer__name', 'consumer__meter_no', 'consumer__address']
  inlines = [RaidProgressInline, RaidEnergyAssessmentInline,RaidCashflowInline, RaidGroupInline] #RaidGroupInline] #CashFlowInline, ]
  list_filter = ['raid_groups','date', 'is_disconnected', 'action', 'observations']
  date_hierarchy = 'date'
  exclude = ['energy_assessments']
  list_per_page = 5
  autocomplete_fields = ['consumer']
  list_display = ['__str__', 'list_raidgroups']
  def list_raidgroups(self, obj):
    return "".join([f'[{rg.name}]' for rg in obj.raid_groups.all()])
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
  inlines = [HistoryCashflowInline, RaidCashflowInline]

class UnauthConsumerAdmin(admin.ModelAdmin):
  inlines = [RaidInline]
  
class DefectiveMeterAdmin(admin.ModelAdmin):
  autocomplete_fields = ['consumer']
  list_filter = ['prioritized', ]
  search_fields = ['meter_no', 'consumer__name']
admin.site.register(DefectiveMeter, DefectiveMeterAdmin)

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
  list_display = ['name', 'selected', 'freezed']

admin.site.register(RaidGroup, RaidGroupAdmin)

class MultiConsumerAdmin(admin.ModelAdmin):
  autocomplete_fields =['consumer', 'consumer_b']
  list_display = ['consumer__consumer_id','consumer__name','consumer__address','consumer__meter_no','consumer__connection_id','duplication','verified','dup_is_b' ,'consumer_b__consumer_id','consumer_b__name','consumer_b__address','consumer_b__meter_no','consumer_b__connection_id']
  list_filter = ['duplication']
  list_per_page = 10
  search_fields = ['consumer__consumer_id', 'consumer__name', 'consumer_b__consumer_id', 'consumer_b__name']

admin.site.register(MultiConsumer, MultiConsumerAdmin)

admin.site.register(RaidGrouping, RaidGroupingAdmin)

admin.site.register(ConsumerGrouping, ConsumerGroupingAdmin)
class ConsumerNAAdmin(admin.ModelAdmin):
  list_per_page = 10
  list_display = ['consumer_id', 'name', 'address']
admin.site.register(ConsumerNA, ConsumerNAAdmin)
admin.site.register(RaidObservation)
admin.site.register(State)
admin.site.register(Progress)
admin.site.register(RaidCashFlow)
class DefectiveMeterCashFlowAdmin(admin.ModelAdmin):
  search_fields = ['defective_meter__meter_no', 'defective_meter__consumer__name']
  autocomplete_fields = ['defective_meter']
  
admin.site.register(DefectiveMeterCashFlow, DefectiveMeterCashFlowAdmin)