from django.contrib import admin
from .models import Package

class SitePackagesFilter(admin.SimpleListFilter):
  title = 'Site Packages'
  parameter_name = 'site_packages'
  def lookups(self, request, model_admin):
    packages = Package.objects.all()
    return [(x.pk, x.name) for x in packages]

  def queryset(self, request, queryset):
    package_pk = self.value()
    package = Package.objects.get(pk=package_pk)
    sites = package.sites.all()
    return sites