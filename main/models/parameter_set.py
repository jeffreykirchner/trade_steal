'''
parameter set
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
    parameter set
    '''

    period_count = models.IntegerField(verbose_name='Number of periods', default=20)                          #number of periods in the experiment
    period_length_production = models.IntegerField(verbose_name='Period Length, Production', default=10)      #production phase length in seconds
    period_length_trade = models.IntegerField(verbose_name='Period Length, Trade', default=90)                #trade phase length in seconds
    break_period_frequency = models.IntegerField(verbose_name='Break Period Fequency (Periods)', default=7)   #every x periods only allow chat, no production or trading
    allow_stealing = models.BooleanField(default=False, verbose_name = 'Allow Stealing')                      #if true subjects can take from other users
    private_chat = models.BooleanField(default=True, verbose_name = 'Private Chat')                           #if true subjects can privately chat one on one
    town_count = models.IntegerField(verbose_name='Town Count', default=1)                                    #number of different towns
    good_count = models.IntegerField(verbose_name='Number of Goods', default=2)                               #number of goods available to all towns
    show_avatars = models.BooleanField(default=False, verbose_name = 'Show Avatars')                          #if true show avatar next to field

    test_mode = models.BooleanField(default=False, verbose_name = 'Test Mode')                                 #if true subject screens will do random auto testing

    timestamp = models.DateTimeField(auto_now_add= True)
    updated= models.DateTimeField(auto_now= True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Parameter Set'
        verbose_name_plural = 'Parameter Sets'
    
    def from_dict(self, new_ps):
        '''
        load values from dict
        '''
        logger = logging.getLogger(__name__) 

        message = "Parameters loaded successfully."
        status = "success"

        try:
            self.period_count = new_ps.get("period_count")
            self.period_length_production = new_ps.get("period_length_production")
            self.period_length_trade = new_ps.get("period_length_trade")
            self.break_period_frequency = new_ps.get("break_period_frequency")
            self.allow_stealing = new_ps.get("allow_stealing")
            self.private_chat = new_ps.get("private_chat")
            self.town_count = new_ps.get("town_count")
            self.good_count = new_ps.get("good_count")
            self.show_avatars = new_ps.get("show_avatars")

            self.save()

            #parameter set types
            new_parameter_set_types = new_ps.get("parameter_set_types")
            for new_p in new_parameter_set_types:
                p = self.parameter_set_types.get(subject_type=new_p.get("subject_type"))
                p.from_dict(new_p)
            
            #parameter set goods
            new_parameter_set_goods = new_ps.get("parameter_set_goods")
            for index, p in enumerate(self.parameter_set_goods.all()) :
                p.from_dict(new_parameter_set_goods[index])
            
            #parameter set players
            parameter_set_goods = self.parameter_set_goods.all()
            new_parameter_set_players = new_ps.get("parameter_set_players")

            if len(new_parameter_set_players) > self.parameter_set_players.count():
                #add more players
                new_player_count = len(new_parameter_set_players) - self.parameter_set_players.count()

                for i in range(new_player_count):
                    self.add_new_player(self.parameter_set_types.first(),
                                        i,
                                        parameter_set_goods[0],
                                        parameter_set_goods[1],
                                        parameter_set_goods[2])

            elif len(new_parameter_set_players) < self.parameter_set_players.count():
                #remove excess players

                extra_player_count = self.parameter_set_players.count() - len(new_parameter_set_players)

                for i in range(extra_player_count):
                    self.parameter_set_players.last().delete()
            
            self.update_group_counts()

            new_parameter_set_players = new_ps.get("parameter_set_players")
            counter=0
            for p in self.parameter_set_players.all():                
                p.from_dict(new_parameter_set_players[counter])
                counter+=1

            #parameter set goods
            new_parameter_set_goods = new_ps.get("parameter_set_goods")
            counter=0
            for g in self.parameter_set_goods.all():                
                g.from_dict(new_parameter_set_goods[counter])
                counter+=1            

        except IntegrityError as exp:
            message = f"Failed to load parameter set: {exp}"
            status = "fail"
            logger.warning(message)

        return {"status" : status, "message" :  message}

    def setup(self):
        '''
        default setup
        '''

        #three type parameters
        self.add_parameter_set_type(globals.SubjectType.ONE, Decimal('0'), Decimal('0.411096'), Decimal('2.5'), Decimal('0'), Decimal('2.254'),  Decimal('1'), 3, 1)
        self.add_parameter_set_type(globals.SubjectType.TWO, Decimal('0'), Decimal('2.530'), Decimal('1'), Decimal('0'), Decimal('1.1'),  Decimal('2'), 1, 2)
        self.add_parameter_set_type(globals.SubjectType.THREE, Decimal('0'), Decimal('2.530'), Decimal('1'), Decimal('0'), Decimal('1.1'),  Decimal('2'), 1, 2)
        self.add_parameter_set_type(globals.SubjectType.FOUR, Decimal('0'), Decimal('2.530'), Decimal('1'), Decimal('0'), Decimal('1.1'),  Decimal('2'), 1, 2)
    
        # good setup
        parameter_set_good_one = main.models.ParameterSetGood(parameter_set=self, label="Orange", rgb_color="#FF5733")
        parameter_set_good_one.save()

        parameter_set_good_two = main.models.ParameterSetGood(parameter_set=self, label="Blue", rgb_color="#6495ED")
        parameter_set_good_two.save()

        parameter_set_good_three = main.models.ParameterSetGood(parameter_set=self, label="Pink", rgb_color="#FF1493")
        parameter_set_good_three.save()

        #player setup
        for i in range(8):
            if i % 2 == 0:
                self.add_new_player(self.parameter_set_types.get(subject_type=main.globals.SubjectType.ONE), i,
                                     parameter_set_good_one, parameter_set_good_two, parameter_set_good_three)
            else:
                self.add_new_player(self.parameter_set_types.get(subject_type=main.globals.SubjectType.TWO), i,
                                     parameter_set_good_one, parameter_set_good_two, parameter_set_good_three)
            
        self.update_group_counts()

    def add_parameter_set_type(self, subject_type, g_1_1, g_1_2, g_1_3,g_2_1 ,g_2_2, g_2_3, g1, g2):
        '''
        add new parameter set good
        subject_type :  SubjectType()
        g_1_1 : decimal
        g_1_2 : decimal
        g_1_3 : decimal
        g_2_1 : decimal
        g_2_2 : decimal
        g_2_3 : decimal
        '''

        parameter_set_type = main.models.ParameterSetType()
        parameter_set_type.parameter_set = self
        parameter_set_type.subject_type = subject_type

        parameter_set_type.good_one_production_1 = g_1_1
        parameter_set_type.good_one_production_2 = g_1_2
        parameter_set_type.good_one_production_3 = g_1_3

        parameter_set_type.good_two_production_1 = g_2_1
        parameter_set_type.good_two_production_2 = g_2_2
        parameter_set_type.good_two_production_3 = g_2_3

        parameter_set_type.good_one_amount = g1
        parameter_set_type.good_two_amount = g2

        parameter_set_type.save()

    def add_new_player(self, subject_type, location, good_one, good_two, good_three):
        '''
        add a new player of type subject_type
        '''

        #8 players max
        if self.parameter_set_players.all().count() >= 24:
            return

        player = main.models.ParameterSetPlayer()

        player.parameter_set = self
        player.good_one = good_one
        player.good_two = good_two
        player.good_three = good_three

        player.parameter_set_type = subject_type
        player.id_label = str(location+1)
        player.location = location+1

        player.save()

    def update_group_counts(self):
        '''
        update player group counts
        '''

        for p in self.parameter_set_players.all():
            p.update_group_period_count(self.period_count)

    def copy_groups_forward(self, period_number):
        '''
        copy the specifed period's group forward for all players
        '''

        for p in self.parameter_set_players.all():
            p.copy_group_foward(period_number)

    def get_group(self, group_number, period_number):
        '''
        return the group for the specified period and group number
        group_number : int
        period_number : int
        '''
        
        return main.models.ParameterSetPlayerGroup.objects.filter(period=period_number) \
                                                            .filter(group_number=group_number) \
                                                            .filter(parameter_set_player__in=self.parameter_set_players.all()) \
                                                            .values('parameter_set_player')
       # return [p.parameter_set_player for p in parameter_set_player_group]

    def json(self):
        '''
        return json object of model
        '''
        return{
            "id" : self.id,
            "town_count" : self.town_count,
            "good_count" : self.good_count,
            "period_count" : self.period_count,

            "period_length_production" : self.period_length_production,
            "period_length_trade" : self.period_length_trade,
            "break_period_frequency" : self.break_period_frequency,

            "allow_stealing" : "True" if self.allow_stealing else "False",
            "private_chat" : "True" if self.private_chat else "False",
            "show_avatars" : "True" if self.show_avatars else "False",

            "parameter_set_goods" : [p.json() for p in self.parameter_set_goods.all()],
            "parameter_set_types" : [p.json() for p in self.parameter_set_types.all()],
            "parameter_set_players" : [p.json() for p in self.parameter_set_players.all()],

            "test_mode" : "True" if self.test_mode else "False",
        }
    
    def json_for_subject(self):
        '''
        return json object for subject
        '''
        return{
            "id" : self.id,

            "town_count" : self.town_count,
            "good_count" : self.good_count,
            
            "period_length_production" : self.period_length_production,
            "period_length_trade" : self.period_length_trade,

            "break_period_frequency" : self.break_period_frequency,
            "allow_stealing" : "True" if self.allow_stealing else "False",
            "private_chat" : "True" if self.private_chat else "False",
            "show_avatars" : "True" if self.show_avatars else "False",

            "test_mode" : self.test_mode,
        }

