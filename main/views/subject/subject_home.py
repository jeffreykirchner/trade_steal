'''
staff view
'''
import logging
import uuid

from django.views import View
from django.shortcuts import render
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse

from main.decorators import user_is_owner

from main.models import Session
from main.models import SessionPlayer

from main.forms import SessionForm
from main.forms import SessionPlayerMoveTwoForm
from main.forms import SessionPlayerMoveThreeForm

class SubjectHomeView(View):
    '''
    class based staff view
    '''
    template_name = "subject/subject_home.html"
    websocket_path = "subject-home"
    
    def get(self, request, *args, **kwargs):
        '''
        handle get requests
        '''
        session_subject = SessionPlayer.objects.get(uuid=kwargs['subject_uuid'])
        session = session_subject.session

        session_player_move_two_form_ids=[]
        for i in SessionPlayerMoveTwoForm():
            session_player_move_two_form_ids.append(i.html_name)

        session_player_move_three_form_ids=[]
        for i in SessionPlayerMoveThreeForm():
            session_player_move_three_form_ids.append(i.html_name)

        return render(request=request,
                      template_name=self.template_name,
                      context={"channel_key" : session.channel_key,
                               "id" : session.id,
                               "session_form" : SessionForm(),
                               "session_player_move_two_form" : SessionPlayerMoveTwoForm(),
                               "session_player_move_two_form_ids" : session_player_move_two_form_ids,
                               "session_player_move_three_form" : SessionPlayerMoveThreeForm(),
                               "session_player_move_three_form_ids" : session_player_move_three_form_ids,
                               "websocket_path" : self.websocket_path,
                               "page_key" : f'session-{session.id}',
                               "session_subject" : session_subject,
                               "session" : session})
    
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        '''
        handle post requests
        '''

        logger = logging.getLogger(__name__) 
        session = self.get_object()        

        return JsonResponse({"response" :  "fail"},safe=False)