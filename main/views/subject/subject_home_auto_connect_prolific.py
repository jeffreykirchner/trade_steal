'''
auto log subject in view
'''
import logging
import uuid

from django.db import transaction

from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.urls import reverse
from django.views import View

from main.models import Session

from main.globals import ExperimentPhase

class SubjectHomeAutoConnectProlificView(View):
    '''
    class based auto login for subject for Prolific
    '''
        
    def get(self, request, *args, **kwargs):
        '''
        handle get requests
        '''
        prolific_pid = request.GET.get('PROLIFIC_PID', None)
        prolific_session_id = request.GET.get('SESSION_ID', None)
        subject_id = request.GET.get('SUBJECT_ID', None)

        try:
            session = Session.objects.get(session_key=kwargs['session_key'])
        except ObjectDoesNotExist:
            raise Http404("Session not found.")

        try:
            with transaction.atomic():

                first_connect = False

                #check is subject already connected
                session_player = session.session_players.filter(student_id=prolific_pid).first()

                if not session_player:
                    if session.current_experiment_phase != ExperimentPhase.INSTRUCTIONS:
                        return HttpResponse("<br><br><center><h1>The session has already started.</h1></center>")
                    
                    first_connect = True
                    session_player = session.session_players.filter(connecting=False, connected_count=0).first()

                if session_player:
                    player_key = session_player.player_key
                else:
                    return HttpResponse("<br><br><center><h1>All connections are full.</h1></center>")
                
                if first_connect:
                    session_player.reset()

                session_player.connecting = True
                session_player.student_id = prolific_pid
                session_player.name = prolific_session_id

                session_player.save()

        except ObjectDoesNotExist:
            return HttpResponse("<br><br><center><h1>All connections are full.</h1></center>")
    

        return HttpResponseRedirect(reverse('subject_home', args=(player_key,)))