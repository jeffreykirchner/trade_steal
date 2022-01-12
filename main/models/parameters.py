'''
site parameters
'''
import uuid
from django.db import models

#gloabal parameters for site
class Parameters(models.Model):
    '''
    site parameters
    '''

    contact_email =  models.CharField(max_length = 1000, default="JohnSmith@abc.edu")       #primary contact for subjects
    experiment_time_zone = models.CharField(max_length = 1000, default="US/Pacific")        #time zone the experiment is in

    site_url = models.CharField(max_length = 200, default="http://localhost:8000")         #site URL used for display in emails

    avatar_sprite_sheet = models.CharField(max_length = 200, default="avatars.json")          #sprite sheet with avatar images
    graph_sprite_sheet = models.CharField(max_length = 200, default="sprite_sheet.json")      #site sheet with graph images

    timestamp = models.DateTimeField(auto_now_add=True)
    updated= models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Site Parameters"

    class Meta:
        verbose_name = 'Parameters'
        verbose_name_plural = 'Parameters'

    def json(self):
        '''
        model json object
        '''
        return{
            "id" : self.id
        }
        