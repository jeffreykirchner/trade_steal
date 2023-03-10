'''
session period model
'''

#import logging
from statistics import mean

from django.db import models

from main.models import Session

import main

class SessionPeriod(models.Model):
    '''
    session period model
    '''
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="session_periods")

    period_number = models.IntegerField()                       #period number from 1 to N

    timestamp = models.DateTimeField(auto_now_add= True)
    updated= models.DateTimeField(auto_now= True)

    def __str__(self):
        return f"{self.id}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['session', 'period_number'], name='unique_SD')
        ]
        verbose_name = 'Session Period'
        verbose_name_plural = 'Session Periods'
        ordering = ['period_number']

    def update_efficiency(self):
        '''
        calc player efficiency for period
        '''
        for p in self.session_player_periods_a.all():
            p.update_efficiency()
        

    #return json object of class
    def json(self):
        '''
        json object of model
        '''
        #current_best_bid = self.get_current_best_bid()
        #current_best_offer = self.get_current_best_offer()

        #current_trade = self.get_current_trade()

        efficiency_list = [p.efficiency for p in self.session_player_periods_a.all()]

        efficiency_mean = str(mean(efficiency_list)) if len(efficiency_list) > 0 else 0

        return{
            "id" : self.id,
            "period_number" : self.period_number,
            "efficiency_list" : list(map(lambda v:str(v), efficiency_list)) ,
            "efficiency_mean" : efficiency_mean,

        }
        