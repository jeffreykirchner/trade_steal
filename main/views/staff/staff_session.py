'''
staff view
'''
import logging
import uuid
import json

from django.views import View
from django.shortcuts import render
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder

from main.decorators import user_is_owner

from main.models import Session
from main.models import Parameters

from main.forms import SessionForm
from main.forms import SessionPlayerMoveTwoForm
from main.forms import SessionPlayerMoveThreeForm

class StaffSessionView(SingleObjectMixin, View):
    '''
    class based staff view
    '''
    template_name = "staff/staff_session.html"
    websocket_path = "staff-session"
    model = Session
    
    @method_decorator(user_is_owner)
    @method_decorator(login_required)
    def get(self, request, *args, **kwargs):
        '''
        handle get requests
        '''
        
        parameters = Parameters.objects.first()

        session = self.get_object()

        session_player_move_two_form_ids=[]
        for i in SessionPlayerMoveTwoForm():
            session_player_move_two_form_ids.append(i.html_name)

        session_player_move_three_form_ids=[]
        for i in SessionPlayerMoveThreeForm():
            session_player_move_three_form_ids.append(i.html_name)


        return render(request=request,
                      template_name=self.template_name,
                      context={"channel_key" : session.channel_key,
                               "player_key" :  session.channel_key,
                               "avatar_sprite_sheet" : parameters.avatar_sprite_sheet,
                               "graph_sprite_sheet" : parameters.graph_sprite_sheet,
                               "id" : session.id,
                               "session_form" : SessionForm(),
                               "session_player_move_two_form" : SessionPlayerMoveTwoForm(),
                               "session_player_move_two_form_ids" : session_player_move_two_form_ids,
                               "session_player_move_three_form" : SessionPlayerMoveThreeForm(),
                               "session_player_move_three_form_ids" : session_player_move_three_form_ids,
                               "websocket_path" : self.websocket_path,
                               "town_count_range" : range(session.parameter_set.town_count),
                               "page_key" : f'session-{session.id}',
                               "parameters" : parameters,
                               "session" : session,
                               "session_json":json.dumps(session.json(), cls=DjangoJSONEncoder),
                               })
    
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        '''
        handle post requests
        '''

        logger = logging.getLogger(__name__) 
        session = self.get_object()        

        return JsonResponse({"response" :  "fail"},safe=False)