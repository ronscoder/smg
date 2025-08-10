from django.db import models
from django.utils import timezone
STATUS = [('DONE','DONE'),('PENDING','PENDING'), ('ONGOING','ONGOING'),('FAILED','FAILED'),('RESOLVED', 'RESOLVED'), ('POSTPONED','POSTPONED'),('--','--')]
class Progress(models.Model):
  date = models.DateField(default=timezone.now)
  text = models.CharField(max_length=100)
  #status = models.CharField()
  status = models.CharField(max_length=50, choices=STATUS, default='--')
  status_text = models.CharField(max_length=200, null=True, blank=True)
  def __str__(self):
    return " | ".join([str(self.date),self.status, self.text])

#from consumers.models import ConsumerWork   
class Work(models.Model):
  date= models.DateField(default=timezone.now)
  subject = models.TextField()
  info = models.TextField(null=True, blank=True)
  deadline = models.DateField(blank=True, null=True)
  priority = models.CharField(max_length=20, default="LOW", choices= [(x,x) for x in ['LOW', 'MEDIUM', 'HIGH']])
  status = models.CharField(max_length=50, choices=STATUS, default='PENDING')
  def __str__(self):
    return " | ".join([self.priority, self.status, self.subject])
class WorkProgress(models.Model):
  work = models.ForeignKey(Work, on_delete=models.CASCADE)
  progress = models.ForeignKey(Progress, on_delete=models.CASCADE)
  def __str__(self):
    return "•".join([str(self.work)])
  
  