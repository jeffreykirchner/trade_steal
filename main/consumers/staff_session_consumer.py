'''
websocket session list
'''
from asgiref.sync import sync_to_async

import json
import logging
import re

from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
from django.db.utils import IntegrityError
from channels.layers import get_channel_layer

from main.consumers import SocketConsumerMixin
from main.consumers import StaffSubjectUpdateMixin

from main.forms import SessionForm
from main.forms import StaffEditNameEtcForm

from main.models import Session
from main.models import SessionPlayer
from main.models import Parameters

from .staff_session_consumer_mixins import *

class StaffSessionConsumer(SocketConsumerMixin, 
                           StaffSubjectUpdateMixin,
                           DataMixin,
                           TimerMixin,
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
        message_data = {}
        message_data["session"] = await sync_to_async(take_get_session)(self.connection_uuid)       

        self.session_id = message_data["session"]["id"]
        self.timer_running = message_data["session"]["timer_running"]

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message,}, cls=DjangoJSONEncoder))
    
    async def update_session(self, event):
        '''
        return a list of sessions
        '''
        # logger = logging.getLogger(__name__) 
        # logger.info(f"Update Session: {event}")

        #build response
        message_data = {}
        message_data =  await sync_to_async(take_update_session_form)(self.session_id, event["message_text"])

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
            

    async def update_subject(self, event):
        '''
        set the name etc info of a subjec from staff screen
        '''

        result = await sync_to_async(take_update_subject)(self.session_id,  event["message_text"])

        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "update_update_subject",
             "data": result,
             "sender_channel_name": self.channel_name,},
        )
    
    async def email_list(self, event):
        '''
        take csv email list and load in to session players
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_email_list)(self.session_id,  event["message_text"])

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def anonymize_data(self, event):
        '''
        send invitations to subjects
        '''

        result = await sync_to_async(take_anonymize_data)(self.session_id,  event["message_text"])

        #update all 
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "update_anonymize_data",
             "data": result,
             "sender_channel_name": self.channel_name,},
        )
        
    async def update_chat(self, event):
        '''
        send chat to clients, if clients can view it
        '''
        result = event["staff_result"]

        message_data = {}
        message_data["status"] = result

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def update_move_goods(self, event):
        '''
        update good count staff
        '''
        # logger = logging.getLogger(__name__) 
        # logger.info(f'update_goods{self.channel_name}')

        message_data = {}
        message_data["status"] = event["data"]

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    

    async def update_groups(self, event)  :
        '''
        update groups on client
        '''

        result = await sync_to_async(take_update_groups)(self.session_id)

        message_data = {}
        message_data["status"] = result

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def update_connection_status(self, event):
        '''
        handle connection status update from group member
        '''
        # logger = logging.getLogger(__name__) 
        # logger.info("Connection update")

        #update not from a client
        if event["data"]["value"] == "fail":
            return

        message_data = {}
        message_data["status"] = event["data"]

        #get subject name and student id
        subject_id = message_data["status"]["result"]["id"]

        session_player = await SessionPlayer.objects.aget(id=subject_id)
        message_data["status"]["result"]["name"] = session_player.name
        message_data["status"]["result"]["student_id"] = session_player.student_id
        message_data["status"]["result"]["current_instruction"] = session_player.current_instruction
        message_data["status"]["result"]["survey_complete"] = session_player.survey_complete
        message_data["status"]["result"]["instructions_finished"] = session_player.instructions_finished

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def update_name(self, event):
        '''
        send update name notice to staff screens
        '''

        # logger = logging.getLogger(__name__) 
        # logger.info("Eng game update")

        message_data = {}
        message_data["status"] = event["data"]

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def update_avatar(self, event):
        '''
        send update avatar notice to staff screens
        '''

        # logger = logging.getLogger(__name__) 
        # logger.info("Eng game update")

        message_data = {}
        message_data["status"] = event["data"]

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def update_next_instruction(self, event):
        '''
        send instruction status to staff
        '''

        # logger = logging.getLogger(__name__) 
        # logger.info("Eng game update")

        message_data = {}
        message_data["status"] = event["data"]

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def update_finish_instructions(self, event):
        '''
        send instruction status to staff
        '''

        # logger = logging.getLogger(__name__) 
        # logger.info("Eng game update")

        message_data = {}
        message_data["status"] = event["data"]

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def update_production_time(self, event):
        '''
        send production settings update
        '''

        # logger = logging.getLogger(__name__) 
        # logger.info("Eng game update")

        message_data = {}
        message_data["status"] = event["data"]

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def update_anonymize_data(self, event):
        '''
        send anonymize data update to staff sessions
        '''

        # logger = logging.getLogger(__name__) 
        # logger.info("Eng game update")

        message_data = {}
        message_data["status"] = event["data"]

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def update_update_subject(self, event):
        '''
        send anonymize data update to staff sessions
        '''

        # logger = logging.getLogger(__name__) 
        # logger.info("Eng game update")

        message_data = {}
        message_data["status"] = event["data"]

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
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
    return session.json()
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

        return {"status":"success", "session" : session.json()}                      
                                
    logger.info("Invalid session form")
    return {"status":"fail", "errors":dict(form.errors.items())}

def take_update_groups(session_id):
    '''
    take update groups
    '''

    session = Session.objects.get(id=session_id)

    status = "success"
    
    return {"status" : status,
            "group_list" : session.json_for_group_update()}


def take_update_subject(session_id, data):
    '''
    take update subject info from staff screen
    param: data {json} incoming form and session data
    '''

    logger = logging.getLogger(__name__)
    logger.info(f'take_update_subject: {data}')

    #session_id = data["sessionID"]
    form_data = dict(data["formData"])

    try:        
        session = Session.objects.get(id=session_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_update_session_form session, not found: {session_id}")
        return {"status":"fail", "message":"session not found"}

    form = StaffEditNameEtcForm(form_data)

    if form.is_valid():

        session_player = session.session_players.get(id=form_data["id"])
        session_player.name = form.cleaned_data["name"]
        session_player.student_id = form.cleaned_data["student_id"]
        session_player.email = form.cleaned_data["email"]
        
        try:
            session_player.save()              
        except IntegrityError as e:
            return {"value":"fail", "errors" : {f"email":["Email must be unique within session."]}}  

        return {"value":"success",
                "session_player" : {"id":session_player.id,
                                    "name":session_player.name, 
                                    "student_id":session_player.student_id,
                                    "email":session_player.email}}                      
                                
    logger.info("Invalid session form")
    return {"status":"fail", "errors":dict(form.errors.items())}



def take_email_list(session_id, data):
    '''
    take uploaded csv server from list and load emails into session players
    '''

    logger = logging.getLogger(__name__)
    logger.info(f'take_email_list: {session_id} {data}')

    try:        
        session = Session.objects.get(id=session_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_send_invitations session, not found: {session_id}")
        return {"value":"fail", "result":"session not found"}
    
    raw_list = data["csv_data"]

    raw_list = raw_list.splitlines()

    for i in range(len(raw_list)):
        raw_list[i] =  re.split(r',|\t', raw_list[i])
    
    u_list = []

    if not session.parameter_set.prolific_mode:
        for i in raw_list:
            for j in i:
                if "@" in j:
                    u_list.append(j)
        
        if len(u_list)>0:
            session.session_players.update(email=None)

        for i in u_list:
            p = session.session_players.filter(email=None).first()

            if(p):
                p.email = i
                p.save()
            else:
                break
    else:
        for i in raw_list:
            for j in i:
                u_list.append(j)

        if len(u_list)>0:
            session.session_players.update(student_id="")
        
        for i in u_list:
            p = session.session_players.filter(student_id='').first()

            if(p):
                p.student_id = i
                p.save()
            else:
                break
    
    result = []
    for p in session.session_players.all():
        result.append({"id" : p.id, "email" : p.email,  "student_id" : p.student_id})
    
    return {"value" : "success",
            "result" : result}

def take_anonymize_data(session_id, data):
    '''
    remove name, email and student id from the data
    '''

    logger = logging.getLogger(__name__)
    logger.info(f'take_email_list: {session_id} {data}')

    try:        
        session = Session.objects.get(id=session_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_anonymize_data session, not found: {session_id}")
        return {"value":"fail", "result":"session not found"}

    result = {}

    session.session_players.all().update(name="---", student_id="---", email="")

    result = session.session_players.all().values('id', 'name', 'student_id', 'email')
    
    return {"value" : "success",
            "result" : list(result)}


    
