from django.db import models
#from django.contrib.gis.db import models
from django.utils import timezone
#from anchor.models.fields import SingleAttachmentField
from location_field.models.plain import PlainLocationField
from taggit.managers import TaggableManager

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
    location = PlainLocationField(based_fields=["city"], zoom=15, default='24.823044419753995,93.95751714635482', blank=True, null=True)
    def __str__(self):
        return f'{self.name}, {self.address}'


class ConsumerHistory(models.Model):
    consumer = models.ForeignKey(Consumer, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    remark = models.TextField(max_length=500)
    tags = TaggableManager(blank=True)
    def __str__(self):
        return f'{self.remark}'
    status = models.CharField(default="", choices=[('PENDING', 'PENDING'), ('HOLD','HOLD'), ("COMPLETED","COMPLETED"), ("","")], blank=True)
    status_justification = models.TextField(null=True, blank=True)

class UnauthConsumer(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    contact_nos= models.CharField(max_length=30, null=True, blank=True)
    remark = models.CharField(max_length=100, null=True, blank=True)
    tags = TaggableManager(blank=True)
    def __str__(self):
        return f'{self.name}, {self.address}'

class Raid(models.Model):
    date = models.DateField(default=timezone.now)
    consumer = models.ForeignKey(Consumer, on_delete=models.SET_NULL, null=True, blank=True)
    unauth = models.ForeignKey(UnauthConsumer, on_delete=models.SET_NULL, null=True, blank=True)
    observation = models.TextField(max_length=200, null=True, blank=True)
    theft = models.BooleanField(default=False)
    unused = models.BooleanField(default=False)
#    image = SingleAttachmentField()
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    tags = TaggableManager(blank=True)
    info = models.TextField(max_length=200, null=True, blank=True)
    theft_duration_months = models.FloatField("Theft duration in months", null=True, blank=True)
    penalty_amount = models.FloatField(null=True, blank=True)
    action = models.TextField(max_length=200, null=True, blank=True)
    is_disconnected = models.BooleanField(default=False)
    amount_paid = models.FloatField(null=True, blank=True)
    pay_ref = models.CharField(max_length=20, null=True, blank=True)
    is_closed = models.BooleanField(default=False)
    skip = models.BooleanField(default=False)
    def __str__(self):
        return f'{self.unauth}' if self.consumer==None else f'{self.consumer}'
