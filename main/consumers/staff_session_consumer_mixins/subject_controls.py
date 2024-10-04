
import logging
import re
import json

from asgiref.sync import sync_to_async

from django.urls import reverse
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder

from main.models import Session
from main.models import Parameters

from main.forms import StaffEditNameEtcForm

from main.globals import send_mass_email_service

class SubjectControlsMixin():
    '''
    subject controls mixin for staff session consumer
    '''

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