'''
session player parameters 
'''

from django.db import models

from main.models import ParameterSet

from main.globals import SubjectType

import main

class ParameterSetPlayer(models.Model):
    '''
    session player parameters 
    '''

    parameter_set = models.ForeignKey(ParameterSet, on_delete=models.CASCADE, related_name="parameter_set_players")

    subject_type = models.CharField(max_length=100, choices=SubjectType.choices, default=SubjectType.ONE)         #type of subject

    id_label = models.CharField(verbose_name='ID Label', max_length = 2, default="1")      #id label shown on screen to subjects
    location = models.IntegerField(verbose_name='Location number (1-8)', default=1)        #location number of 1 to 8
    
    timestamp = models.DateTimeField(auto_now_add= True)
    updated= models.DateTimeField(auto_now= True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Parameter Set Player'
        verbose_name_plural = 'Parameter Set Players'
        ordering = ['location']

    def from_dict(self, source):
        '''
        copy source values into this period
        source : dict object of period
        '''
        
        message = "Parameters loaded successfully."

        self.subject_type = source.get("subject_type")
        self.id_label = source.get("id_label")
        self.location = source.get("location")

        self.save()

        new_period_groups = source.get("period_groups")
        for g in new_period_groups:
            parameter_set_player_group = self.parameter_set_player_groups.get(period=g["period"])
            parameter_set_player_group.group_number = g["group_number"]
            parameter_set_player_group.save()

        return message

    def update_group_period_count(self, count):
        '''
        when period count changes update group with default 1 if needed
        '''

        current_groups = self.parameter_set_player_groups.all()


        if len(current_groups)<count:
            # add more player groups

            for i in range(len(current_groups)+1, count+1):
                new_group = main.models.ParameterSetPlayerGroup()

                new_group.parameter_set_player = self
                new_group.group_number = 1
                new_group.period = i

                new_group.save()

        elif len(current_groups)>count:
            #remove excess groups
            main.models.ParameterSetPlayerGroup.objects.filter(parameter_set_player=self,
                                                               period__gt=count) \
                                                        .delete() 

    def copy_group_foward(self, period_number):
        '''
        copy group from the specified period to future periods
        '''

        source_group_number = self.parameter_set_player_groups.get(period=period_number).group_number
        self.parameter_set_player_groups.filter(period__gt=period_number).update(group_number=source_group_number)
    
    def json(self):
        '''
        return json object of model
        '''

        return{

            "id" : self.id,
            "id_label" : self.id_label,
            "location" : self.location,
            "subject_type" : self.subject_type,
            "period_groups" : [g.json() for g in self.parameter_set_player_groups.all()],
        }
