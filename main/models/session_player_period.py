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

    good_one_production = models.IntegerField(verbose_name='Good one amount produced', default=0)        #amount of good one produced
    good_two_production = models.IntegerField(verbose_name='Good two amount produced', default=0)        #amount of good two produced
    
    good_one_consumption = models.IntegerField(verbose_name='Good one amount consumed', default=0)        #amount of good one consumed
    good_two_consumption = models.IntegerField(verbose_name='Good two amount consumed', default=0)        #amount of good two consumed
    good_three_consumption = models.IntegerField(verbose_name='Good three amount consumed', default=0)      #amount of good three consumed

    earnings = models.IntegerField(verbose_name='Period Earnings', default=0)        #earnings in cents this period

    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Player {self.session_player.parameter_set_player.id_label}, Period {self.session_period.period_number}"

    class Meta:
        
        verbose_name = 'Session Player Period'
        verbose_name_plural = 'Session Player Periods'
        ordering = ['session_player__session', 'session_player', 'session_period__period_number']
        constraints = [
            models.UniqueConstraint(fields=['session_player', 'session_period'], name='unique_session_player_period'),
        ]
        
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

            "earnings" : self.earnings,
        }