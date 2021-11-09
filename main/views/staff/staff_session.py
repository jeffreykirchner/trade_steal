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

from main.forms import SessionForm
from main.forms import SessionPlayerMoveForm

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

        session = self.get_object()

        session_player_move_form_ids=[]
        for i in SessionPlayerMoveForm():
            session_player_move_form_ids.append(i.html_name)

        return render(request=request,
                      template_name=self.template_name,
                      context={"channel_key" : uuid.uuid4(),
                               "id" : session.id,
                               "session_form" : SessionForm(),
                               "session_player_move_form" : SessionPlayerMoveForm(),
                               "session_player_move_form_ids" : session_player_move_form_ids,
                               "websocket_path" : self.websocket_path,
                               "page_key" : f'{self.websocket_path}-{session.id}',
                               "session" : session})
    
    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        '''
        handle post requests
        '''

        logger = logging.getLogger(__name__) 
        session = self.get_object()        

        return JsonResponse({"response" :  "fail"},safe=False)