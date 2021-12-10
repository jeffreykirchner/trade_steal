'''
avatars
'''
import uuid
from django.db import models

#gloabal parameters for site
class Avatar(models.Model):
    '''
    avatars
    '''

    label =  models.CharField(max_length = 200, default="Avatar", unique=True)           #primary contact for subjects
    file_name = models.CharField(max_length = 200, default="abc.jpg")       #name of file located in /static/avatars

    timestamp = models.DateTimeField(auto_now_add=True)
    updated= models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.label

    class Meta:
        verbose_name = 'Avatar'
        verbose_name_plural = 'Avatars'
        ordering = ['label']

    def json(self):
        '''
        model json object
        '''
        return{
            "id" : self.id,

            "label" : self.label,
            "file_name" : self.file_name,
        }
        