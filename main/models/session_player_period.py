'''
session player period results
'''

#import logging

from django.db import models

from main.models import SessionPlayer
from main.models import SessionPeriod


class SessionPlayerPeriod(models.Model):
    '''
    session player period model
    '''
    session_period = models.ForeignKey(SessionPeriod, on_delete=models.CASCADE, related_name="session_player_periods_a")
    session_player = models.ForeignKey(SessionPlayer, on_delete=models.CASCADE, related_name="session_player_periods_b")

    good_one_production = models.IntegerField(verbose_name='Good one amount')        #amount of good one produced
    good_two_production = models.IntegerField(verbose_name='Good two amount')        #amount of good two produced
    
    good_one_consumption = models.IntegerField(verbose_name='Good one amount')        #amount of good one consumed
    good_two_consumption = models.IntegerField(verbose_name='Good two amount')        #amount of good two consumed
    good_three_consumption = models.IntegerField(verbose_name='Good two amount')      #amount of good three consumed

    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}"

    class Meta:
        
        verbose_name = 'Session Player Period'
        verbose_name_plural = 'Session Player Periods'
        ordering = ['session_period__period_number']
        
    def json_for_subject(self):
        '''
        json object of model
        '''

        return{
            "id" : self.id,    
            
            "period_number" : self.session_period.period_number,

            "good_one_production" : self.good_one_production,
            "good_two_production" : self.good_two_production,

            "good_one_consumption" : self.good_one_consumption,
            "good_two_consumption" : self.good_two_consumption,
            "good_three_consumption" : self.good_three_consumption,
        }