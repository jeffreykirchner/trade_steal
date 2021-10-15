'''
paramters model form
'''
import pytz

from django import forms
from django.forms import ModelChoiceField

from main.models import Parameters

class ParametersForm(forms.ModelForm):
    '''
    paramters model form
    '''
    contact_email = forms.CharField(label='Contact Email Address',
                                    widget=forms.TextInput(attrs={"size":"125"}))

    site_url = forms.CharField(label='Site URL',
                               widget=forms.TextInput(attrs={"size":"125"}))

    experiment_time_zone = forms.ChoiceField(label="Study Timezone",
                                             choices=[(tz, tz) for tz in pytz.all_timezones])

    channel_key = forms.CharField(label='Socket channel for general site.',
                                  widget=forms.TextInput(attrs={"size":"125"}))

    class Meta:
        model=Parameters
        fields = ('__all__')
