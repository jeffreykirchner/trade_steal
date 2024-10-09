'''
websocket session list
'''
from asgiref.sync import sync_to_async

import json
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder

from main.consumers import SocketConsumerMixin
from main.consumers import StaffSubjectUpdateMixin

from main.forms import SessionForm

from main.models import Session

from .staff_session_consumer_mixins import *

from .send_message_mixin import SendMessageMixin

class StaffSessionConsumer(SocketConsumerMixin, 
                           StaffSubjectUpdateMixin,
                           SendMessageMixin,
                           DataMixin,
                           TimerMixin,
                           SubjectControlsMixin,
                           SubjectUpdatesMixin,
                           ExperimentControlsMixin):
    '''
    websocket session list
    '''    

    has_timer_control = False
    timer_running = False
        
    async def get_session(self, event):
        '''
        return a list of sessions
        '''
        # logger = logging.getLogger(__name__) 
        # logger.info(f"Get Session {event}")

        self.connection_uuid = event["message_text"]["sessionKey"]
        self.connection_type = "staff"

        #build response
        result = await sync_to_async(take_get_session)(self.connection_uuid)       

        self.session_id = result["session"]["id"]
        self.timer_running = result["session"]["timer_running"]

        await self.send_message(message_to_self=result, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)
    
    async def update_session(self, event):
        '''
        return a list of sessions
        '''
        # logger = logging.getLogger(__name__) 
        # logger.info(f"Update Session: {event}")

        result =  await sync_to_async(take_update_session_form)(self.session_id, event["message_text"])

        await self.send_message(message_to_self=result, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

    async def update_survey_complete(self, event):
        '''
        send survey complete update
        '''
        message_data = {}
        message_data["status"] = event["data"]

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, 
                        cls=DjangoJSONEncoder))
        
    async def update_set_controlling_channel(self, event):
        '''
        update controlling channel
        '''
        event_data = event["data"]
        self.controlling_channel = event_data["controlling_channel"]
#local async function

#local sync functions    
def take_get_session(session_key):
    '''
    return session with specified id
    param: session_key {uuid} session uuid
    '''
    session = None
    logger = logging.getLogger(__name__)

    # try:        
    session = Session.objects.get(session_key=session_key)
    return {"session" : session.json()}
    # except ObjectDoesNotExist:
    #     logger.warning(f"staff get_session session, not found: {session_key}")
    #     return {}

def take_update_session_form(session_id, data):
    '''
    take session form data and update session or return errors
    param: data {json} incoming form and session data
    '''

    logger = logging.getLogger(__name__)
    logger.info(f'take_update_session_form: {data}')

    #session_id = data["sessionID"]
    form_data = data["formData"]

    try:        
        session = Session.objects.get(id=session_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_update_session_form session, not found: {session_id}")
    
    form_data_dict = form_data

    form = SessionForm(form_data_dict, instance=session)

    if form.is_valid():
        #print("valid form")                
        form.save()              

        return {"value":"success", "session" : session.json()}                      
                                
    logger.info("Invalid session form")
    return {"value":"fail", "errors":dict(form.errors.items())}





    
