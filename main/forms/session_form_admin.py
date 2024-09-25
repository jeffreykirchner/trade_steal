from django import forms
from main.models import Session
from django.contrib.auth.models import User
from django.forms import ModelChoiceField
from django.forms import ModelMultipleChoiceField


class UserModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.email

class UserModelMultipleChoiceField(ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.email

class SessionFormAdmin(forms.ModelForm):

    # parameter_set = models.ForeignKey(ParameterSet, on_delete=models.CASCADE)
    # creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # collaborators = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="session_collaborators")

    # title = models.CharField(max_length = 300, default="*** New Session ***")    #title of session
    # start_date = models.DateField(default=now)                                   #date of session start

    # channel_key = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name = 'Channel Key')     #unique channel to communicate on
    # session_key = models.UUIDField(default=uuid.uuid4, editable=False, verbose_name = 'Session Key')     #unique key for session to auto login subjects by id

    # started =  models.BooleanField(default=False)                                #starts session and filll in session
    # current_period = models.IntegerField(default=0)                              #current period of the session
    # current_period_phase = models.CharField(max_length=100, choices=PeriodPhase.choices, default=PeriodPhase.PRODUCTION)         #current phase of current period
    # time_remaining = models.IntegerField(default=0)                              #time remaining in current phase of current period
    # timer_running = models.BooleanField(default=False)                           #true when period timer is running
    # finished = models.BooleanField(default=False)                                #true after all session periods are complete

    # shared = models.BooleanField(default=False)                                  #shared session parameter sets can be imported by other users
    # locked = models.BooleanField(default=False)                                  #locked models cannot be deleted

    # soft_delete =  models.BooleanField(default=False)                            #hide session if true


    creator =  UserModelChoiceField(label="Creator",
                                     empty_label=None,
                                     queryset=User.objects.all(),
                                     widget=forms.Select(attrs={}))
    
    collaborators = UserModelMultipleChoiceField(label="Collaborators",
                                                 queryset=User.objects.all(),
                                                 required=False
                                                   )

    title = forms.CharField(label='Title',
                            widget=forms.TextInput(attrs={"size":"50"}))
    
    channel_key = forms.CharField(label='Channel Key',
                            widget=forms.TextInput(attrs={"size":"50"}))
    
    id_string = forms.CharField(label='ID String',
                            widget=forms.TextInput(attrs={"size":"6"}))
    
    shared = forms.BooleanField(label='Share parameterset with all.', required=False)
    locked = forms.BooleanField(label='Locked, prevent deletion.', required=False)
    soft_delete = forms.BooleanField(label='Soft Delete.', required=False)

    class Meta:
        model=Session
        fields = ('creator', 'collaborators', 'title', 'shared', 'locked', 'soft_delete', 'id_string')