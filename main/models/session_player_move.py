'''
session player move goods
'''

#import logging

from django.db import models
from django.db.models import Q
from django.db.models import F

from main.models import SessionPlayer, parameter_set
from main.models import SessionPeriod

from main.globals import ContainerTypes
from main.globals import PeriodPhase

class SessionPlayerMove(models.Model):
    '''
    session player move model
    '''
    session_period = models.ForeignKey(SessionPeriod, on_delete=models.CASCADE, related_name="session_player_moves_a")

    session_player_source = models.ForeignKey(SessionPlayer, on_delete=models.CASCADE, related_name="session_player_moves_b")
    session_player_target = models.ForeignKey(SessionPlayer, on_delete=models.CASCADE, related_name="session_player_moves_c")

    good_one_amount = models.IntegerField(verbose_name='Good one amount')        #amount of good one to be moved
    good_two_amount = models.IntegerField(verbose_name='Good two amount')        #amount of good two to be moved
    good_three_amount = models.IntegerField(verbose_name='Good three amount')        #amount of good two to be moved
    
    source_container = models.CharField(max_length=100, choices=ContainerTypes.choices, verbose_name='Source Container')         #source container
    target_container = models.CharField(max_length=100, choices=ContainerTypes.choices, verbose_name='Target Container')         #target container

    time_remaining = models.IntegerField(verbose_name='Good one amount', default=0)                                              #amount time left in period when move made
    current_period_phase = models.CharField(max_length=100, choices=PeriodPhase.choices, default=PeriodPhase.PRODUCTION)         #phase when move was made

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
            models.CheckConstraint(check=~Q(Q(session_player_source=F('session_player_target')) &
                                            Q(source_container=F('target_container'))), name='source_equals_target'),
        ]

    def write_action_download_csv(self, writer):
        '''
        take csv writer and add row
        '''        
        #  writer.writerow(["Period", "Town", "Phase", "Time", "Group", "Location", "Client #", "Label", "Action","Info", "Info (JSON)", "Timestamp"])

        writer.writerow([self.session_period.period_number,
                        self.session_player_source.parameter_set_player.town,
                        self.current_period_phase,
                        self.time_remaining,
                        self.session_player_source.get_group_number(self.session_period.period_number),
                        self.session_player_source.parameter_set_player.location,
                        self.session_player_source.player_number,
                        self.session_player_source.parameter_set_player.id_label,
                        "Move",
                        f'P{self.session_player_source.player_number}->P{self.session_player_target.player_number} | ' +
                           f'{self.source_container}->{self.target_container} | ' +
                           f'{self.good_one_amount} {self.session_player_source.parameter_set_player.good_one} and {self.good_two_amount} {self.session_player_source.parameter_set_player.good_two}',
                        self.json_csv(),
                        self.timestamp])

    def json_csv(self):
        '''
        json object for csv download
        '''
        return{
            "id" : self.id,         

            "session_player_source_client_number" : self.session_player_source.player_number,
            "session_player_target_client_number" : self.session_player_target.player_number,

            "good_one_amount" : self.good_one_amount,
            "good_two_amount" : self.good_two_amount,

            "good_one_amount_type" : self.session_player_source.parameter_set_player.good_one.label,
            "good_two_amount_type" : self.session_player_source.parameter_set_player.good_two.label,

            "source_container" : self.source_container,
            "target_container" : self.target_container,
        }


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
        