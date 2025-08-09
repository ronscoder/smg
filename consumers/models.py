from django.db import models
#from django.contrib.gis.db import models
from django.utils import timezone
#from anchor.models.fields import SingleAttachmentField
from location_field.models.plain import PlainLocationField
from taggit.managers import TaggableManager
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from dateutil.rrule import rrule, MONTHLY
import calendar
from dateutil.relativedelta import relativedelta

class State(models.Model):
  name = models.CharField(max_length=20)
  text = models.CharField(max_length=50, blank=True, null=True)
  number = models.IntegerField(null=True, blank=True)
  decimal = models.FloatField(null=True, blank=True)
  boolean = models.BooleanField(null=True, blank=True)
  def __str__(self):
    return f'{self.pk} {self.name}'
class RechargeHistory(models.Model):
  connection_id = models.CharField(max_length=20)
  meter_no = models.CharField(max_length=10)
  meter_make = models.IntegerField()
  consumer_name= models.CharField(max_length=50)
  amount = models.FloatField()
  paid_on = models.DateField()
  pay_mode = models.CharField(max_length=20, null=True, blank=True)
class ConsumerGroup(models.Model):
  group_code = models.CharField(max_length=30, unique=True)
  group_name = models.CharField(max_length=50)
  description = models.TextField(blank=True, null=True)
  status = models.CharField(max_length=50, blank=True, null=True)
  def __str__(self):
    return f'{self.id}: {self.group_code} {self.group_name}'
    
class ConsumerGrouping(models.Model):
  group = models.ForeignKey(ConsumerGroup, on_delete=models.CASCADE)
  consumer = models.ForeignKey('Consumer', on_delete=models.CASCADE)
  remark = models.CharField(max_length=100, null=True, blank=True)
  def __str__(self):
    return ":".join([str(self.group), str(self.consumer)])
  
class CashFlow(models.Model):
  txn_date = models.DateField(default=timezone.now)
  txn_text = models.CharField(max_length=100, blank=True, null=True)
  amount = models.FloatField()
  internal = models.BooleanField(default=False)
  debit= models.BooleanField(default=False)
  revenue = models.BooleanField(default=False)
  txn_ref = models.CharField(max_length=50, blank=True, null=True)
  def __str__(self):
    return f'{"-" if (self.debit or self.revenue) else "+"}{self.amount}|{self.txn_date}|{self.txn_text}'
  def save(self, *args, **kwargs):
    if(self.revenue==True and (self.txn_ref==None or self.txn_ref=="")):
      return
    super().save(*args, **kwargs)

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
  def no_months(self):
    if(self._state.adding):
      return 0
    delta = relativedelta(self.period_to, self.period_from)
    total_months = delta.years * 12 + delta.months + 1
    return total_months
    
  def demand_charge(self):
    if(self._state.adding):
      return 0
    return self.no_months()*self.total_kw()*self.tariff.demand_charge
    
  def penalised_energy_charge(self):
    if(self._state.adding):
      return 0
    return round(self.energy_charge() * self.penalty_factor)
  def __str__(self):
    return f'{self.title}: energy charge: {self.energy_charge()}x3 = ₹{self.penalised_energy_charge()}, {self.demand_charge()}, {self.total_kw()}kW, {self.no_months()} months'
class Consumer(models.Model):
    consumer_id = models.IntegerField(primary_key=True)
    subdivision = models.CharField(max_length=20, default="smg")
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=200)
    contact_nos = models.CharField(max_length=30,null=True,blank=True)
    meter_no = models.CharField(max_length=20,null=True,blank=True)
    connection_id = models.CharField(max_length=20,null=True,blank=True)
    phase = models.CharField(max_length=10, choices=[('SINGLE', 'SINGLE'), ('THREE', 'THREE')]) 
    current_outstanding = models.DecimalField(default=0, max_digits=15, decimal_places=2)
    bill_upto = models.DateField(null=True, blank=True)
    connection_status = models.CharField(default='ACTIVE')
    tags = TaggableManager(blank=True)
    connection_type = models.CharField(max_length=30, blank=True, null=True)
    load_kw = models.IntegerField(blank=True, null=True)
    location = models.CharField(default='24.823,93.957', blank=True, null=True)
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
  capacity_kw = models.FloatField(blank=True, null=True)
  net_meter_no = models.CharField(max_length=30, blank=True, null=True)
  start_date = models.DateField(blank=True, null=True)
  remark = models.CharField(max_length=100, blank=True, null=True)
  def __str__(self):
    return f'{self.consumer}'
class ConsumerHistory(models.Model):
  class Meta:
    ordering = ['-date']
  consumer = models.ForeignKey(Consumer, on_delete=models.CASCADE)
  date = models.DateField(default=timezone.now)
  remark = models.TextField(null=True, blank=True)
  mark = models.BooleanField(default=False)
  tags = TaggableManager(blank=True)
  def __str__(self):
      return f'{self.consumer} — {self.remark}'
  energy_assessments = models.ManyToManyField(EnergyAssessment, blank=True)
  cash_flows = models.ManyToManyField(CashFlow, blank=True)
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
    raid_groups = models.ManyToManyField('RaidGroup', blank=True, related_name='raid_groups', through='RaidGrouping')
    date = models.DateField(default=timezone.now)
    consumer = models.ForeignKey(Consumer, on_delete=models.SET_NULL, null=True, blank=True)
    unauth = models.ForeignKey(UnauthConsumer, on_delete=models.SET_NULL, null=True, blank=True)
    info = models.TextField(null=True, blank=True)
    observations = models.ManyToManyField('RaidObservation', blank=True)
    comment = models.TextField(null=True, blank=True)
    action = models.CharField(max_length=200, null=True, blank=True)
    remark = models.TextField(null=True, blank=True)
    is_disconnected = models.BooleanField(default=False)
    skip = models.BooleanField(default=False)
    energy_assessments = models.ManyToManyField(EnergyAssessment, blank=True)
    staffs_assignments = models.ForeignKey(StaffAssignment, on_delete=models.SET_NULL, null=True, blank=True)
    staffs_engaged = models.ManyToManyField(Staff, blank=True)
    raid_groups = models.ManyToManyField('RaidGroup', through='RaidGrouping')
    def save(self, *args, **kwargs):
      super().save(*args, **kwargs)
    def __str__(self):
      obs = ", ".join([x.text for x in self.observations.all()])
      return f'{self.unauth}' if self.consumer==None else f'{self.consumer}, [{obs}], [{self.action}],{"disconnected" if self.is_disconnected else " "}'
class RaidCashFlow(models.Model):
  raid = models.ForeignKey(Raid, on_delete=models.SET_NULL, null=True)
  cash_flow = models.ForeignKey(CashFlow, on_delete=models.CASCADE)
class RaidObservation(models.Model):
  #raid = models.ForeignKey(Raid, on_delete= models.SET_NULL)
  text = models.CharField(max_length=30)
  theft = models.BooleanField(default=False)
  def __str__(self):
    return f'{self.id} {self.text}'
    
class TemporaryConnection(models.Model):
    report_date = models.DateField(default=timezone.now)
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    contact_nos= models.CharField(max_length=30, null=True, blank=True)
    purpose = models.CharField(max_length=100, null=True, blank=True)
    loads = models.ManyToManyField(LoadSurvey, blank=True)
    authorised_by = models.ForeignKey(Staff, on_delete=models.SET_NULL, null=True, related_name="authorised_by")
    connected_by = models.ManyToManyField(Staff, blank=True, related_name="connected_by")
    remark = models.CharField(max_length=100, null=True, blank=True)
   # tags = TaggableManager(blank=True)
    followup = models.CharField(max_length=100, null=True, blank=True)
    is_closed = models.BooleanField(default=False)
    energy_assessments = models.ManyToManyField(EnergyAssessment, blank=True)
    cash_flows = models.ManyToManyField(CashFlow, blank=True)
    def __str__(self):
        return f'{self.name}, {self.address}'

class Todo(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    content = models.TextField(max_length=255,null=False)
    status = models.CharField(max_length=10, default='PENDING', choices =[('PENDING','PENDING'),('DONE','DONE'),('HOLD','HOLD'),('SKIP','SKIP')])
    remark = models.TextField(max_length=200, blank=True, null=True)
class DefectiveMeter(models.Model):
  consumer = models.ForeignKey(Consumer, on_delete=models.SET_NULL, null=True)
  fetch = models.BooleanField(default=False)
  meter_no = models.CharField(max_length=10, null=True, blank=True)
  contact_nos = models.CharField(max_length=100, blank=True, null=True)
  record_date = models.DateField(default=timezone.now)
  picked_date = models.DateField(default=timezone.now, blank=True, null=True)
  picked_by = models.ManyToManyField(Staff, related_name='picked_by')
  reason = models.CharField(max_length=100)
  custody = models.ManyToManyField(Staff, related_name='custody')
  #custodyx = models.CharField(max_length=50, null=True, blank=True)
  balance = models.FloatField(default=0)
  postpaid = models.BooleanField(default=False)
  new_meter_no = models.CharField(max_length=10, blank=True, null=True)
  action_text = models.CharField(max_length=100, blank=True, null=True)
  action_date = models.DateField(blank=True, null=True)
  installed_by = models.ManyToManyField(Staff, related_name='installed_by', blank=True)
  action_date = models.DateField(blank=True, null=True)
  remark= models.CharField(max_length=100, blank=True, null=True)
  prioritized = models.BooleanField(default=False)
  is_resolved = models.BooleanField(default=False)
  progress = models.ForeignKey('DefectiveMeterProgress', on_delete=models.SET_NULL, null=True, blank=True)
  def __str__(self):
    return ", ".join([str(self.consumer)])
  def save(self, *args, **kwargs):
    if(self.fetch):
      self.meter_no = self.consumer.meter_no
    super().save(*args, **kwargs)
class DefectiveMeterProgress(models.Model):
  defective_meter = models.ForeignKey(DefectiveMeter, on_delete=models.CASCADE)
  progress = models.ForeignKey('Progress', on_delete=models.CASCADE, null=True)
class Progress(models.Model):
  date = models.DateField(default=timezone.now)
  text = models.CharField(max_length=200)
  status = models.CharField(max_length=50, choices=[('DONE','DONE'),('PENDING','PENDING'), ('ONGOING','ONGOING'),('FAILED','FAILED'),('--','--')], default='--')
  status_text = models.CharField(max_length=200, null=True, blank=True)
  def __str__(self):
    return " | ".join([str(self.date),self.status, self.text])
    
class Complaint(models.Model):
  consumer = models.ForeignKey(Consumer, on_delete=models.SET_NULL, null=True)
  date= models.DateField(default=timezone.now)
  complaint = models.TextField()
  action = models.TextField(blank=True, null=True)
  status = models.CharField(max_length=100, blank=True, null=True)
  is_resolved = models.BooleanField(default=False)
  remark = models.CharField(max_length=100, blank=True, null=True)
  #logs = models.ManyToManyField('Log', blank=True)
  def __str__(self):
    return ", ".join([str(self.consumer), self.complaint, str(self.is_resolved)])
class Log(models.Model):
  #awaiting = models.BooleanField(default=False)
  date = models.DateField(default=timezone.now)
  text1 = models.CharField(max_length=100)
  text2= models.CharField(max_length=100, blank=True, null=True)
  status = models.CharField(max_length=20, blank=True, null=True)
  def __str__(self):
    return ", ".join([self.text1, str(self.text2), str(self.date),])

class ComplaintLog(models.Model):
  complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE)
  log = models.ForeignKey(Log, on_delete=models.CASCADE)
  #awaiting = models.BooleanField(default=False)
  
class HistoryLog(models.Model):
  history = models.ForeignKey(ConsumerHistory, on_delete=models.CASCADE)
  log = models.ForeignKey(Log, on_delete=models.CASCADE)
class Work2(models.Model):
  date= models.DateField(default=timezone.now)
  subject = models.TextField()
  info = models.TextField(null=True, blank=True)
  deadline = models.DateField(blank=True, null=True)
  priority = models.CharField(max_length=20, default="LOW", choices= [(x,x) for x in ['LOW', 'MEDIUM', 'HIGH']])
  status = models.CharField(max_length=50, choices=[('DONE','DONE'),('PENDING','PENDING'),('ONGOING','ONGOING'), ('FAILED','FAILED')], default='PENDING')
  def __str__(self):
    return " | ".join([self.priority, self.status, self.subject])
class WorkProgress(models.Model):
  work = models.ForeignKey(Work2, on_delete=models.CASCADE)
  progress = models.ForeignKey(Progress, on_delete=models.CASCADE)
  def __str__(self):
    return "•".join([str(self.work)])
  
  
from office.models import Work

class ConsumerWork(models.Model):
  consumer=models.ForeignKey(Consumer, on_delete=models.CASCADE)
  work=models.ForeignKey(Work, on_delete=models.CASCADE)
  work2=models.ForeignKey(Work2, on_delete=models.CASCADE, null=True)
  def __str__(self):
    return "•".join([str(self.consumer), str(self.work)])
    
class RaidGroup(models.Model):
  date = models.DateField(default=timezone.now)
  name = models.CharField(max_length=50)
  description = models.TextField(blank=True)
  #raids = models.ManyToManyField(Raid, blank=True)
  selected = models.BooleanField(default=False)
  freezed = models.BooleanField(default=False)
  #def save(self, *args, **kwargs):
    
  def __str__(self):
    return ":".join([str(self.id), self.name])

class RaidGrouping(models.Model):
  raid = models.ForeignKey(Raid, on_delete=models.CASCADE, related_name='raidgroupings')
  group = models.ForeignKey(RaidGroup, on_delete=models.CASCADE)
  def __str__(self):
    return "—".join([self.group.name, self.raid.consumer.name, str(self.raid.consumer.consumer_id), str(self.raid.observations)])

class RaidProgress(models.Model):
  raid = models.ForeignKey(Raid, on_delete=models.CASCADE, related_name='raid_progress')
  progress = models.ForeignKey(Progress, on_delete=models.CASCADE)
  
class MultiConsumer(models.Model):
  #relationship_name = models.CharField(max_length=100)
  consumer = models.ForeignKey(Consumer, on_delete=models.SET_NULL, null=True)
  #consumers = models.ManyToManyField(Consumer, blank=True, related_name='close_consumers')
  consumer_b = models.ForeignKey(Consumer, on_delete=models.CASCADE, null=True, related_name='consumer_b')
  dup_is_b = models.BooleanField(default=False)
  duplication = models.BooleanField(default=False)
  mark_both = models.BooleanField(default=False)
  revise_bill = models.BooleanField(default=False)
  verified = models.BooleanField('Different connections',default= False)
  remark = models.CharField(max_length=100, null=True, blank=True)
  status = models.CharField(max_length=50, null=True, blank=True)
  mark = models.BooleanField(default=False)
  def __str__(self):
    return str(self.consumer)

class ConsumerNA(models.Model):
  consumer_id = models.IntegerField(primary_key=True)
  name = models.CharField(max_length=50, null=True, blank=True)
  address = models.CharField(max_length=100, null=True, blank=True)
  contacts = models.CharField(max_length=50, null=True, blank=True)
  subdivision = models.CharField(max_length=50, null=True, blank=True)
  info = models.TextField(null=True, blank=True)
  remark = models.TextField(null=True, blank=True)
  tags = TaggableManager(blank=True)

class DefectiveMeterCashFlow(models.Model):
  defective_meter = models.OneToOneField(DefectiveMeter, on_delete=models.CASCADE)
  cash_flows = models.ForeignKey(CashFlow, on_delete=models.CASCADE)