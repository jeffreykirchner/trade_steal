'''
session player parameters 
'''

from django.db import models
from django.db.models import Q
from django.db.models import F

from main.models import ParameterSet
from main.models import Avatar

import main

class ParameterSetAvatar(models.Model):
    '''
    session player parameters 
    '''

    parameter_set = models.ForeignKey(ParameterSet, on_delete=models.CASCADE, related_name="parameter_set_avatars_a")
    avatar = models.ForeignKey(Avatar, on_delete=models.CASCADE, related_name="parameter_set_avatars_b", null=True, blank=True)
    
    grid_location_row = models.IntegerField(verbose_name='Grid Location Row', default=1)         #row location on choice grid
    grid_location_col = models.IntegerField(verbose_name='Rid Location Column', default=1)       #col location on choice grid

    timestamp = models.DateTimeField(auto_now_add= True)
    updated= models.DateTimeField(auto_now= True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Parameter Set Avatar'
        verbose_name_plural = 'Parameter Set Avatars'
        ordering = ['grid_location_row', 'grid_location_col']
        constraints = [
            models.UniqueConstraint(fields=['parameter_set', 
                                            'grid_location_row', 
                                            'grid_location_col'], name='unique_parameter_set_avatar'),
           
        ]


    def from_dict(self, source):
        '''
        copy source values into this period
        source : dict object of period
        '''
        
        message = "Parameters loaded successfully."

        if source.get("avatar"):
            self.avatar.id = source.get("avatar")["id"]
        
        self.grid_location_row = source.get("grid_location_row")
        self.grid_location_col = source.get("grid_location_col")

        self.save()

        return message

    def json(self):
        '''
        return json object of model
        '''

        return{
            "id" : self.id,
            
            "avatar" : self.avatar.json() if self.avatar else None,
            "grid_location_row" : self.grid_location_row,
            "grid_location_col" : self.grid_location_col,           
        }


