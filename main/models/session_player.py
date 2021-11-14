'''
session player model
'''

#import logging

from django.db import models

from main.models import Session, parameter_set_player
from main.models import ParameterSetPlayer

import main

class SessionPlayer(models.Model):
    '''
    session player model
    '''
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="session_players")
    parameter_set_player = models.ForeignKey(ParameterSetPlayer, on_delete=models.CASCADE, related_name="session_players_paramterset")

    good_one_house = models.IntegerField(verbose_name='Good one in house', default=0)        #amount of good one currently in house
    good_two_house = models.IntegerField(verbose_name='Good two in house', default=0)        #amount of good two currently in house
    good_three_house = models.IntegerField(verbose_name='Good three in house', default=0)    #amount of good three currently in house

    good_one_field = models.IntegerField(verbose_name='Good one in field', default=0)        #amount of good one currently in field
    good_two_field = models.IntegerField(verbose_name='Good two in field', default=0)        #amount of good two currently in field

    timestamp = models.DateTimeField(auto_now_add= True)
    updated= models.DateTimeField(auto_now= True)

    def __str__(self):
        return f"{self.id}"

    class Meta:
        
        verbose_name = 'Session Player'
        verbose_name_plural = 'Session Players'
        ordering = ['parameter_set_player__location']

    #return json object of class
    def json(self):
        '''
        json object of model
        '''

        return{
            "id" : self.id,         

            "good_one_house" : self.good_one_house,
            "good_two_house" : self.good_two_house,
            "good_three_house" : self.good_three_house,

            "good_one_field" : self.good_one_field,
            "good_two_field" : self.good_two_field,

            "parameter_set_player" : self.parameter_set_player.json(),

            "sprite" : None,
        }
    
    def json_min(self):
        '''
        minimal json objcet of model
        '''

        return{
            "id" : self.id,         

            "good_one_house" : self.good_one_house,
            "good_two_house" : self.good_two_house,
            "good_three_house" : self.good_three_house,

            "good_one_field" : self.good_one_field,
            "good_two_field" : self.good_two_field,
        }

        