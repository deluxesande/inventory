from django.db import models


class TrackingModel(models.Model):

    created_at = models.DateTimeField(auto_now=True)
    updates_at = models.DateTimeField(auto_now_add=True)

    #this sets it as an abstract class, 
    # meaning it is only to be inherited from
    class Meta:
        abstract = True
        ordering = ('-created_at',)