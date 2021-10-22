'''
session's period parameters
'''
from decimal import Decimal

from django.db import models
from django.db.utils import IntegrityError

from main.models import ParameterSet

from main.globals import SubjectType

import main

#experiment session parameters
class ParameterSetPlayer(models.Model):
    '''
    session player parameters 
    '''

    parameter_set = models.ForeignKey(ParameterSet, on_delete=models.CASCADE, related_name="parameter_set_players")

    subject_type = models.CharField(max_length=100, choices=SubjectType.choices, default=SubjectType.ONE)         #type of subject

    id_label = models.CharField(verbose_name='ID Label', max_length = 2, default="1")      #id label shown on screen to subjects
    location = models.IntegerField(verbose_name='Location number (1-8)', default=1)        #location number of 1 to 8
    period_groups = models.JSONField(verbose_name='Group by period', default=dict)         #list of group membershiop by period 

    timestamp = models.DateTimeField(auto_now_add= True)
    updated= models.DateTimeField(auto_now= True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Parameter Set Player'
        verbose_name_plural = 'Parameter Set Players'
        ordering = ['location']

    def from_dict(self, source):
        '''
        copy source values into this period
        source : dict object of period
        '''
        
        message = "Parameters loaded successfully."

        

        return message

    def update_group_period_count(self, count):
        '''
        when period count changes update group with default 1 if needed
        '''

        for i in range(count):
            result = self.period_groups.get(i+1,-1)

            if result == -1:
                self.period_groups[i+1] = {"group" : 1}

        self.save()


    def json(self):
        '''
        return json object of model
        '''

        return{

            "id" : self.id,
            "id_label" : self.id_label,
            "location" : self.location,
            "subject_type" : self.subject_type,
            "period_groups" : self.period_groups,
        }
