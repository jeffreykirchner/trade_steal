'''
websocket session list
'''
from asgiref.sync import sync_to_async

import json
import logging
import asyncio

from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction

from main.consumers import SocketConsumerMixin
from main.consumers import StaffSubjectUpdateMixin

from main.forms import SessionForm
from main.forms import SessionPlayerMoveTwoForm
from main.forms import SessionPlayerMoveThreeForm

from main.models import Session

class StaffSessionConsumer(SocketConsumerMixin, StaffSubjectUpdateMixin):
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

    async def next_period(self, event):
        '''
        force advance to next period in experiment
        '''
        #update subject count
        message_data = {}
        message_data["data"] = await sync_to_async(take_next_period)(self.session_id, event["message_text"])

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def start_timer(self, event):
        '''
        start or stop timer 
        '''
        logger = logging.getLogger(__name__)

        logger.info(f"start_timer {event}")

        result = await sync_to_async(take_start_timer)(self.session_id, event["message_text"])

        message_data = {}
        message_data["status"] = result

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        if event["message_text"]["action"] == "start":
            self.timer_running = True
        else:
            self.timer_running = False

        #Send reply to sending channel
        if self.timer_running == True:
            await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

        #update all that timer has started
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "update_time",
                "data": result,
                "sender_channel_name": self.channel_name,},
        )

        if result["value"] == "success" and event["message_text"]["action"] == "start":
            #start continue timer
            await self.channel_layer.send(
                self.channel_name,
                {
                    'type': "continue_timer",
                    'message_text': {},
                }
            )
        else:
            logger.warning(f"start_timer: {message}")
        
        logger.info(f"start_timer complete {event}")

    async def continue_timer(self, event):
        '''
        continue to next second of the experiment
        '''
        logger = logging.getLogger(__name__)
        logger.info(f"continue_timer start")

        if not self.timer_running:
            logger.info(f"continue_timer timer off")
            return

        await asyncio.sleep(1)

        if not self.timer_running:
            logger.info(f"continue_timer timer off")
            return

        timer_result = await sync_to_async(take_do_period_timer)(self.session_id)

        # timer_result = await do_period_timer(self.session_id)

        if timer_result["value"] == "success":

            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "update_time",
                "data": timer_result,
                "sender_channel_name": self.channel_name,},
            )

            if timer_result["result"]["do_group_update"]:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {"type": "update_groups",
                     "data": {},
                     "sender_channel_name": self.channel_name,},
                )

            #if session is not over continue
            if not timer_result["end_game"]:
                await self.channel_layer.send(
                    self.channel_name,
                    {
                        'type': "continue_timer",
                        'message_text': {},
                    }
                )
        
        logger.info(f"continue_timer end")

    async def download_summary_data(self, event):
        '''
        download summary data
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_download_summary_data)(self.session_id)

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def download_action_data(self, event):
        '''
        download summary data
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_download_action_data)(self.session_id)

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def download_recruiter_data(self, event):
        '''
        download summary data
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_download_recruiter_data)(self.session_id)

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

        #get session json object
        result = await sync_to_async(take_get_session)(self.connection_uuid)

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
        message_data["session"] = await sync_to_async(take_get_session)(self.connection_uuid)

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
        message_data["session"] = await sync_to_async(take_get_session)(self.connection_uuid)

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
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

    async def update_time(self, event):
        '''
        update running, phase and time status
        '''

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
    
    form_data_dict = {}

    for field in form_data:            
        form_data_dict[field["name"]] = field["value"]

    form = SessionForm(form_data_dict, instance=session)

    if form.is_valid():
        #print("valid form")                
        form.save()              

        return {"status":"success", "session" : session.json()}                      
                                
    logger.info("Invalid session form")
    return {"status":"fail", "errors":dict(form.errors.items())}

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

def take_next_period(session_id, data):
    '''
    advance to next period in the experiment
    '''   

    logger = logging.getLogger(__name__) 
    logger.info(f"Advance to Next Period: {data}")

    #session_id = data["sessionID"]
    session = Session.objects.get(id=session_id)

    if session.current_period == session.parameter_set.get_number_of_periods():
        session.finished = True
    else:
        session.current_period += 1

    session.save()

    status = "success"
    
    return {"status" : status,
            "current_period" : session.current_period,
            "finished" : session.finished}

def take_start_timer(session_id, data):
    '''
    start timer
    '''   
    logger = logging.getLogger(__name__) 
    logger.info(f"Start timer {data}")

    action = data["action"]

    with transaction.atomic():
        session = Session.objects.get(id=session_id)

        if session.timer_running and action=="start":
            
            logger.warning(f"Start timer: already started")
            return {"value" : "fail", "result" : {"message":"timer already running"}}

        if action == "start":
            session.timer_running = True
        else:
            session.timer_running = False

        session.save()

    return {"value" : "success", "result" : session.json_for_timmer()}

def take_do_period_timer(session_id):
    '''
    do period timer actions
    '''
    logger = logging.getLogger(__name__)

    session = Session.objects.get(id=session_id)

    if session.timer_running == False or session.finished:
        return_json = {"value" : "fail", "result" : {"message" : "session no longer running"}}
    else:
        return_json = session.do_period_timer()

    logger.info(f"take_do_period_timer: {return_json}")

    return return_json

def take_update_groups(session_id):
    '''
    take update groups
    '''

    session = Session.objects.get(id=session_id)

    status = "success"
    
    return {"status" : status,
            "group_list" : session.json_for_group_update()}

def take_download_summary_data(session_id):
    '''
    download summary data for session
    '''

    session = Session.objects.get(id=session_id)

    return {"value" : "success", "result" : session.get_download_summary_csv()}

def take_download_action_data(session_id):
    '''
    download action data for session
    '''

    session = Session.objects.get(id=session_id)

    return {"value" : "success", "result" : session.get_download_action_csv()}

def take_download_recruiter_data(session_id):
    '''
    download recruiter data for session
    '''

    session = Session.objects.get(id=session_id)

    return {"value" : "success", "result" : session.get_download_recruiter_csv()}


