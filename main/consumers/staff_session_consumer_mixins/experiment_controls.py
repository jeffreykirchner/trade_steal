from asgiref.sync import sync_to_async

import logging
import json

from django.db import transaction
from django.core.serializers.json import DjangoJSONEncoder
from main.globals import ExperimentPhase

import main

from main.models import Session

# from ...consumers import take_get_session

class ExperimentControlsMixin():
    '''
    This mixin is used to start an the experiment.
    '''

    async def start_experiment(self, event):
        '''
        start experiment
        '''
        message_data = {}
        message_data["status"] = await sync_to_async(take_start_experiment)(self.session_id, event["message_text"])

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        #Send message to staff page
        if message_data["status"]["value"] == "fail":
            await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
        else:
            #send message to client pages
            await self.channel_layer.group_send(
                    self.room_group_name,
                    {"type": "update_start_experiment",
                    "sender_channel_name": self.channel_name},
                )
    
    async def reset_experiment(self, event):
        '''
        reset experiment, removes all trades, bids and asks
        '''
        message_data = {}
        message_data["status"] = await sync_to_async(take_reset_experiment)(self.session_id, event["message_text"])

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        # Send message to WebSocket
        if message_data["status"]["value"] == "fail":
            await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
        else:
            #send message to client pages
            await self.channel_layer.group_send(
                    self.room_group_name,
                    {"type": "update_reset_experiment",
                     "sender_channel_name": self.channel_name},
                )
    
    async def end_early(self, event):
        '''
        set the current period as the last period
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_end_early)(self.session_id)

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def reset_connections(self, event):
        '''
        reset connection counts for experiment
        '''
        #update subject count
        message_data = {}
        message_data["status"] = await sync_to_async(take_reset_connections)(self.session_id, event["message_text"])

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        # Send message to WebSocket
        if message_data["status"]["value"] == "fail":
            await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
        else:
            #send message to client pages
            await self.channel_layer.group_send(
                    self.room_group_name,
                    {"type": "update_reset_connections",
                     "sender_channel_name": self.channel_name},
                )

    async def next_phase(self, event):
        '''
        advance to next phase in experiment
        '''
        #update subject count
        message_data = {}
        message_data["status"] = await sync_to_async(take_next_phase)(self.session_id, event["message_text"])

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        # Send message to WebSocket
        if message_data["status"]["value"] == "fail":
            await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
        else:
            #send message to client pages
            await self.channel_layer.group_send(
                    self.room_group_name,
                    {"type": "update_next_phase",
                     "data": message_data["status"],
                     "sender_channel_name": self.channel_name},
                )

    
    #consumer updates
    async def update_start_experiment(self, event):
        '''
        start experiment on staff
        '''
        # logger = logging.getLogger(__name__) 
        # logger.info(f'update_goods{self.channel_name}')

        #get session json object
        result = await sync_to_async(main.consumers.take_get_session)(self.connection_uuid)

        message_data = {}
        message_data["session"] = result

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        #if self.channel_name != event['sender_channel_name']:
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def update_reset_experiment(self, event):
        '''
        update reset experiment
        '''
        #update subject count
        message_data = {}
        message_data["session"] = await sync_to_async(main.consumers.take_get_session)(self.connection_uuid)

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def update_reset_connections(self, event):
        '''
        update reset experiment
        '''
        #update subject count
        message_data = {}
        message_data["session"] = await sync_to_async(main.consumers.take_get_session)(self.connection_uuid)

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    

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

    return {"value" : "success", "result" : session.parameter_set.period_count}

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