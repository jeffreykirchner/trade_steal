'''
session player model
'''

#import logging
import decimal
import uuid
from decimal import Decimal

from django.db import models
from django.forms.utils import to_current_timezone
from django.urls import reverse
from django.db.models import Q
from django.db.models import F
from django.db.models import Value
from django.db.models import Func
from django.db.models.expressions import RawSQL

from main.models import Session, parameter_set_player
from main.models import ParameterSetPlayer

from main.globals import round_half_away_from_zero

import main

class SessionPlayer(models.Model):
    '''
    session player model
    '''
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="session_players")
    parameter_set_player = models.ForeignKey(ParameterSetPlayer, on_delete=models.CASCADE, related_name="session_players_paramterset")

    good_one_house = models.DecimalField(verbose_name = 'Good one in house', decimal_places=0, default=0, max_digits=3)
    good_two_house =  models.DecimalField(verbose_name = 'Good two in house', decimal_places=0, default=0, max_digits=3)
    good_three_house =  models.DecimalField(verbose_name = 'Good three in house', decimal_places=0, default=0, max_digits=3)

    good_one_field = models.DecimalField(verbose_name = 'Good one in field', decimal_places=9, default=0, max_digits=12)
    good_two_field = models.DecimalField(verbose_name = 'Good two in field', decimal_places=9, default=0, max_digits=12)

    good_one_production_rate = models.IntegerField(verbose_name='Good one production rate (0-100)', default=50)        #percent of time to devote to good one production
    good_two_production_rate = models.IntegerField(verbose_name='Good two production rate (0-100)', default=50)        #percent of time to devote to good two production

    player_number = models.IntegerField(verbose_name='Player number', default=0)               #player number, from 1 to N
    player_key = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name = 'Player Key')   #login and channel key

    earnings = models.IntegerField(verbose_name='Earnings in cents', default=0)      #earnings in cents

    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}"

    class Meta:
        
        verbose_name = 'Session Player'
        verbose_name_plural = 'Session Players'
        ordering = ['parameter_set_player__town', 'parameter_set_player__location']
        constraints = [
              models.CheckConstraint(check=RawSQL('good_one_production_rate+good_two_production_rate=100',
                                                  (),
                                                  output_field=models.BooleanField(),),                                                                       
                                     name='production_total_equals_100'),
        ]

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

    def reset(self):
        '''
        reset player to starting state
        '''
        self.session_player_moves_b.all().delete()
        self.session_player_chats_b.all().delete()

        self.good_one_house = 0
        self.good_two_house = 0
        self.good_three_house = 0

        self.good_one_field = 0
        self.good_two_field = 0
        self.good_three_field = 0

        self.earnings = 0

        self.save()

    def get_current_group_list(self):
        '''
        return list of session_players in group
        '''

        parameter_set_player_group_all = self.parameter_set_player.parameter_set.get_group(self.get_current_group_number(), self.session.current_period)
        
        return self.session.session_players.filter(parameter_set_player__in=parameter_set_player_group_all)

    def get_current_group_number(self):
        '''
        return current group number
        '''
        return self.parameter_set_player.parameter_set_player_groups.get(period=self.session.current_period).group_number
    
    def get_current_town_number(self):
        '''
        return current town number
        '''
        return self.parameter_set_player.town

    def do_period_production(self, current_time):
        '''
        do one second of production
        '''

        # Good Production = P1 + P2 x Time ^ P3

        
        parameter_set_type = self.parameter_set_player.parameter_set_type
  
        self.good_one_field += self.do_period_production_function(parameter_set_type.good_one_production_1,
                                                                  parameter_set_type.good_one_production_2,
                                                                  parameter_set_type.good_one_production_3,
                                                                  self.good_one_production_rate)

        self.good_two_field += self.do_period_production_function(parameter_set_type.good_two_production_1,
                                                                  parameter_set_type.good_two_production_2,
                                                                  parameter_set_type.good_two_production_3,
                                                                  self.good_two_production_rate)

        self.save()

    def do_period_production_function(self, good_production_1, good_production_2, good_production_3, production_rate):
        '''
        return production for single good
        '''
        total_time = Decimal(self.parameter_set_player.parameter_set.period_length_production)

        good_time =  total_time * Decimal(production_rate)/Decimal('100')
        production = good_production_1 + good_production_2 * good_time ** good_production_3
        production *= Decimal('1')/total_time

        return round(production, 9)
        
    def do_period_consumption(self):
        '''
        covert goods in house to earnings
        '''

        self.good_one_house = 0
        self.good_two_house = 0
        self.good_three_house = 0

        self.good_one_field = 0
        self.good_two_field = 0

        self.save()

    def json(self):
        '''
        json object of model
        '''
        return{
            "id" : self.id,         

            "good_one_house" : round_half_away_from_zero(self.good_one_house, 0),
            "good_two_house" : round_half_away_from_zero(self.good_two_house, 0),
            "good_three_house" : round_half_away_from_zero(self.good_three_house, 0),

            "good_one_field" : round_half_away_from_zero(self.good_one_field, 0),
            "good_two_field" : round_half_away_from_zero(self.good_two_field, 0),

            "earnings" : self.earnings,

            "player_number" : self.player_number,
            "player_key" : self.player_key,

            "login_link" : reverse('subject_home', kwargs={'player_key': self.player_key}),

            "parameter_set_player" : self.parameter_set_player.json(),

            "chat_all" : [c.json_for_subject() for c in self.session_player_chats_c.filter(chat_type=main.globals.ChatTypes.ALL)],
        }
    
    def json_for_subject(self, session_player):
        '''
        json model for subject screen
        session_player_id : int : id number of session player for induvidual chat
        '''

        return{
            "id" : self.id,  

            "good_one_house" : round_half_away_from_zero(self.good_one_house, 0),
            "good_two_house" : round_half_away_from_zero(self.good_two_house, 0),
            "good_three_house" : round_half_away_from_zero(self.good_three_house, 0),

            "good_one_field" : round_half_away_from_zero(self.good_one_field, 0),
            "good_two_field" : round_half_away_from_zero(self.good_two_field, 0),

            "player_number" : self.player_number,

            "chat_individual" : [c.json_for_subject() for c in  main.models.SessionPlayerChat.objects \
                                                                            .filter(chat_type=main.globals.ChatTypes.INDIVIDUAL) \
                                                                            .filter(Q(Q(session_player_recipients=session_player) & Q(session_player=self)) |
                                                                                    Q(Q(session_player_recipients=self) & Q(session_player=session_player))                       )],

            "parameter_set_player" : self.parameter_set_player.json_for_subject(),
        }

    def json_min(self):
        '''
        minimal json object of model
        '''

        return{
            "id" : self.id,         

            "good_one_house" : round_half_away_from_zero(self.good_one_house, 0),
            "good_two_house" : round_half_away_from_zero(self.good_two_house, 0),
            "good_three_house" : round_half_away_from_zero(self.good_three_house, 0),

            "good_one_field" : round_half_away_from_zero(self.good_one_field, 0),
            "good_two_field" : round_half_away_from_zero(self.good_two_field, 0),
        }

        