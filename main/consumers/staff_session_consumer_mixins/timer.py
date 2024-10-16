from datetime import datetime
from decimal import Decimal
from asgiref.sync import sync_to_async

import logging
import math
import json

from django.db import transaction
from django.core.serializers.json import DjangoJSONEncoder

from main.models import Session

class TimerMixin():
    '''
    timer mixin for staff session consumer
    '''

    async def start_timer(self, event):
        '''
        start or stop timer 
        '''
        logger = logging.getLogger(__name__) 

        if self.controlling_channel != self.channel_name:
            # logger.warning(f"start_timer: not controlling channel")
            return
        
        logger = logging.getLogger(__name__)

        logger.info(f"start_timer {event}")

        result = await sync_to_async(take_start_timer)(self.session_id, event["message_text"])

        if event["message_text"]["action"] == "start":
            self.timer_running = True

            self.world_state_local["timer_history"].append({"time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                                                            "count": 0})
        else:
            self.timer_running = False

        await self.store_world_state(force_store=True)

        #Send reply to sending channel
        if self.timer_running == True:
            await self.send_message(message_to_self=result, message_to_group=None,
                                    message_type="start_timer", send_to_client=True, send_to_group=False)

        #update all that timer has started
        await self.send_message(message_to_self=None, message_to_group=result,
                                message_type="time", send_to_client=False, send_to_group=True)
        
        logger.info(f"start_timer complete {event}")

    async def continue_timer(self, event):
        '''
        continue to next second of the experiment
        '''
        logger = logging.getLogger(__name__) 
        
        if self.controlling_channel != self.channel_name:
            # logger.warning(f"continue_timer: not controlling channel")
            return
        
        logger = logging.getLogger(__name__)
        # logger.info(f"continue_timer start")

        if not self.timer_running:
            logger.info(f"continue_timer timer off")
            result = {}
            await self.send_message(message_to_self=result, message_to_group=None,
                                    message_type="stop_timer_pulse", send_to_client=True, send_to_group=False)
            return
        
        #check if full second has passed
        send_update = True
        ts = datetime.now() - datetime.strptime(self.world_state_local["timer_history"][-1]["time"],"%Y-%m-%dT%H:%M:%S.%f")

        #check if a full second has passed
        if self.world_state_local["timer_history"][-1]["count"] == math.floor(ts.seconds):
            send_update = False

        if not send_update:
            return
        
        session = await Session.objects.select_related("parameter_set").aget(id=self.session_id)

        if session.timer_running == False or session.finished:
            result = {"value" : "fail", "result" : {"message" : "session no longer running"}}
        else:
            result = await sync_to_async(session.do_period_timer)(self.parameter_set_local)

        if result["value"] == "success":

            self.world_state_local["timer_history"][-1]["count"] = math.floor(ts.seconds)
            await self.store_world_state(force_store=True)

            await self.send_message(message_to_self=None, message_to_group=result,
                                    message_type="time", send_to_client=False, send_to_group=True)

            if result["result"]["do_group_update"]:
                await self.send_message(message_to_self=None, message_to_group={},
                                    message_type="groups", send_to_client=False, send_to_group=True)
                
    async def update_time(self, event):
        '''
        update running, phase and time status
        '''

        result = json.loads(event["group_data"])

        await self.send_message(message_to_self=result, message_to_group=None,
                                    message_type=event['type'], send_to_client=True, send_to_group=False)

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

    # logger.info(f"take_do_period_timer: {return_json}")

    return return_json

