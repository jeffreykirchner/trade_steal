'''
parameter type settings
'''
from decimal import Decimal

from django.db import models
from django.db.utils import IntegrityError

from main.models import ParameterSet
from main.globals import SubjectType

import main

class ParameterSetType(models.Model):
    '''
    parameter set type
    '''

    parameter_set = models.ForeignKey(ParameterSet, on_delete=models.CASCADE,  related_name="parameter_set_types")
    
    subject_type = models.CharField(max_length=100, choices=SubjectType.choices, default=SubjectType.ONE)         #type of subject
     
    good_one_amount =  models.IntegerField(verbose_name='Good One Amount', default=1)         #amount of good one needed to earn 1 cent
    good_two_amount =  models.IntegerField(verbose_name='Good Two Amount', default=1)         #amount of good two needed to earn 1 cent

    good_one_production_1 = models.DecimalField(verbose_name = 'Good One Production Parameter 1', decimal_places=9, default=0, max_digits=10)
    good_one_production_2 = models.DecimalField(verbose_name = 'Good One Production Parameter 2', decimal_places=9, default=0, max_digits=10)
    good_one_production_3 = models.DecimalField(verbose_name = 'Good One Production Parameter 3', decimal_places=9, default=0, max_digits=10)

    good_two_production_1 = models.DecimalField(verbose_name = 'Good Two Production Parameter 1', decimal_places=9, default=0, max_digits=10)
    good_two_production_2 = models.DecimalField(verbose_name = 'Good Two Production Parameter 2', decimal_places=9, default=0, max_digits=10)
    good_two_production_3 = models.DecimalField(verbose_name = 'Good Two Production Parameter 3', decimal_places=9, default=0, max_digits=10)

    timestamp = models.DateTimeField(auto_now_add= True)
    updated= models.DateTimeField(auto_now= True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Parameter Set Type'
        verbose_name_plural = 'Parameter Set Types'
        constraints = [
            models.UniqueConstraint(fields=['parameter_set', 'subject_type'], name='unique_player_type'),
        ]
        ordering = ['id']


    def from_dict(self, source):
        '''
        copy source values into this
        source : dict object of this
        '''
        
        message = "Parameters loaded successfully."

        self.subject_type = source.get("subject_type")

        self.good_one_amount = source.get("good_one_amount")
        self.good_two_amount = source.get("good_two_amount")

        self.good_one_production_1 = source.get("good_one_production_1")
        self.good_one_production_2 = source.get("good_one_production_2")
        self.good_one_production_3 = source.get("good_one_production_3")
        
        self.good_two_production_1 = source.get("good_two_production_1")
        self.good_two_production_2 = source.get("good_two_production_2")
        self.good_two_production_3 = source.get("good_two_production_3")

        self.save()

        return message


    def json(self):
        '''
        return json object of model
        '''

        return{

            "id" : self.id,
            "subject_type" : self.subject_type,
            "good_one_amount" : self.good_one_amount,
            "good_two_amount" : self.good_two_amount,

            "good_one_production_1" : self.good_one_production_1.normalize(),
            "good_one_production_2" : self.good_one_production_2.normalize(),
            "good_one_production_3" : self.good_one_production_3.normalize(),

            "good_two_production_1" : self.good_two_production_1.normalize(),
            "good_two_production_2" : self.good_two_production_2.normalize(),
            "good_two_production_3" : self.good_two_production_3.normalize(),
        }
