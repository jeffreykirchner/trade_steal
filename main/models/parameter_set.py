'''
sessions parameters
'''
import logging

from decimal import Decimal

from django.db import models
from django.db.utils import IntegrityError
from django.db.models.signals import post_init
from django.dispatch import receiver

from main import globals

import main

#experiment session parameters
class ParameterSet(models.Model):
    '''
    session parameters
    '''

    period_count = models.IntegerField(verbose_name='Number of periods', default=20)                          #number of periods in the experiment
    period_length_production = models.IntegerField(verbose_name='Period Length, Production', default=10)      #production phase length in seconds
    period_length_trade = models.IntegerField(verbose_name='Period Length, Trade', default=90)                #trade phase length in seconds
    break_period_frequency = models.IntegerField(verbose_name='Break Period Fequency (Periods)', default=7)   #every x periods only allow chat, no production or trading
    allow_stealing = models.BooleanField(default=True, verbose_name = 'Allow Stealing')                       #if true subjects can take from other users

    good_one_label =  models.CharField(verbose_name='Good One Label', max_length = 10, default="Red")        #label for good one
    good_two_label =  models.CharField(verbose_name='Good One Label', max_length = 10, default="Blue")       #label for good two

    good_one_rgb_color =  models.CharField(verbose_name='Good One RGB Color', max_length = 10, default="#DC143C")      #rgb color of good one
    good_two_rgb_color =  models.CharField(verbose_name='Good Two RGB Color', max_length = 10, default="#6495ED")      #rgb color of good two

    timestamp = models.DateTimeField(auto_now_add= True)
    updated= models.DateTimeField(auto_now= True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Parameter Set'
        verbose_name_plural = 'Parameter Sets'
    
    def setup(self):
        '''
        default setup
        '''

        #one type parameters
        parameter_set_type_one = main.models.ParameterSetType()
        parameter_set_type_one.parameter_set = self
        parameter_set_type_one.subject_type = globals.SubjectType.ONE

        parameter_set_type_one.good_one_production_1 = Decimal('0')
        parameter_set_type_one.good_one_production_2 = Decimal('0.411096')
        parameter_set_type_one.good_one_production_3 = Decimal('2.5')

        parameter_set_type_one.good_two_production_1 = Decimal('0')
        parameter_set_type_one.good_two_production_2 = Decimal('2.254')
        parameter_set_type_one.good_two_production_3 = Decimal('1')

        parameter_set_type_one.save()

        #two type parameters
        parameter_set_type_two = main.models.ParameterSetType()
        parameter_set_type_two.parameter_set = self
        parameter_set_type_two.subject_type = globals.SubjectType.TWO

        parameter_set_type_two.good_one_production_1 = Decimal('0')
        parameter_set_type_two.good_one_production_2 = Decimal('2.530')
        parameter_set_type_two.good_one_production_3 = Decimal('1')

        parameter_set_type_two.good_two_production_1 = Decimal('0')
        parameter_set_type_two.good_two_production_2 = Decimal('1.1')
        parameter_set_type_two.good_two_production_3 = Decimal('2')

        parameter_set_type_two.save()

        #player setup
        for i in range(8):
            player = main.models.ParameterSetPlayer()
            player.parameter_set = self

            if i % 2 == 0:
                player.parameter_set_type = parameter_set_type_one
            else:
                player.parameter_set_type = parameter_set_type_two

            player.id_label = str(i+1)
            player.location = i+1

            player.save()
            player.update_group_period_count(self.period_count)

    def json(self):
        '''
        return json object of model
        '''
        return{
            "id" : self.id,
            "period_count" : self.period_count,
            "period_length_production" : self.period_length_production,
            "period_length_trade" : self.period_length_trade,
            "break_period_frequency" : self.break_period_frequency,
            "allow_stealing" : "True" if self.allow_stealing else "False",
            "good_one_label" : self.good_one_label,
            "good_two_label" : self.good_two_label,
            "good_one_rgb_color" : self.good_one_rgb_color,
            "good_two_rgb_color" : self.good_two_rgb_color,
            "parameter_set_types" : [p.json() for p in self.parameter_set_types.all()],
            "parameter_set_players" : [p.json() for p in self.parameter_set_players.all()],
        }
