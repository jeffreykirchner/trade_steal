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

    label =  models.CharField(verbose_name='Good Label', max_length = 10, default="Orange")     #label for good 
    abbreviation = models.CharField(verbose_name='Good Abbreviation', max_length = 2, blank=True, null=True)     #abbreviation for good
    rgb_color =  models.CharField(verbose_name='Good RGB Color', max_length = 10, default="#FF5733")      #rgb color of good a   
    
    timestamp = models.DateTimeField(auto_now_add= True)
    updated= models.DateTimeField(auto_now= True)

    def __str__(self):
        return self.label

    class Meta:
        verbose_name = 'Parameter Set Good'
        verbose_name_plural = 'Parameter Set Goods'
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(fields=['parameter_set', 'label'], name='unique_parameter_set_good_label'),
            models.UniqueConstraint(fields=['parameter_set', 'abbreviation'], name='unique_parameter_set_good_abbreviation'),
            models.UniqueConstraint(fields=['parameter_set', 'rgb_color'], name='unique_parameter_set_good_rgb'),
        ]

    def from_dict(self, source, parameter_set_goods_pk_map):
        '''
        copy source values into this
        source : dict object of this
        '''
        
        message = "Parameters loaded successfully."

        self.label = source.get("label")
        self.abbreviation = source.get("abbreviation")
        self.rgb_color = source.get("rgb_color")
        
        self.save()

        parameter_set_goods_pk_map[source.get("id")] = self.id

        return message


    def get_html(self):
        '''
        return html object of model
        '''
        return f"<span style='color:{self.rgb_color}'>{self.label}</span>"

    def json(self):
        '''
        return json object of model
        '''

        return{
            "id" : self.id,
            "label" : self.label,
            "abbreviation" : self.abbreviation,
            "rgb_color" : self.rgb_color,
        }
