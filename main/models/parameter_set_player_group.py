'''
session player group parameters 
'''

from django.db import models

from main.models import ParameterSetPlayer

class ParameterSetPlayerGroup(models.Model):
    '''
    session player group parameters 
    '''

    parameter_set_player = models.ForeignKey(ParameterSetPlayer, on_delete=models.CASCADE, related_name="parameter_set_player_groups")

    group_number = models.IntegerField(verbose_name='Group Number (1-24)', default=1)        #group number 1 - N
    period = models.IntegerField(verbose_name='Period', default=1)                    #period number 1 - N

    timestamp = models.DateTimeField(auto_now_add= True)
    updated= models.DateTimeField(auto_now= True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Parameter Set Player Group'
        verbose_name_plural = 'Parameter Set Player Groups'
        ordering = ['period']
        constraints = [
            models.UniqueConstraint(fields=['parameter_set_player', 'period'], name='unique_player_period_group'),
        ]

    def from_dict(self, source):
        '''
        copy source values into this period
        source : dict object of period
        '''
        
        message = "Parameters loaded successfully."

        self.group_number = source.get("group_number")
        self.period = source.get("period")

        self.save()

        return message

    def json(self):
        '''
        return json object of model
        '''

        return{
            "id" : self.id,
            "group_number" : self.group_number,
            "period" : self.period,
        }
