'''
session model
'''

from datetime import datetime

import logging
import uuid

from asgiref.sync import sync_to_async
from django.conf import settings

from django.dispatch import receiver
from django.db import models
from django.db.models.signals import post_delete
from django.utils.timezone import now
from django.core.exceptions import ObjectDoesNotExist

import main

from main.models import ParameterSet, parameter_set
from main.models import Parameters

from main.globals import PeriodPhase

#experiment sessoin
class Session(models.Model):
    '''
    session model
    '''
    parameter_set = models.ForeignKey(ParameterSet, on_delete=models.CASCADE)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    title = models.CharField(max_length = 300, default="*** New Session ***")    #title of session
    start_date = models.DateField(default=now)                                   #date of session start

    channel_key = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name = 'Channel Key')     #unique channel to communicate on
    session_key = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name = 'Session Key')     #unique key for session to auto login subjects by id

    started =  models.BooleanField(default=False)                                #starts session and filll in session
    current_period = models.IntegerField(default=0)                              #current period of the session
    current_period_phase = models.CharField(max_length=100, choices=PeriodPhase.choices, default=PeriodPhase.PRODUCTION)         #current phase of current period
    time_remaining = models.IntegerField(default=0)                              #time remaining in current phase of current period
    timer_running = models.BooleanField(default=False)                           #true when period timer is running
    finished = models.BooleanField(default=False)                                #true after all session periods are complete

    shared = models.BooleanField(default=False)                                  #shared session parameter sets can be imported by other users
    locked = models.BooleanField(default=False)                                  #locked models cannot be deleted

    soft_delete =  models.BooleanField(default=False)                            #hide session if true

    timestamp = models.DateTimeField(auto_now_add=True)
    updated= models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def creator_string(self):
        return self.creator.email
    creator_string.short_description = 'Creator'

    class Meta:
        verbose_name = 'Session'
        verbose_name_plural = 'Sessions'
        ordering = ['-start_date']

    def get_start_date_string(self):
        '''
        get a formatted string of start date
        '''
        return  self.start_date.strftime("%#m/%#d/%Y")

    def start_experiment(self):
        '''
        setup and start experiment
        '''

        self.started = True
        self.finished = False
        self.current_period = 1
        self.start_date = datetime.now()
        self.current_period_phase = PeriodPhase.PRODUCTION
        self.time_remaining = self.parameter_set.period_length_production

        session_periods = []

        for i in range(self.parameter_set.period_count):
            session_periods.append(main.models.SessionPeriod(session=self, period_number=i+1))
        
        main.models.SessionPeriod.objects.bulk_create(session_periods)

        self.save()
    
    def reset_experiment(self):
        '''
        reset the experiment
        '''
        self.started = False
        self.finished = False
        self.current_period = 1
        self.timer_running = False

        for p in self.session_players.all():
            p.reset()

        self.save()
        self.session_periods.all().delete()
    
    def get_current_session_period(self):
        '''
        return the current session period
        '''
        if not self.started:
            return None

        return self.session_periods.get(period_number=self.current_period)
    
    def update_player_count(self):
        '''
        update the number of session players based on the number defined in the parameterset
        '''

        self.session_players.all().delete()
    
        for count, i in enumerate(self.parameter_set.parameter_set_players.all()):
            new_session_player = main.models.SessionPlayer()

            new_session_player.session = self
            new_session_player.parameter_set_player = i
            new_session_player.player_number = count + 1

            new_session_player.save()

    def do_period_timer(self):
        '''
        do period timer actions
        '''

        status = "success"

        #check session over
        if self.time_remaining == 0 and \
           self.current_period_phase == PeriodPhase.TRADE and \
           self.current_period == self.parameter_set.period_count:

            self.finished = True
            status = "fail"

        if status != "fail":
            if self.time_remaining == 0:

                if self.current_period_phase == PeriodPhase.PRODUCTION:
                    #start trade phase
                    self.current_period_phase = PeriodPhase.TRADE
                    self.time_remaining = self.parameter_set.period_length_trade
                else:
                    self.current_period += 1
                    self.current_period_phase = PeriodPhase.PRODUCTION
                    self.time_remaining = self.parameter_set.period_length_production
                
            else:
                self.time_remaining -= 1

        self.save()

        result = self.json_for_timmer()

        return {"value" : status, "result" : result}

    def json(self):
        '''
        return json object of model
        '''
        
        chat = {}
        for i in range(self.parameter_set.town_count):
            chat[str(i+1)] = [c.json_for_staff() for c in main.models.SessionPlayerChat.objects \
                                                       .filter(session_player__in=self.session_players.all())\
                                                       .filter(session_player__parameter_set_player__town=i+1)                                                       
                             ]

        return{
            "id":self.id,
            "title":self.title,
            "locked":self.locked,
            "start_date":self.get_start_date_string(),
            "started":self.started,
            "current_period":self.current_period,
            "current_period_phase":self.current_period_phase,
            "time_remaining":self.time_remaining,
            "timer_running":self.timer_running,
            "finished":self.finished,
            "parameter_set":self.parameter_set.json(),
            "session_periods":[i.json() for i in self.session_periods.all()],
            "session_players":[i.json() for i in self.session_players.all()],
            "chat_all" : chat,
        }
    
    def json_for_subject(self, session_player):
        '''
        json object for subject screen
        session_player : SessionPlayer() : session player requesting session object
        '''
        
        return{
            "started":self.started,
            "current_period":self.current_period,
            "current_period_phase":self.current_period_phase,
            "time_remaining":self.time_remaining,
            "timer_running":self.timer_running,
            "finished":self.finished,
            "parameter_set":self.parameter_set.json_for_subject(),

            "session_players":[i.json_for_subject(session_player) for i in session_player.get_current_group_list()]
        }
    
    def json_for_timmer(self):
        '''
        return json object for timer update
        '''

        return{
            "started":self.started,
            "current_period":self.current_period,
            "current_period_phase":self.current_period_phase,
            "time_remaining":self.time_remaining,
            "timer_running":self.timer_running,
            "finished":self.finished,
        }
       
@receiver(post_delete, sender=Session)
def post_delete_parameterset(sender, instance, *args, **kwargs):
    '''
    use signal to delete associated parameter set
    '''
    if instance.parameter_set:
        instance.parameter_set.delete()
