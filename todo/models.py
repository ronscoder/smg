from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
# Create your models here.
class Post(models.Model):
    content = models.CharField(max_length=255,null=False)
    
    def __str__(self):
    	return self.content
    	