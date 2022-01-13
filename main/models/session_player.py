'''
session player model
'''

#import logging
import uuid
import logging

from decimal import Decimal

from django.db import models
from django.urls import reverse
from django.db.models import Q
from django.db.models.expressions import RawSQL
from django.core.exceptions import ObjectDoesNotExist

from main.models import Session
from main.models import ParameterSetPlayer
from main.models import Avatar

from main.globals import round_half_away_from_zero

import main

class SessionPlayer(models.Model):
    '''
    session player model
    '''
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="session_players")
    parameter_set_player = models.ForeignKey(ParameterSetPlayer, on_delete=models.CASCADE, related_name="session_players_paramterset")
    avatar = models.ForeignKey(Avatar, on_delete=models.CASCADE, related_name="session_players_b", null=True, blank=True)

    good_one_house = models.DecimalField(verbose_name = 'Good one in house', decimal_places=0, default=0, max_digits=3)
    good_two_house =  models.DecimalField(verbose_name = 'Good two in house', decimal_places=0, default=0, max_digits=3)
    good_three_house =  models.DecimalField(verbose_name = 'Good three in house', decimal_places=0, default=0, max_digits=3)

    good_one_field = models.DecimalField(verbose_name = 'Good one in field', decimal_places=9, default=0, max_digits=12)
    good_two_field = models.DecimalField(verbose_name = 'Good two in field', decimal_places=9, default=0, max_digits=12)

    good_one_production_rate = models.IntegerField(verbose_name='Good one production rate (0-100)', default=50)        #percent of time to devote to good one production
    good_two_production_rate = models.IntegerField(verbose_name='Good two production rate (0-100)', default=50)        #percent of time to devote to good two production

    player_number = models.IntegerField(verbose_name='Player number', default=0)                        #player number, from 1 to N
    player_key = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name = 'Player Key')      #login and channel key
    connecting = models.BooleanField(default=False, verbose_name='Consumer is connecting')              #true when a consumer is connceting
    connected_count = models.IntegerField(verbose_name='Number of consumer connections', default=0)     #number of consumers connected to this subject

    name = models.CharField(verbose_name='Full Name', max_length = 100, default="")                     #subject's full name
    student_id = models.CharField(verbose_name='Student ID', max_length = 100, default="")              #subject's student ID number
    email =  models.EmailField(verbose_name='Email Address', max_length = 100, blank=True)              #subject's email address
    earnings = models.IntegerField(verbose_name='Earnings in cents', default=0)                         #earnings in cents

    current_instruction = models.IntegerField(verbose_name='Current Instruction', default=0)                     #current instruction page subject is on
    current_instruction_complete = models.IntegerField(verbose_name='Current Instruction Complete', default=0)   #furthest complete page subject has done
    instructions_finished = models.BooleanField(verbose_name='Instructions Finished', default=False)             #true once subject has completed instructions

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
        self.session_player_periods_b.all().delete()
        self.session_player_notices_b.all().delete()

        self.good_one_house = 0
        self.good_two_house = 0
        self.good_three_house = 0

        self.good_one_field = 0
        self.good_two_field = 0
        self.good_three_field = 0

        self.earnings = 0
        self.name = ""
        self.student_id = ""

        self.good_one_production_rate = 50
        self.good_two_production_rate = 50

        self.avatar = None

        self.current_instruction = 1
        self.current_instruction_complete = 1
        self.instructions_finished = False

        self.save()
    
    def start(self):
        '''
        start experiment
        '''

        self.reset()

        #session player periods
        session_player_periods = []

        for i in self.session.session_periods.all():
            session_player_periods.append(main.models.SessionPlayerPeriod(session_period=i, session_player=self))
        
        main.models.SessionPlayerPeriod.objects.bulk_create(session_player_periods)

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
        logger = logging.getLogger(__name__)

        try:
            return self.parameter_set_player.parameter_set_player_groups.get(period=self.session.current_period).group_number
        except ObjectDoesNotExist:
            logging.warning(f"get_current_group_number: not found for period {self.session.current_period}")
            return -1
    
    def get_group_number(self, period_number):
        '''
        return group number for player for period_number
        '''
        try:
            return self.parameter_set_player.parameter_set_player_groups.get(period=period_number).group_number
        except ObjectDoesNotExist:
            logging.warning(f"get_group_number: not found for period {self.session.current_period}")
            return -1

    def get_group_changed_this_period(self):
        '''
        true if subject is in a new group this period
        '''
        if self.session.current_period == 1:
            return False

        if self.parameter_set_player.parameter_set_player_groups.get(period=self.session.current_period).group_number != \
           self.parameter_set_player.parameter_set_player_groups.get(period=self.session.current_period-1).group_number:

           return True
        
        return False

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

    def record_period_production(self):
        '''
        record how much subject produced this period
        '''

        session_player_period = self.session_player_periods_b.get(session_period=self.session.get_current_session_period())

        session_player_period.good_one_production = round_half_away_from_zero(self.good_one_field, 0)
        session_player_period.good_two_production = round_half_away_from_zero(self.good_two_field, 0)

        session_player_period.good_one_production_rate = self.good_one_production_rate
        session_player_period.good_two_production_rate = self.good_two_production_rate

        session_player_period.save() 

        #record production notice        
        text = f'Period {self.session.current_period} production: '

        if session_player_period.good_one_production == 0 and session_player_period.good_two_production == 0:
            text += "None"
        else:
            if session_player_period.good_one_production > 0:
                text += f"{int(session_player_period.good_one_production)} {self.parameter_set_player.good_one.get_html()}"
            
            if session_player_period.good_two_production > 0:
                if session_player_period.good_one_production > 0:
                    text += ' and '

                text += f"{int(session_player_period.good_two_production)} {self.parameter_set_player.good_two.get_html()}"

            text += ' at '
            text += f'{session_player_period.good_one_production_rate}% {self.parameter_set_player.good_one.get_html()} and '
            text += f'{session_player_period.good_two_production_rate}% {self.parameter_set_player.good_two.get_html()}'

            text += "."

        return self.add_notice(text)

    def add_notice(self, text):
        '''
        add notice
        '''
        session_player_notice = main.models.SessionPlayerNotice()

        session_player_notice.session_period = self.session.get_current_session_period()
        session_player_notice.session_player = self

        session_player_notice.text = text

        session_player_notice.save()

        return session_player_notice.json()

    def do_period_consumption(self):
        '''
        covert goods in house to earnings
        '''

        #record house inventory
        session_player_period = self.session_player_periods_b.get(session_period=self.session.get_current_session_period())

        session_player_period.good_one_consumption = int(self.good_one_house)
        session_player_period.good_two_consumption = int(self.good_two_house)
        session_player_period.good_three_consumption = int(self.good_three_house)

        #convert goods to earnings

        parameter_set_type = self.parameter_set_player.parameter_set_type

        earnings_per_unit = max(parameter_set_type.good_one_amount, parameter_set_type.good_two_amount)

        while self.good_one_house >= parameter_set_type.good_one_amount and \
              self.good_two_house >= parameter_set_type.good_two_amount:

              self.earnings += earnings_per_unit
              session_player_period.earnings += earnings_per_unit

              self.good_one_house -= parameter_set_type.good_one_amount
              self.good_two_house -= parameter_set_type.good_two_amount

        self.good_one_house = 0
        self.good_two_house = 0
        self.good_three_house = 0

        self.good_one_field = 0
        self.good_two_field = 0

        self.save()
        session_player_period.save()

    def get_instruction_set(self):
        '''
        return a proccessed list of instructions to the subject
        '''

        instructions = [i.json() for i in self.parameter_set_player.parameter_set.instruction_set.instructions.all()]
 
        for i in instructions:
            i["text_html"] = i["text_html"].replace("#player_number#", self.parameter_set_player.id_label)
            i["text_html"] = i["text_html"].replace("#player_count-1#", str(self.parameter_set_player.parameter_set.get_town_count(self.parameter_set_player.town)-1))
            i["text_html"] = i["text_html"].replace("#good_one#", self.parameter_set_player.good_one.get_html())
            i["text_html"] = i["text_html"].replace("#good_two#", self.parameter_set_player.good_two.get_html())
            i["text_html"] = i["text_html"].replace("#good_three#", self.parameter_set_player.good_three.get_html())
            i["text_html"] = i["text_html"].replace("#production_length#", str(self.parameter_set_player.parameter_set.period_length_production))
            i["text_html"] = i["text_html"].replace("#move_length#", str(self.parameter_set_player.parameter_set.period_length_trade))
            i["text_html"] = i["text_html"].replace("#good_one_count#", str(self.parameter_set_player.parameter_set_type.good_one_amount))
            i["text_html"] = i["text_html"].replace("#good_two_count#", str(self.parameter_set_player.parameter_set_type.good_two_amount))
            i["text_html"] = i["text_html"].replace("#good_earnings#", str(max(self.parameter_set_player.parameter_set_type.good_one_amount, self.parameter_set_player.parameter_set_type.good_two_amount)))
            i["text_html"] = i["text_html"].replace("#break_period#", str(self.parameter_set_player.parameter_set.break_period_frequency))

        return instructions

    def json(self, get_chat=True):
        '''
        json object of model
        '''
        return{
            "id" : self.id,      
            "name" : self.name,
            "student_id" : self.student_id,   
            "email" : self.email,

            "good_one_house" : round_half_away_from_zero(self.good_one_house, 0),
            "good_two_house" : round_half_away_from_zero(self.good_two_house, 0),
            "good_three_house" : round_half_away_from_zero(self.good_three_house, 0),

            "good_one_field" : round_half_away_from_zero(self.good_one_field, 0),
            "good_two_field" : round_half_away_from_zero(self.good_two_field, 0),

            "earnings" : self.earnings,

            "good_one_production_rate" : self.good_one_production_rate,
            "good_two_production_rate" : self.good_two_production_rate,

            "player_number" : self.player_number,
            "player_key" : self.player_key,

            "login_link" : reverse('subject_home', kwargs={'player_key': self.player_key}),
            "connected_count" : self.connected_count,

            "parameter_set_player" : self.parameter_set_player.json(),

            "group_number" : self.get_current_group_number(),

            "chat_all" : [c.json_for_subject() for c in self.session_player_chats_c.filter(chat_type=main.globals.ChatTypes.ALL)
                                                                                   .order_by('-timestamp')[:100:-1]
                         ] if get_chat else [],
            "new_chat_message" : False,           #true on client side when a new un read message comes in

            "notices" : [n.json() for n in self.session_player_notices_b.all()] if get_chat else [],

            "avatar" : self.avatar.json() if self.avatar else None,

            "current_instruction" : self.current_instruction,
            "current_instruction_complete" : self.current_instruction_complete,
            "instructions_finished" : self.instructions_finished,

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

            "group_number" : self.get_current_group_number(),

            "chat_individual" : [c.json_for_subject() for c in  main.models.SessionPlayerChat.objects \
                                                                            .filter(chat_type=main.globals.ChatTypes.INDIVIDUAL) \
                                                                            .filter(Q(Q(session_player_recipients=session_player) & Q(session_player=self)) |
                                                                                    Q(Q(session_player_recipients=self) & Q(session_player=session_player)))
                                                                            .order_by('-timestamp')[:100:-1]
                                ],

            "new_chat_message" : False,           #true on client side when a new un read message comes in

            "parameter_set_player" : self.parameter_set_player.json_for_subject(),

            "avatar" : self.avatar.json() if self.avatar else None,
        }

    def json_min(self, session_player_notice=None):
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

            "group_number" : self.get_current_group_number(),

            "notice" : session_player_notice.json() if session_player_notice else None,
        }
    
    def json_earning(self):
        '''
        return json object of earnings only
        '''
        return{
            "id" : self.id, 
            "earnings" : self.earnings,
        }
    
    def get_earnings_in_dollars(self):
        '''
        return earnings in dollar format
        '''

        return f'${(self.earnings/100):.2f}'


        