'''
session player notice
'''

#import logging

from django.db import models
from django.db.models import Q

from main.models import SessionPlayer
from main.models import SessionPeriod

class SessionPlayerNotice(models.Model):
    '''
    session player notice model
    '''
    session_period = models.ForeignKey(SessionPeriod, on_delete=models.CASCADE, related_name="session_player_notices_a")
    session_player = models.ForeignKey(SessionPlayer, on_delete=models.CASCADE, related_name="session_player_notices_b")

    text = models.CharField(max_length = 1000, default="", verbose_name="Notice Text")                 #notice text
    show_on_staff = models.BooleanField(default=False, verbose_name = 'Show Notice on Staff Screen')   #if true, show notice on staff screen as well as subject screen 

    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id}"

    class Meta:
        
        verbose_name = 'Session Player Notice'
        verbose_name_plural = 'Session Player Notice'
        ordering = ['timestamp']
        constraints = [
             models.CheckConstraint(check=~Q(text=''), name='notice_text_not_empty'),
        ]

    def json(self):
        '''
        json object of model
        '''

        return{
            "id" : self.id,   
            "session_player_id" : self.session_player.id, 
            "text" : self.text,  
            "show_on_staff" : self.show_on_staff,
            "session_player_label" : self.session_player.parameter_set_player.id_label,
        }