from django.contrib import admin

from .models import Project, Site, Material, Unit, WorkItem, ItemRate,WorkGroup, Package,Party, MaterialBOQ, MaterialExisting, MaterialDismantled, WorkProgress, CashFlow, Person
from nested_admin import NestedModelAdmin, NestedStackedInline, NestedTabularInline

class PackageAdmin(admin.ModelAdmin):
  list_display = ['name', 'list_sites']
  def list_sites(self, obj):
    return ", ".join([f'{i+1}. {x.name} | {x.status}' for i, x in enumerate(obj.sites.all())])
class WorkProgressInline(admin.TabularInline):
  model = WorkProgress
  extra = 0
  show_change_link = True
class WorkItemAdmin(admin.ModelAdmin):
  list_display = ['name', 'unit__short', 'ref_material__name']
  list_filter = ['ref_material__name']
  list_per_page = 5
  readonly_fields = ['site_quantity']
  inlines = [WorkProgressInline]
class ItemRateAdmin(admin.ModelAdmin):
  list_display = ['work_item__name','rate','work_item__unit__short', 'party__name','work_item__ref_material']
  list_per_page = 10
  list_filter = ['party__name', 'work_item__name']
class ItemRateGroupAdmin(admin.ModelAdmin):
  pass
  #list_display = ['package', 'party']
class WorkGroupAdmin(admin.ModelAdmin):
  list_display = ['package__name','party__name', 'estimate', 'expended', 'margin', 'total_lt_poles']
  list_filter = ['party', 'package']
  readonly_fields = ['estimate', 'expended', 'margin', 'total_lt_poles']

class MaterialBOQAdmin(admin.ModelAdmin):
  list_display = ['material', 'quantity','site__name', 'quantity_issued', 'quantity_utilised']
  list_filter = ['material', 'site']
  list_per_page = 8
  def qty_nil(self, obj):
    return not obj.quantity > 0
  #readonly_fields = ['qty_nil']
admin.site.register(Project)
class SiteAdmin(admin.ModelAdmin):
  list_display = ['name', 'status']
admin.site.register(Site, SiteAdmin)
admin.site.register(Unit)
admin.site.register(Material)
admin.site.register(WorkItem, WorkItemAdmin)
admin.site.register(ItemRate, ItemRateAdmin)
#admin.site.register(ItemRateGroup, ItemRateGroupAdmin)
admin.site.register(WorkGroup, WorkGroupAdmin)
admin.site.register(Package, PackageAdmin)
#admin.site.register(PackageWorkGroup, PackageWorkGroupAdmin)
admin.site.register(Party)
admin.site.register(MaterialBOQ, MaterialBOQAdmin)
#admin.site.register(MaterialIssued, MaterialIssuedAdmin)
#admin.site.register(MaterialUtilised)
admin.site.register(MaterialExisting)
admin.site.register(MaterialDismantled)
#admin.site.register(Estimation, EstimationAdmin)
class WorkProgressAdmin(admin.ModelAdmin):
  list_display =['date', 'site__name','work_item__name','quantity','target_quantity', 'status']
  list_filter= ['site__name','work_item__name']
  readonly_fields = ['target_quantity']
admin.site.register(WorkProgress, WorkProgressAdmin)
class CashFlowAdmin(admin.ModelAdmin):
  list_display = ['date', 'item','amount', 'payer', 'payee', 'virtual', 'include']
  list_filter =['payer', 'payee', 'package', 'virtual']
admin.site.register(CashFlow, CashFlowAdmin)
admin.site.register(Person)
#admin.site.register()