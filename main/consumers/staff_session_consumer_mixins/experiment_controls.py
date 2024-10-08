from asgiref.sync import sync_to_async

import logging
import json

from django.db import transaction
from django.core.serializers.json import DjangoJSONEncoder
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist

from main.globals import ExperimentPhase
from main.globals import send_mass_email_service
from main.globals import AvatarModes

import main

from main.models import Session
from main.models import Parameters

class ExperimentControlsMixin():
    '''
    This mixin is used to start an the experiment.
    '''

    async def start_experiment(self, event):
        '''
        start experiment
        '''
        result = await sync_to_async(take_start_experiment)(self.session_id, event["message_text"])

        if result["value"] == "fail":
            await self.send_message(message_to_self=result, message_to_group=None,
                                    message_type=event['type'], send_to_client=True, send_to_group=False)
        else:
            await self.send_message(message_to_self=None, message_to_group=result,
                                    message_type=event['type'], send_to_client=False, send_to_group=True)
    
    async def reset_experiment(self, event):
        '''
        reset experiment, removes all trades, bids and asks
        '''
        result = await sync_to_async(take_reset_experiment)(self.session_id, event["message_text"])

        if result["value"] == "fail":
            await self.send_message(message_to_self=result, message_to_group=None,
                                    message_type=event['type'], send_to_client=True, send_to_group=False)
        else:
            await self.send_message(message_to_self=None, message_to_group=result,
                                    message_type=event['type'], send_to_client=False, send_to_group=True)
    
    async def end_early(self, event):
        '''
        set the current period as the last period
        '''

        result = await sync_to_async(take_end_early)(self.session_id)

        await self.send_message(message_to_self=result, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

    async def reset_connections(self, event):
        '''
        reset connection counts for experiment
        '''

        result = await sync_to_async(take_reset_connections)(self.session_id, event["message_text"])

        if result["value"] == "fail":
            await self.send_message(message_to_self=result, message_to_group=None,
                                    message_type=event['type'], send_to_client=True, send_to_group=False)
        else:
            await self.send_message(message_to_self=None, message_to_group=result,
                                    message_type=event['type'], send_to_client=False, send_to_group=True)

    async def next_phase(self, event):
        '''
        advance to next phase in experiment
        '''
        result = await sync_to_async(take_next_phase)(self.session_id, event["message_text"])

        if result["value"] == "fail":
            await self.send_message(message_to_self=result, message_to_group=None,
                                    message_type=event['type'], send_to_client=True, send_to_group=False)
        else:
            await self.send_message(message_to_self=None, message_to_group=result,
                                    message_type=event['type'], send_to_client=False, send_to_group=True)
            
    async def send_invitations(self, event):
        '''
        send invitations to subjects
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_send_invitations)(self.session_id,  event["message_text"])

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def refresh_screens(self, event):
        '''
        refresh client and server screens
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_refresh_screens)(self.session_id,  event["message_text"])

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data


        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    
    #consumer updates
    async def update_start_experiment(self, event):
        '''
        start experiment on staff
        '''
        # logger = logging.getLogger(__name__) 
        # logger.info(f'update_goods{self.channel_name}')

        result = await sync_to_async(main.consumers.take_get_session)(self.connection_uuid)

        await self.send_message(message_to_self=result, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)
    
    async def update_reset_experiment(self, event):
        '''
        update reset experiment
        '''

        result = await sync_to_async(main.consumers.take_get_session)(self.connection_uuid)

        await self.send_message(message_to_self=result, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

    async def update_reset_connections(self, event):
        '''
        update reset experiment
        '''

        result = await sync_to_async(main.consumers.take_get_session)(self.connection_uuid)
 
        await self.send_message(message_to_self=result, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)
    
    async def update_next_phase(self, event):
        '''
        update session phase
        '''

        result = json.loads(event["group_data"])

        await self.send_message(message_to_self=result, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

   
def take_start_experiment(session_id, data):
    '''
    start experiment
    '''   

    logger = logging.getLogger(__name__) 
    logger.info(f"Start Experiment: {data}")

    #session_id = data["sessionID"]
    with transaction.atomic():
        session = Session.objects.get(id=session_id)

        if not session.started:
            session.start_experiment()

        value = "success"
    
    return {"value" : value, "started" : session.started}

def take_reset_experiment(session_id, data):
    '''
    reset experiment remove bids and asks
    '''   

    logger = logging.getLogger(__name__) 
    logger.info(f"Reset Experiment: {data}")

    #session_id = data["sessionID"]
    session = Session.objects.get(id=session_id)

    if session.started:
        session.reset_experiment()  

    value = "success"
    
    return {"value" : value, "started" : session.started}

def take_end_early(session_id):
    '''
    make the current period the last period
    '''

    session = Session.objects.get(id=session_id)

    session.parameter_set.period_count = session.current_period
    session.parameter_set.save()
    session.parameter_set.update_json_local()

    return {"value" : "success", "period_count" : session.parameter_set.period_count}

def take_reset_connections(session_id, data):
    '''
    reset connection counts for experiment
    '''   

    logger = logging.getLogger(__name__) 
    logger.info(f"Reset connection counts: {data}")

    #session_id = data["sessionID"]
    session = Session.objects.get(id=session_id)

    if not session.started:
        session.reset_connection_counts()  

    value = "success"
    
    return {"value" : value, "started" : session.started}

def take_next_phase(session_id, data):
    '''
    advance to next phase in the experiment
    '''   

    logger = logging.getLogger(__name__) 
    logger.info(f"Advance to Next Phase: {data}")

    #session_id = data["sessionID"]
    session = Session.objects.get(id=session_id)
    period_update = None

    if session.current_experiment_phase == ExperimentPhase.SELECTION:
        session.current_experiment_phase = ExperimentPhase.RUN
        
    elif session.current_experiment_phase == ExperimentPhase.INSTRUCTIONS:
        
        if session.parameter_set.avatar_assignment_mode == AvatarModes.SUBJECT_SELECT or \
           session.parameter_set.avatar_assignment_mode == AvatarModes.BEST_MATCH :

            session.current_experiment_phase = ExperimentPhase.SELECTION
        else:
            session.current_experiment_phase = ExperimentPhase.RUN

    elif session.current_experiment_phase == ExperimentPhase.RUN:
        session.current_experiment_phase = ExperimentPhase.DONE
        period_update = session.get_current_session_period()

    session.save()

    status = "success"
    
    return {"value" : status,
            "period_update" : period_update.json() if period_update else None,
            "current_experiment_phase" : session.current_experiment_phase,
            }

def take_send_invitations(session_id, data):
    '''
    send login link to subjects in session
    '''
    logger = logging.getLogger(__name__)
    logger.info(f'take_send_invitations: {session_id} {data}')

    try:        
        session = Session.objects.get(id=session_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_send_invitations session, not found: {session_id}")
        return {"status":"fail", "result":"session not found"}

    p = Parameters.objects.first()
    message = data["formData"]

    session.invitation_text =  message["text"]
    session.invitation_subject =  message["subject"]
    session.save()

    message_text =session.invitation_text
    message_text = message_text.replace("[contact email]", p.contact_email)

    user_list = []
    for session_subject in session.session_players.exclude(email=None).exclude(email=""):
        user_list.append({"email" : session_subject.email,
                          "variables": [{"name" : "log in link",
                                         "text" : p.site_url + reverse('subject_home', kwargs={'player_key': session_subject.player_key})
                                        }] 
                         })

    memo = f'Trade Steal: Session {session_id}, send invitations'

    result = send_mass_email_service(user_list, session.invitation_subject, message_text , message_text, memo)

    return {"value" : "success",
            "result" : {"email_result" : result,
                        "invitation_subject" : session.invitation_subject,
                        "invitation_text" : session.invitation_text }}

def take_refresh_screens(session_id, data):
    '''
    refresh screen
    '''
    logger = logging.getLogger(__name__)
    # logger.info(f'refresh screen: {session_id} {data}')

    try:        
        session = Session.objects.get(id=session_id)
        session.parameter_set.json(update_required=True)

    except ObjectDoesNotExist:
        logger.warning(f"take_refresh_screens session not found: {session_id}")
        return {"status":"fail", 
                "message":"Session not found",
                "result":{}}

    return {"session" : session.json()}

