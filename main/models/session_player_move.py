'''
session move goods
'''

#import logging

from django.db import models
from django.db.models import Q
from django.db.models import F

from main.models import SessionPlayer
from main.models import SessionPeriod

from main.globals import ContainerTypes

class SessionPlayerMove(models.Model):
    '''
    session player move model
    '''
    session_period = models.ForeignKey(SessionPeriod, on_delete=models.CASCADE, related_name="session_player_move_a")

    session_player_source = models.ForeignKey(SessionPlayer, on_delete=models.CASCADE, related_name="session_player_move_b")
    session_player_target = models.ForeignKey(SessionPlayer, on_delete=models.CASCADE, related_name="session_player_move_c")

    good_one_amount = models.IntegerField(verbose_name='Good one amount')        #amount of good one to be moved
    good_two_amount = models.IntegerField(verbose_name='Good two amount')        #amount of good two to be moved
    good_three_amount = models.IntegerField(verbose_name='Good three amount')        #amount of good two to be moved
    
    source_container = models.CharField(max_length=100, choices=ContainerTypes.choices)         #source container
    target_container = models.CharField(max_length=100, choices=ContainerTypes.choices)         #target container

    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}"

    class Meta:
        
        verbose_name = 'Session Player Move'
        verbose_name_plural = 'Session Player Moves'
        ordering = ['timestamp']
        constraints = [
            models.CheckConstraint(check=Q(good_one_amount__gte=0), name='good_one_amount__gte_0'),
            models.CheckConstraint(check=Q(good_two_amount__gte=0), name='good_two_amount__gte_0'),
            models.CheckConstraint(check=Q(good_three_amount__gte=0), name='good_three_amount__gte_0'),
            models.CheckConstraint(check=~Q(session_player_source=F('session_player_target')) &
                                         ~Q(source_container=F('target_container')), name='source_equals_target'),
        ]

    #return json object of class
    def json(self):
        '''
        json object of model
        '''

        return{
            "id" : self.id,         

            "session_player_source" : self.session_player_source,
            "session_player_target" : self.session_player_target,

            "good_one_amount" : self.good_one_amount,
            "good_two_amount" : self.good_two_amount,

            "source_container" : self.source_container,
            "target_container" : self.target_container,
        }
        