from django.db import models
from authentication.models import User
from helpers.models import TrackingModel
from django.conf import settings

class MainCategory(TrackingModel):
    name = models.CharField(max_length=5000)

    def __str__(self):
        return self.name

class Category(TrackingModel):
    sub_category = models.CharField(max_length=5000)
    main_category = models.ForeignKey('MainCategory', on_delete=models.CASCADE)

    def __str__(self):
        return self.sub_category

class Reports(TrackingModel):
    date = models.DateTimeField(auto_now_add=True, null=True)
    description = models.CharField(max_length=200, null=True)
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE)
    category = models.ManyToManyField(MainCategory)
    receipts = models.FloatField(max_length=200, null=True)
    payments = models.FloatField(max_length=200, null=True)
    for_edit = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)  # New field


    def __str__(self):
        return f"Report on {self.date}"
    
class Feedback(models.Model):
    report = models.ForeignKey(Reports, on_delete=models.CASCADE, related_name='feedbacks')
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reported_feedbacks')
    directed_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='directed_feedbacks')
    content = models.TextField()
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.reporter.username} on {self.report}"