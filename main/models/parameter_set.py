'''
sessions parameters
'''
import logging

from django.db import models
from django.db.utils import IntegrityError

import main

#experiment session parameters
class ParameterSet(models.Model):
    '''
    session parameters
    '''

    timestamp = models.DateTimeField(auto_now_add= True)
    updated= models.DateTimeField(auto_now= True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Study Parameter Set'
        verbose_name_plural = 'Study Parameter Sets'

    def json(self):
        '''
        return json object of model
        '''
        return{
            "id" : self.id,
        }
