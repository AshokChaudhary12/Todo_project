from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User



# Create your models here.

class Todo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, blank=False)
    description = models.TextField(max_length=100, blank=False)
    start_date = models.DateField()
    end_date = models.DateField()
    completed = models.BooleanField(default=False)
    # created_at = models.DateTimeField(default=datetime.datetime.now)  
    created_at = models.DateTimeField(default=timezone.now) 
        
    def __str__(self):
        return self.title