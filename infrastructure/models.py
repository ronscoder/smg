from django.db import models

class Feeder(models.Model):
  feeder_id = models.CharField(max_length=20)
  name = models.CharField(max_length=100)
  substation = models.CharField(max_length=50)
  def __str__(self):
    return f'{self.feeder_id}, {self.name}, {self.substation}'
class DTR(models.Model):
  dtr_id = models.CharField(max_length=20)
  feeder = models.ForeignKey(Feeder, on_delete=models.CASCADE)
  name = models.CharField(max_length=100)
  capacity_kva = models.IntegerField()
  location = models.CharField(max_length=12, blank=True, null=True)
  def __str__(self):
    return ", ".join([self.name, str(self.capacity_kva), 'KVA', str(self.feeder)])
  