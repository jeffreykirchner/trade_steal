'''
session model
'''

from datetime import datetime
from tinymce.models import HTMLField
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

import logging
import uuid
import csv
import io
import random
import string

from django.conf import settings

from django.dispatch import receiver
from django.db import models
from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.utils.timezone import now
from django.core.exceptions import ObjectDoesNotExist

import main

from main.models import ParameterSet, avatar

from main.globals import PeriodPhase
from main.globals import AvatarModes
from main.globals import ExperimentPhase
from main.globals import AvatarModes

#experiment sessoin
class Session(models.Model):
    '''
    session model
    '''
    parameter_set = models.ForeignKey(ParameterSet, on_delete=models.CASCADE)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sessions_a")
    collaborators = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="sessions_b")

    title = models.CharField(max_length = 300, default="*** New Session ***")    #title of session

    start_date = models.DateField(default=now)                                   #date of session start

    channel_key = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name = 'Channel Key')     #unique channel to communicate on
    session_key = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name = 'Session Key')     #unique key for session to auto login subjects by id

    id_string = models.CharField(max_length=6, unique=True, null=True, blank=True)                       #unique string for session to auto login subjects by id

    controlling_channel = models.CharField(max_length = 300, default="")         #channel controlling session

    started =  models.BooleanField(default=False)                                #starts session and filll in session
    current_experiment_phase = models.CharField(max_length=100, choices=ExperimentPhase.choices, default=ExperimentPhase.RUN)         #current phase of expeirment
    current_period = models.IntegerField(default=0)                              #current period of the session
    current_period_phase = models.CharField(max_length=100, choices=PeriodPhase.choices, default=PeriodPhase.PRODUCTION)         #current phase of current period
    time_remaining = models.IntegerField(default=0)                              #time remaining in current phase of current period
    timer_running = models.BooleanField(default=False)                           #true when period timer is running
    finished = models.BooleanField(default=False)                                #true after all session periods are complete

    shared = models.BooleanField(default=False)                                  #shared session parameter sets can be imported by other users
    locked = models.BooleanField(default=False)                                  #locked models cannot be deleted

    invitation_text = HTMLField(default="", verbose_name="Invitation Text")      #inviataion email subject and text
    invitation_subject = HTMLField(default="", verbose_name="Invitation Subject")

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

    def get_group_channel_name(self):
        '''
        return channel name for group
        '''
        page_key = f"session-{self.id}"
        room_name = f"{self.channel_key}"
        return  f'{page_key}-{room_name}'
    
    def send_message_to_group(self, message_type, message_data):
        '''
        send socket message to group
        '''
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(self.get_group_channel_name(),
                                                {"type" : message_type,
                                                 "data" : message_data})

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

        # if self.parameter_set.avatar_assignment_mode == AvatarModes.SUBJECT_SELECT or \
        #    self.parameter_set.avatar_assignment_mode == AvatarModes.BEST_MATCH :

        #     self.current_experiment_phase = ExperimentPhase.SELECTION
        # el   
        #      
        if self.parameter_set.show_instructions:
            self.current_experiment_phase = ExperimentPhase.INSTRUCTIONS
        else:
             self.current_experiment_phase = ExperimentPhase.RUN

        session_periods = []

        for i in range(self.parameter_set.period_count):
            session_periods.append(main.models.SessionPeriod(session=self, period_number=i+1))
        
        main.models.SessionPeriod.objects.bulk_create(session_periods)

        self.save()

        if self.parameter_set.avatar_assignment_mode == AvatarModes.PRE_ASSIGNED:
            self.pre_assign_avatars()

        for i in self.session_players.all():
            i.start()
    
    def pre_assign_avatars(self):
        '''
        asign avatars based on parameter set player
        '''
        logger = logging.getLogger(__name__)
        logger.info("pre_assign_avatars")

        for i in self.session_players.all():
            i.avatar = i.parameter_set_player.avatar
            i.save()
 
    def reset_experiment(self):
        '''
        reset the experiment
        '''
        self.started = False
        self.finished = False
        self.current_period = 1
        self.current_period_phase = PeriodPhase.PRODUCTION
        self.current_experiment_phase = ExperimentPhase.RUN
        self.time_remaining = self.parameter_set.period_length_production
        self.timer_running = False

        for p in self.session_players.all():
            p.reset()

        self.save()
        self.session_periods.all().delete()
    
    def reset_connection_counts(self):
        '''
        reset connection counts
        '''
        self.session_players.all().update(connecting=False, connected_count=0)
    
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
        end_game = False
        period_update = None

        #check session over
        if self.time_remaining == 0 and \
           self.current_period_phase == PeriodPhase.TRADE and \
           self.current_period >= self.parameter_set.period_count:

            self.do_period_consumption()
            period_update = self.get_current_session_period()
            self.finished = True
            end_game = True

        notice_list = []
        

        if not status == "fail" and not end_game:

            if self.time_remaining == 0:

                if self.current_period_phase == PeriodPhase.PRODUCTION:
                    notice_list = self.record_period_production()
                                       
                    #start trade phase
                    self.current_period_phase = PeriodPhase.TRADE
                    self.time_remaining = self.parameter_set.period_length_trade
                else:
                    self.do_period_consumption()
                    
                    period_update = self.get_current_session_period()
                    if period_update:
                        period_update.update_efficiency()

                    self.current_period += 1
                    self.current_period_phase = PeriodPhase.PRODUCTION
                    self.time_remaining = self.parameter_set.period_length_production                         

                    if self.current_period % self.parameter_set.break_period_frequency == 0:
                        notice_list = self.add_notice_to_all(f"<center>*** Break period, chat only, no production. ***</center>")           
            else:
                
                if self.current_period_phase == PeriodPhase.PRODUCTION:

                    if self.current_period % self.parameter_set.break_period_frequency != 0 :
                        self.do_period_production()                        

                self.time_remaining -= 1

        self.save()

        result = self.json_for_timmer()

        return {"value" : status,
                "result" : result,
                "period_update" : period_update.json() if period_update else None,
                "notice_list" : notice_list,
                "end_game" : end_game}

    def do_period_production(self):
        '''
        do one second of production for all players
        '''

        for p in self.session_players.all():
            p.do_period_production(self.time_remaining)
    
    def record_period_production(self):
        '''
        do one second of production for all players
        '''

        notice_list=[]

        for p in self.session_players.all():
            notice_list.append(p.record_period_production())

        return notice_list
    
    def add_notice_to_all(self, text):
        notice_list=[]

        for p in self.session_players.all():
            notice_list.append(p.add_notice(text))

        return notice_list
    
    def do_period_consumption(self):
        '''
        covert goods in house to earnings
        '''

        for p in self.session_players.all():
            p.do_period_consumption()

    def get_download_summary_csv(self):
        '''
        return data summary in csv format
        '''
        output = io.StringIO()

        writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)

        writer.writerow(["Session ID", "Period", "Town", "Group", "Location", "Client #", "Label", "Good One Production", "Good One Production %", "Good Two Production", "Good Two Production %",
                         "Good One Consumption", "Good Two Consumption", "Earnings ¢"])

        session_player_periods = main.models.SessionPlayerPeriod.objects.filter(session_player__in=self.session_players.all()) \
                                                                        .order_by('session_period__period_number', 
                                                                                  'session_player__parameter_set_player__town', 
                                                                                  'session_player__parameter_set_player__location')

        for p in session_player_periods.all():
            p.write_summary_download_csv(writer)

        return output.getvalue()
    
    def get_download_action_csv(self):
        '''
        return data actions in csv format
        '''
        output = io.StringIO()

        writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)

        writer.writerow(["Session ID", "Period", "Town", "Phase", "Time", "Group",  "Location", "Client #", "Label", "Action","Info", "Info (JSON)", "Timestamp"])

        session_player_chats = main.models.SessionPlayerChat.objects.filter(session_player__in=self.session_players.all())

        for p in session_player_chats.all():
            p.write_action_download_csv(writer)
        
        session_player_moves = main.models.SessionPlayerMove.objects.filter(session_player_source__in=self.session_players.all()) \
                                                                    .select_related("session_player_source") \
                                                                    .select_related("session_player_source__parameter_set_player") \
                                                                    .select_related("session_player_target") \
                                                                    .select_related("session_period") \
                                                                    .select_related("session_period__session")

        for p in session_player_moves.all():
            p.write_action_download_csv(writer)

        return output.getvalue()
    
    def get_download_recruiter_csv(self):
        '''
        return data recruiter in csv format
        '''
        output = io.StringIO()

        writer = csv.writer(output)

        session_players = self.session_players.all()

        for p in session_players:
            writer.writerow([p.student_id, p.earnings/100])

        return output.getvalue()
    
    def get_download_payment_csv(self):
        '''
        return data payments in csv format
        '''
        output = io.StringIO()

        writer = csv.writer(output)

        if not self.parameter_set.prolific_mode:
            writer.writerow(['Session ID', 'Name', 'Student ID', 'Client #','Study Subject ID', 'Earnings', 'Avatar'])
        else:
            writer.writerow(['Session ID', 'Prolific Session ID', 'Prolific Subject ID', 'Study Subject ID', 'Client #', 'Earnings', 'Avatar'])

        session_players = self.session_players.all()

        for p in session_players:
            writer.writerow([self.id, p.name, p.student_id, p.player_key, p.player_number, p.earnings/100, p.avatar.label if p.avatar else 'None'])

        return output.getvalue()

    def json(self):
        '''
        return json object of model
        '''
        
        chat = {}
        notices = {}
        for i in range(self.parameter_set.town_count):
            chat[str(i+1)] = [c.json_for_staff() for c in main.models.SessionPlayerChat.objects \
                                                       .filter(session_player__in=self.session_players.all())\
                                                       .filter(session_player__parameter_set_player__town=i+1)
                                                       .prefetch_related('session_player_recipients')
                                                       .select_related('session_player__parameter_set_player')
                                                       .order_by('-timestamp')[:100:-1]
                             ]

            notices[str(i+1)] = [n.json() for n in main.models.SessionPlayerNotice.objects \
                                                       .filter(session_player__in=self.session_players.all()) \
                                                       .filter(session_player__parameter_set_player__town=i+1) \
                                                       .filter(show_on_staff=True) \
                                                       .order_by('-timestamp')[:100:-1]    
                                ]                                               
                             

        return{
            "id":self.id,
            "title":self.title,
            "locked":self.locked,
            "start_date":self.get_start_date_string(),
            "started":self.started,
            "id_string":self.id_string,
            "current_experiment_phase":self.current_experiment_phase,
            "current_period":self.current_period,
            "current_period_phase":self.current_period_phase,
            "time_remaining":self.time_remaining,
            "timer_running":self.timer_running,
            "finished":self.finished,
            "parameter_set":self.parameter_set.json(),
            "session_periods":[i.json() for i in self.session_periods.all()],
            "session_players":[i.json(False) for i in self.session_players.all()],
            "chat_all" : chat,
            "notices" : notices,
            "invitation_text" : self.invitation_text,
            "invitation_subject" : self.invitation_subject,
            "autarky_efficiency" : self.parameter_set.get_autarky_efficiency(),
        }
    
    def json_min(self):
        '''
        return json object of model
        '''
        return{
            "id":self.id,
            "title":self.title,
            "start_date":self.get_start_date_string(),
            "started":self.started,
            "current_experiment_phase":self.current_experiment_phase,
            "current_period":self.current_period,
            "current_period_phase":self.current_period_phase,
            "time_remaining":self.time_remaining,
            "timer_running":self.timer_running,
            "finished":self.finished,
            "parameter_set":self.parameter_set.json(),
        }
    
    def json_for_subject(self, session_player):
        '''
        json object for subject screen
        session_player : SessionPlayer() : session player requesting session object
        '''
        
        return{
            "started":self.started,
            "current_experiment_phase":self.current_experiment_phase,
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

        session_players = []

        #send update each second during production
        if self.current_period_phase == PeriodPhase.PRODUCTION:
            session_players = [i.json_min() for i in self.session_players.all()]

        #if groups have changed this period send a group update
        if self.time_remaining==self.parameter_set.period_length_production and \
           self.current_period_phase == PeriodPhase.PRODUCTION :
           
           do_group_update = False

           for i in self.session_players.all():
               if i.get_group_changed_this_period():
                   do_group_update = True
                   break

        else:
            do_group_update = False

        return{
            "started":self.started,
            "current_period":self.current_period,
            "current_period_phase":self.current_period_phase,
            "time_remaining":self.time_remaining,
            "timer_running":self.timer_running,
            "finished":self.finished,
            "session_players":session_players,
            "do_group_update" : do_group_update,
            "session_player_earnings": [i.json_earning() for i in self.session_players.all()]
        }

    def json_for_group_update(self):
        '''
        return list of groups
        '''   

        return [{"id" : p.id, "group_number" : p.get_current_group_number()} for p in self.session_players.all()]
        
@receiver(post_delete, sender=Session)
def post_delete_parameterset(sender, instance, *args, **kwargs):
    '''
    use signal to delete associated parameter set
    '''
    if instance.parameter_set:
        instance.parameter_set.delete()

@receiver(post_save, sender=Session)
def post_save_session(sender, instance, created, *args, **kwargs):
    '''
    after session is initialized
    '''
    if created:
        id_string = ''.join(random.choices(string.ascii_lowercase, k=6))

        while Session.objects.filter(id_string=id_string).exists():
            id_string = ''.join(random.choices(string.ascii_lowercase, k=6))

        instance.id_string = id_string
        instance.save()
