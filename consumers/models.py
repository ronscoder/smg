from django.db import models
#from django.contrib.gis.db import models
from django.utils import timezone
#from anchor.models.fields import SingleAttachmentField
from location_field.models.plain import PlainLocationField
from taggit.managers import TaggableManager
class RechargeHistory(models.Model):
  connection_id = models.CharField(max_length=20)
  meter_no = models.CharField(max_length=10)
  meter_make = models.IntegerField()
  consumer_name= models.CharField(max_length=50)
  amount = models.FloatField()
  paid_on = models.DateField()
  pay_mode = models.CharField(max_length=20, null=True, blank=True)
class ConsumerGroup(models.Model):
  #id = models.Auto(primary_key=True)
  #group_id = models.IntegerField(default=0)
  consumer = models.ManyToManyField('Consumer', blank=True)
  group_name = models.CharField(max_length=30)
  #group_activated = models.BooleanField(default=False)
  
  def __str__(self):
    return f'{self.id}: {self.group_name}'
class CashFlow(models.Model):
  txn_date = models.DateField(default=timezone.now)
  txn_text = models.CharField(max_length=100, blank=True, null=True)
  amount = models.FloatField()
  debit= models.BooleanField(default=False)
  revenue = models.BooleanField(default=False)
  txn_ref = models.CharField(max_length=50, blank=True, null=True)
  internal = models.BooleanField(default=False)
  def __str__(self):
    return f'{"-" if self.debit else "+"}{self.amount} | {self.txn_text}'
  def save(self, *args, **kwargs):
    if(self.revenue==True and (self.txn_ref==None or self.txn_ref=="")):
      return
    super().save(*args, **kwargs)
  raid = models.ForeignKey('Raid', on_delete=models.CASCADE, null=True, blank=True)
  chistory = models.ForeignKey('ConsumerHistory', on_delete=models.CASCADE, null=True, blank=True)
class LoadSurvey(models.Model):
  appliance = models.CharField(max_length=30, null=True, blank=True)
  kw = models.FloatField()
  day_hours = models.IntegerField()
  #loading_group = models.CharField(max_length=100, blank=True, null=True)
  remark = models.CharField(max_length=50, blank=True, null=True)
  def day_units(self):
    if(self._state.adding):
      return 0
    return self.kw * self.day_hours
  def __str__(self):
    return f'{self.appliance} ({self.kw}kW-{self.day_hours} hrs): {self.day_units()} kWh'
categories = [
  ('Domestic', 'Domestic'),
  ('Commercial','Commercial'),
  ('Small Industry','Small Industry'),
  ('Public Lighting','Public Lighting')
  ]
  
class Tariff(models.Model):
  billing_class = models.CharField(default='LT', choices=(('LT','LT'),('HT', 'HT')))
  category = models.CharField(default='Domestic', choices = categories)
  year = models.IntegerField(default=2025)
  demand_charge = models.FloatField()
  rate1 = models.FloatField()
  rate2 = models.FloatField()
  rate3 = models.FloatField()
  load_factor = models.FloatField()
  demand_factor = models.FloatField(default=0.45)
  late_surcharge = models.FloatField(default=2)
  def __str__(self):
    return f'{self.billing_class} {self.category} {self.year}'
    
from dateutil.rrule import rrule, MONTHLY
import calendar
from dateutil.relativedelta import relativedelta
class EnergyAssessment(models.Model):
  title = models.CharField(max_length=50, null=True, blank=True)
  load_surveys = models.ManyToManyField('LoadSurvey', blank=True)
  tariff = models.ForeignKey(Tariff, on_delete=models.SET_NULL, null=True)
  period_from = models.DateField()
  period_to = models.DateField()
  mf_full = models.BooleanField(default=False)
  #no_months = 0
  def daily_units(self):
    return round(sum([x.day_units() for x in self.load_surveys.all()])*(1 if self.mf_full else (self.tariff.load_factor*self.tariff.demand_factor)),3)
  def energy_charge(self):
    if(self._state.adding):
      return 0
    energy_charge=0
    for dt in rrule(MONTHLY, dtstart=self.period_from, until=self.period_to):
      #no_months+=1
      if(dt.month == self.period_from.month):
        d1 = self.period_from.day
      else: 
        d1 = 1
      if(dt.month == self.period_to.month):
        d2 = self.period_to.day
      else:
        _, d2 = calendar.monthrange(dt.year, dt.month)
      days = d2-d1+1
      month_unit = days * self.daily_units()
      if(month_unit>100):
        b1 = 100
      else:
        b1 = month_unit
      b3=0
      if(month_unit>200):
        b2 = 100
        b3=month_unit-200
      else:
        if(month_unit>100):
          b2=month_unit-100
        else:
          b2 = 0
      print(f'({self.tariff.rate1}*{b1} + {self.tariff.rate2}*{b2} + {self.tariff.rate3}*{b3})*{self.tariff.load_factor}*{self.tariff.demand_factor}')
      energy_charge += (self.tariff.rate1*b1 + self.tariff.rate2*b2 + self.tariff.rate3*b3)
    return round(energy_charge,2)
      
    
  #rate = models.FloatField(default=5.1)
  #demand_factor = models.FloatField(default= 0.45 )
  #load_factor = models.FloatField(default=0.4)
  #fixed_charge = models.FloatField(default=65)
  penalty_factor = models.FloatField(default=3.0)
  def day_counts(self):
    if(self._state.adding):
      return 0
    return (self.period_to - self.period_from).days + 1
  def total_kw(self):
    if(self._state.adding):
      return 0
    return sum([x.kw for x in self.load_surveys.all()])
  
  def total_units(self):
    if(self._state.adding):
      return 0
    print(f'{self.day_counts()} * {self.daily_units()}')
    return round(self.day_counts() * self.daily_units(),1)
  '''
  def energy_charge(self):
    if(self._state.adding):
      return 0
    return round(self.total_units() * self.rate)
  '''
  def no_months(self):
    if(self._state.adding):
      return 0
    delta = relativedelta(self.period_to, self.period_from)
    total_months = delta.years * 12 + delta.months + 1
    return total_months
    
  def demand_charge(self):
    if(self._state.adding):
      return 0
    delta = relativedelta(self.period_to, self.period_to)
    total_months = delta.years * 12 + delta.months + 1
    return total_months*self.total_kw()*self.tariff.demand_charge
    
  def penalised_energy_charge(self):
    if(self._state.adding):
      return 0
    return round(self.energy_charge() * self.penalty_factor)
  def __str__(self):
    return f'{self.title}: {self.total_kw()}kW, {self.no_months()} months,energy charge: {self.energy_charge()}x3 = ₹{self.penalised_energy_charge()}, {self.demand_charge()}'
class Consumer(models.Model):
    consumer_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    contact_nos = models.CharField(max_length=30,null=True,blank=True)
    meter_no = models.CharField(max_length=20,null=True,blank=True)
    connection_id = models.CharField(max_length=20,null=True,blank=True)
    phase = models.CharField(max_length=10, choices=[('SINGLE', 'SINGLE'), ('THREE', 'THREE')]) 
    current_outstanding = models.DecimalField(default=0, max_digits=15, decimal_places=2)
    bill_upto = models.DateField(null=True, blank=True)
    #consumer_type = models.CharField( max_length=30, null=True, blank=True)
    
    tags = TaggableManager(blank=True)
    #latlong = models.CharField(blank=True, null=True)
    location = models.CharField(default='24.823,93.957', blank=True, null=True)
    connection_type = models.CharField(max_length=30, blank=True, null=True)
    #solar=models.BooleanField(default=False)
    infos = models.ManyToManyField('ConsumerInfo', blank=True)
    def __str__(self):
        return f'{self.consumer_id}, {self.name}, {self.address}, {self.meter_no}'
class ConsumerExtension(models.Model):
  consumer = models.OneToOneField(Consumer, on_delete= models.CASCADE)
  purpose = models.CharField(max_length=30, null=True, blank=True)
class ConsumerInfo(models.Model):
  consumers = models.ManyToManyField(Consumer, blank=True)
  field = models.CharField(max_length=20)
  value = models.CharField(max_length=30)
  def __str__(self):
    return f'{self.field}: {self.value}'
class SolarConsumer(models.Model):
  consumer = models.OneToOneField(Consumer, on_delete= models.SET_NULL, null=True)
  capacity_kw = models.FloatField()
  net_meter_no = models.CharField(max_length=30)
  start_date = models.DateField()
  remark = models.CharField(max_length=100, blank=True, null=True)
  def __str__(self):
    return f'{self.consumer}'
class ConsumerHistory(models.Model):
    consumer = models.ForeignKey(Consumer, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    raid = models.BooleanField(default=False)
    internal = models.BooleanField(default=False)
    remark = models.CharField(max_length=500, null=True, blank=True)
    theft = models.BooleanField(default=False)
    unused = models.BooleanField(default=False)
    defaulter = models.BooleanField(default=False)
    meter_defective = models.BooleanField(default=False)
    mark = models.BooleanField(default=False)
    meter_replaced = models.BooleanField(default=False)
    disconnected = models.BooleanField(default=False)
    summoned = models.BooleanField(default=False)
    resolution = models.CharField(max_length=300, blank=True, null= True)
    tags = TaggableManager(blank=True)
    def __str__(self):
        return f'{self.consumer} — {self.remark}'
    status = models.CharField(default="", choices=[('PENDING', 'PENDING'), ('HOLD','HOLD'), ("COMPLETED","COMPLETED"), ("SKIPPED","SKIPPED"), ("","")], blank=True)
    status_justification = models.CharField(null=True, blank=True)
    energy_assessments = models.ManyToManyField(EnergyAssessment, blank=True)
    #cash_flows = models.ManyToManyField(CashFlow, blank=True)
class Staff(models.Model):
  name = models.CharField(max_length=100)
  is_staff = models.BooleanField(default=True)
  contact_nos= models.CharField(max_length=50, null=True, blank=True)
  lead = models.BooleanField(default=False)
  def __str__(self):
    return self.name
class StaffAssignment(models.Model):
  assignment = models.CharField(max_length=100)
  staffs = models.ManyToManyField(Staff)
class UnauthConsumer(models.Model):
    report_date = models.DateField(default=timezone.now)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    contact_nos= models.CharField(max_length=30, null=True, blank=True)
    purpose = models.CharField(max_length=100, null=True, blank=True)
    loads = models.ManyToManyField(LoadSurvey, blank=True)
    connected_by = models.ManyToManyField(Staff, blank=True)
    remark = models.CharField(max_length=100, null=True, blank=True)
    tags = TaggableManager(blank=True)
    followup = models.CharField(max_length=100, null=True, blank=True)
    staffs_assignments = models.ManyToManyField(StaffAssignment, blank=True)
    resolution = models.CharField(max_length=100, null=True, blank=True)
    is_closed = models.BooleanField(default=False)
    
    energy_assessments = models.ManyToManyField(EnergyAssessment, blank=True)
    cash_flows = models.ManyToManyField(CashFlow, blank=True)
    def __str__(self):
        return f'{self.name}, {self.address}'
class Raid(models.Model):
    date = models.DateField(default=timezone.now)
    consumer = models.ForeignKey(Consumer, on_delete=models.SET_NULL, null=True, blank=True)
    unauth = models.ForeignKey(UnauthConsumer, on_delete=models.SET_NULL, null=True, blank=True)
    observation = models.CharField(max_length=200, null=True, blank=True)
    ok = models.BooleanField(default=False)
    theft = models.BooleanField(default=False)
    unauthorised = models.BooleanField(default=False)
    underbilled = models.BooleanField(default=False)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    tags = TaggableManager(blank=True)
    unused = models.BooleanField(default=False)
    info = models.CharField(max_length=200, null=True, blank=True)
    is_disconnected = models.BooleanField(default=False)
    penalty_paid = models.BooleanField(default=False)
    action = models.CharField(max_length=200, null=True, blank=True)
    is_closed = models.BooleanField(default=False)
    skip = models.BooleanField(default=False)
    energy_assessments = models.ManyToManyField(EnergyAssessment, blank=True)
    staffs_assignments = models.ForeignKey(StaffAssignment, on_delete=models.SET_NULL, null=True, blank=True)
    #cash_flows = models.ManyToManyField(CashFlow, blank=True)
    def __str__(self):
        return f'{self.unauth}' if self.consumer==None else f'{self.consumer}, {self.theft}, {self.is_disconnected}'