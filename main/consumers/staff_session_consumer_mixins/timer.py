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

        # if result["value"] == "success" and event["message_text"]["action"] == "start":
        #     #start continue timer
        #     await self.channel_layer.send(
        #         self.channel_name,
        #         {
        #             'type': "continue_timer",
        #             'message_text': {},
        #         }
        #     )
        # else:
        #     logger.info(f"start_timer: {message}")
        
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
            message = {}
            message["messageType"] = "stop_timer_pulse"
            message["messageData"] = {}
            await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
            return

        # await asyncio.sleep(1)

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
            # if not timer_result["end_game"]:

            #     # await self.channel_layer.send(
            #     #     self.channel_name,
            #     #     {
            #     #         'type': "continue_timer",
            #     #         'message_text': {},
            #     #     }
            #     # )

            #     loop = asyncio.get_event_loop()
            #     #loop.call_later(1, asyncio.create_task, take_continue_timer(self.session_id, self.channel_name))
            #     loop.call_later(1, asyncio.create_task, 
            #                     self.channel_layer.send(
            #                         self.channel_name,
            #                         {
            #                             'type': "continue_timer",
            #                             'message_text': {},
            #                         }
            #                     ))

        
        # logger.info(f"continue_timer end")

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

