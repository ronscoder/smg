from django.db import models

# Create your models here.
class Post(models.Model):
    content = models.CharField(max_length=255,null=False)
    
    def __str__(self):
    	return self.content