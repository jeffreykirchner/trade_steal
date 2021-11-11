'''
parameter set good settings
'''

from django.db import models

from main.models import ParameterSet

class ParameterSetGood(models.Model):
    '''
    parameter set good settings
    '''
    parameter_set = models.ForeignKey(ParameterSet, on_delete=models.CASCADE,  related_name="parameter_set_goods")

    label =  models.CharField(verbose_name='Good One Label', max_length = 10, default="Orange")     #label for good 
    rgb_color =  models.CharField(verbose_name='Good One RGB Color', max_length = 10, default="#FF5733")      #rgb color of good a   
    
    timestamp = models.DateTimeField(auto_now_add= True)
    updated= models.DateTimeField(auto_now= True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'Parameter Set Good'
        verbose_name_plural = 'Parameter Set Goods'
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(fields=['label'], name='unique_good_label'),
            models.UniqueConstraint(fields=['rgb_color'], name='unique_good_color'),
        ]

    def from_dict(self, source):
        '''
        copy source values into this
        source : dict object of this
        '''
        
        message = "Parameters loaded successfully."

        self.label = source.get("label")
        self.rgb_color = source.get("rgb_color")
        
        self.save()

        return message


    def json(self):
        '''
        return json object of model
        '''

        return{
            "id" : self.id,
            "label" : self.label,
            "rgb_color" : self.rgb_color,
        }
