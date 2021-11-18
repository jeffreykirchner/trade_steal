'''
session player model
'''

#import logging
import uuid

from django.db import models
from django.forms.utils import to_current_timezone

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

    player_number = models.IntegerField(verbose_name='Player number', default=0)               #player number, from 1 to N
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name = 'Player Key')   #login and channel key

    timestamp = models.DateTimeField(auto_now_add= True)
    updated= models.DateTimeField(auto_now= True)

    def __str__(self):
        return f"{self.id}"

    class Meta:
        
        verbose_name = 'Session Player'
        verbose_name_plural = 'Session Players'
        ordering = ['parameter_set_player__location']

    def check_good_available_at_location(self, good_location, parameter_set_good):
        '''
        check that player has good of specified type
        good_location : string : house or field
        parameter_set_good : ParametersetGood()
        '''

        #for first two good slots
        if self.parameter_set_player.good_one == parameter_set_good or \
           self.parameter_set_player.good_two == parameter_set_good:
           return True

        #check for third good if allowed
        if good_location == "house" and \
           self.parameter_set_player.parameter_set.good_count == 3 and \
           self.parameter_set_player.good_three == parameter_set_good :
            return True

        return False
    
    def add_good_by_type(self, amount, good_location, parameter_set_good):
        '''
        add amount to good of specificed type
        amount : int
        good_location : string : house or field
        parameter_set_good : ParametersetGood()
        '''

        status = "fail"
        good_number = ""

        if good_location == "house":
            if parameter_set_good == self.parameter_set_player.good_one:

                self.good_one_house += amount
                good_number = "one"
                status = "success"

            elif parameter_set_good == self.parameter_set_player.good_two:

                self.good_two_house += amount
                good_number = "two"
                status = "success"

            elif self.parameter_set_player.parameter_set.good_count == 3 and \
                 self.parameter_set_player.good_three == parameter_set_good:

                self.good_three_house += amount
                good_number = "three"
                status = "success"
        else:

            if parameter_set_good == self.parameter_set_player.good_one:

                self.good_one_field += amount
                good_number = "one"
                status = "success"

            elif parameter_set_good == self.parameter_set_player.good_two:

                self.good_two_field += amount
                good_number = "two"
                status = "success"

        self.save()

        if status == "fail":
            return {"status" : "fail", "amount" : 0}
        else:
           return {"status" : "success", "good_number" : good_number}


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

            "player_number" : self.player_number,
            "uuid" : self.uuid,

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

        