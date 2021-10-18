'''
session's period parameters
'''
from decimal import Decimal

from django.db import models
from django.db.utils import IntegrityError

from main.models import ParameterSet

import main

#experiment session parameters
class ParameterSetPeriod(models.Model):
    '''
    session single period parameters 
    '''

    parameter_set = models.ForeignKey(ParameterSet, on_delete=models.CASCADE,  related_name="parameter_set_periods")

    period_number = models.IntegerField(verbose_name='Period number')                                       #period from 1 - N in parameter set
     
    timestamp = models.DateTimeField(auto_now_add= True)
    updated= models.DateTimeField(auto_now= True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Period Parameter Set'
        verbose_name_plural = 'Period Parameter Sets'
        ordering = ['period_number']
        constraints = [
            models.UniqueConstraint(fields=['parameter_set', 'period_number'], name='unique_period'),
        ]

    def from_dict(self, source, copy_buyers, copy_sellers, copy_price_cap):
        '''
        copy source values into this period
        source : dict object of period
        '''
        
        message = "Parameters loaded successfully."

        

        return message


    def json(self):
        '''
        return json object of model
        '''

       

        return{

            "id" : self.id,
            "period_number" : self.period_number,
        }
