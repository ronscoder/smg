from django.db import models
#from django.contrib.gis.db import models
from django.utils import timezone
#from anchor.models.fields import SingleAttachmentField
from location_field.models.plain import PlainLocationField
from taggit.managers import TaggableManager

class CashFlow(models.Model):
  txn_date = models.DateField(default=timezone.now)
  txn_text = models.CharField(max_length=100, blank=True, null=True)
  amount = models.FloatField()
  debit= models.BooleanField(default=False)
  txn_ref = models.CharField(max_length=50, blank=True, null=True)
  internal = models.BooleanField(default=False)
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
class EnergyAssessment(models.Model):
  title = models.CharField(max_length=50, null=True, blank=True)
  #load_surveys = models.ManyToManyField('LoadSurvey', through='LoadEnergyAssessmentInt')
  load_surveys = models.ManyToManyField('LoadSurvey', blank=True)
  #load_surveysx = models.ManyToManyField('LoadSurvey', through='LoadEnergyAssessmentInt')
  period_from = models.DateField()
  period_to = models.DateField()
  rate = models.FloatField(default=5.1)
  demand_factor = models.FloatField(default= 0.45 )
  load_factor = models.FloatField(default=0.4)
  fixed_charge = models.FloatField(default=65)
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
    return round(sum([x.day_units() for x in self.load_surveys.all()])*self.day_counts())
  def energy_charge(self):
    if(self._state.adding):
      return 0
    return round(self.total_units() * self.rate * self.load_factor * self.demand_factor)
  def demand_charge(self):
    if(self._state.adding):
      return 0
    return round(self.total_kw() * self.fixed_charge * self.day_counts() // 30.5)
  def penalised_energy_charge(self):
    if(self._state.adding):
      return 0
    return round(self.energy_charge() * self.penalty_factor)
  def __str__(self):
    return f'{self.title}: {self.total_kw()}kW, ₹{self.penalised_energy_charge()}'
'''   
class LoadEnergyAssessmentInt(models.Model):
  load_survey = models.ForeignKey(LoadSurvey, on_delete=models.CASCADE)
  energy_assessment = models.ForeignKey(EnergyAssessment, on_delete=models.CASCADE)
'''
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
    def __str__(self):
        return f'{self.name}, {self.address}'

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
    
    #amount_received = models.FloatField(default=0.0)
    #pay_ref = models.CharField(max_length=30, blank=True, null=True)
    resolution = models.CharField(max_length=300, blank=True, null= True)
    tags = TaggableManager(blank=True)
    def __str__(self):
        return f'{self.remark}'
    status = models.CharField(default="", choices=[('PENDING', 'PENDING'), ('HOLD','HOLD'), ("COMPLETED","COMPLETED"), ("SKIPPED","SKIPPED"), ("","")], blank=True)
    status_justification = models.CharField(null=True, blank=True)
    energy_assessments = models.ManyToManyField(EnergyAssessment, blank=True)
    cash_flow = models.ManyToManyField(CashFlow, blank=True)
class UnauthConsumer(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    contact_nos= models.CharField(max_length=30, null=True, blank=True)
    remark = models.CharField(max_length=100, null=True, blank=True)
    tags = TaggableManager(blank=True)
    def __str__(self):
        return f'{self.name}, {self.address}'
    energy_assessments = models.ManyToManyField(EnergyAssessment, blank=True)
    cash_flows = models.ManyToManyField(CashFlow, blank=True)

  
class Raid(models.Model):
    date = models.DateField(default=timezone.now)
    consumer = models.ForeignKey(Consumer, on_delete=models.SET_NULL, null=True, blank=True)
    unauth = models.ForeignKey(UnauthConsumer, on_delete=models.SET_NULL, null=True, blank=True)
    observation = models.TextField(max_length=200, null=True, blank=True)
    theft = models.BooleanField(default=False)
    #unused = models.BooleanField(default=False)
#    image = SingleAttachmentField()
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    tags = TaggableManager(blank=True)
    info = models.TextField(max_length=200, null=True, blank=True)
    #theft_duration_months = models.FloatField("Theft duration in months", null=True, blank=True)
    #penalty_amount = models.FloatField(null=True, blank=True)
    action = models.TextField(max_length=200, null=True, blank=True)
    is_disconnected = models.BooleanField(default=False)
    #amount_paid = models.FloatField(null=True, blank=True)
    #pay_ref = models.CharField(max_length=20, null=True, blank=True)
    is_closed = models.BooleanField(default=False)
    skip = models.BooleanField(default=False)
    energy_assessments = models.ManyToManyField(EnergyAssessment, blank=True)
    cash_flows = models.ManyToManyField(CashFlow)
    def __str__(self):
        return f'{self.unauth}' if self.consumer==None else f'{self.consumer}'

