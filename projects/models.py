from django.db import models
from django.db.models import Q
class Project(models.Model):
  name = models.CharField(max_length=30)
  description = models.TextField(blank=True, null=True)
  def __str__(self):
    return self.name
  
class Unit(models.Model):
  short = models.CharField(max_length=5)
  full = models.CharField(max_length=15, null=True, blank=True)
  def __str__(self):
    return self.short
  
class Material(models.Model):
  name = models.CharField(max_length=50)
  specs = models.TextField(null=True, blank=True)
  unit = models.ForeignKey(Unit, on_delete=models.CASCADE, null=True)
  def __str__(self):
    return self.name
  
class Site(models.Model):
  name = models.CharField(max_length=100)
  status = models.CharField(max_length=100)
  def __str__(self):
    return f'{self.name}'
  
class WorkItem(models.Model):
  name = models.CharField(max_length=100)
  description = models.TextField(null=True, blank=True)
  unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
  #TODO add material requirement per unit
  ref_material = models.ForeignKey('Material', on_delete=models.CASCADE, null=True)
  index = models.BooleanField(default=False)
  def site_quantity(self):
    matboqs = MaterialBOQ.objects.filter(material=self.ref_material)
    return ", ".join([f'{x.site.name}: {x.quantity}' for x in matboqs])
  def __str__(self):
    return self.name
class Party(models.Model):
  name = models.CharField(max_length=100)
  role = models.CharField(max_length=100)
  def __str__(self):
    return self.name
class ItemRate(models.Model):
  party = models.ForeignKey(Party, on_delete=models.SET_NULL, null=True)
  description = models.TextField(blank=True)
  work_item = models.ForeignKey(WorkItem, on_delete=models.CASCADE, null=True)
  rate = models.FloatField()
  settled = models.BooleanField(default=False)
  def __str__(self):
    return "|".join([self.party.name, self.work_item.name])

class Package(models.Model):
  project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True)
  name = models.CharField(max_length=50)
  sites = models.ManyToManyField(Site)
  def __str__(self):
    if(not self._state.adding):
      return ": ".join([str(self.id),self.name])
      #*[x.name for x in self.sites.all()]])
class MaterialBOQ(models.Model):
  site = models.ForeignKey(Site, on_delete=models.CASCADE)
  material = models.ForeignKey(Material, on_delete=models.CASCADE)
  quantity = models.FloatField()
  quantity_issued = models.FloatField(default=0)
  quantity_utilised = models.FloatField(default=0)

  def __str__(self):
    return self.material.name
class MaterialExisting(models.Model):
  site = models.ForeignKey(Site, on_delete=models.CASCADE)
  material = models.ForeignKey(Material, on_delete=models.CASCADE)
  quantity = models.FloatField()
class MaterialDismantled(models.Model):
  site = models.ForeignKey(Site, on_delete=models.CASCADE)
  material = models.ForeignKey(Material, on_delete=models.CASCADE)
  quantity = models.FloatField()

from django.utils import timezone
class WorkProgress(models.Model):
  date = models.DateField(default=timezone.now)
  site = models.ForeignKey(Site, on_delete=models.CASCADE, null=True, verbose_name='site')
  work_item = models.ForeignKey(WorkItem, on_delete=models.CASCADE, null=True)
  #work_executed = models.ForeignKey(WorkExecuted, on_delete=models.SET_NULL, null=True)
  quantity = models.FloatField(default=0)
  status = models.CharField(max_length=20, null=True, blank=True)
  remark = models.CharField(max_length= 200, null=True, blank=True)
  class Meta:
    ordering = ['-date']
  def target_quantity(self):
    if(self._state.adding):
      return 0
    boq = MaterialBOQ.objects.get(site=self.site, material=self.work_item.ref_material)
    return str(boq.quantity)
  def __str__(self):
    return "|".join([str(self.date), str(self.work_item), str(self.quantity)])
  
class Person(models.Model):
  name = models.CharField(max_length=100)
  party = models.ForeignKey(Party, on_delete=models.SET_NULL, null=True, blank=True)
  def __str__(self):
    return f'{self.name}, {self.party}'
    
class CashFlow(models.Model):
  package = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True)
  date = models.DateField(default=timezone.now)
  item = models.CharField(max_length=100)
  amount = models.FloatField()
  payer = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, related_name='payer')
  payee = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True, related_name='payee')
  virtual = models.BooleanField(default=False)
  include = models.BooleanField(default=False)

class WorkGroup(models.Model):
  package = models.ForeignKey('Package', on_delete=models.CASCADE, null=True)
  party = models.ForeignKey(Party, on_delete=models.SET_NULL, null=True)
  def total_lt_poles(self):
    if(self._state.adding):
      return "--"
    sites = self.package.sites.all()
    mat_pole_id = 1
    return sum([x.quantity for x in MaterialBOQ.objects.filter(material__id=1, site__in=sites)])
  def expended(self):
    if(self._state.adding):
      return 0
    payers = Person.objects.filter(party=self.party)
    cfs = CashFlow.objects.filter(payer__in=payers,package=self.package).exclude(virtual=True, include=False)
    amount = sum([x.amount for x in cfs])
    return amount
  def estimate(self):
    if(self._state.adding):
      return 0
    items = ItemRate.objects.filter(party=self.party)
    sites = self.package.sites.all()
    amount =0
    for site in sites:
      for item in items:
        rate = item.rate
        print(item, rate)
        work_item = item.work_item
        ref_material = work_item.ref_material
        try:
          boq = MaterialBOQ.objects.get(site=site, material=ref_material)
          qty = boq.quantity
        except Exception as ex:
          qty = 0
        #print(boq, qty)
        amount += qty*rate
        #print('amount', amount)
    return round(amount)
  def margin(self):
    if(self._state.adding):
      return 0
    return (self.estimate() - self.expended()) or "--" 