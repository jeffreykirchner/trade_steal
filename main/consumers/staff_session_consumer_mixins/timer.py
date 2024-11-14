from datetime import datetime
from decimal import Decimal
from asgiref.sync import sync_to_async

import logging
import math
import json

from django.db import transaction
from django.core.serializers.json import DjangoJSONEncoder

from main.models import Session
from main.models import SessionPlayer

from main.globals import PeriodPhase
from main.globals import round_half_away_from_zero

class TimerMixin():
    '''
    timer mixin for staff session consumer
    '''

    async def start_timer(self, event):
        '''
        start or stop timer 
        '''
        if self.controlling_channel != self.channel_name:
            # logger.warning(f"start_timer: not controlling channel")
            return
        
        logger = logging.getLogger(__name__) 
        logger.info(f"start_timer {event}")

        status = "success"
        message = ""

        action = event["message_text"]["action"]

        session = await Session.objects.aget(id=self.session_id)

        if self.world_state_local["timer_running"] and action=="start":
            
            logger.warning(f"Start timer: already started")
            message = "timer already running"
            status = "fail"

        else:
            if action == "start":
                self.world_state_local["timer_running"] = True
            else:
                self.world_state_local["timer_running"] = False

            session.timer_running=self.world_state_local["timer_running"]
            await session.asave()
            message = await sync_to_async(session.json_for_timmer)()

        if action == "start":
            self.timer_running = True

            self.world_state_local["timer_history"].append({"time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
                                                            "count": 0})
        else:
            self.timer_running = False

        await self.store_world_state(force_store=True)

        result = {"value" : status, "result" : message}
        
        await self.send_message(message_to_self=result, message_to_group=None,
                                message_type="start_timer", send_to_client=True, send_to_group=False)

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

        session = await Session.objects.aget(id=self.session_id)

        if not self.world_state_local["timer_running"] or \
               self.world_state_local["finished"]:
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

        end_game = False
        period_update = None

        if self.world_state_local["time_remaining"] == 0 and \
           self.world_state_local["current_period_phase"] == PeriodPhase.TRADE and \
           self.world_state_local["current_period"] >= self.parameter_set_local["period_count"]:

            await sync_to_async(session.do_period_consumption)(self.parameter_set_local)
            period_update = await sync_to_async(session.get_current_session_period)()
            self.world_state_local["finished"] = True
            end_game = True

        notice_list = []
        
        if not end_game:

            if self.world_state_local["time_remaining"] == 0:

                if self.world_state_local["current_period_phase"] == PeriodPhase.PRODUCTION:
                    notice_list = await sync_to_async(session.record_period_production)()
                                       
                    #start trade phase
                    self.world_state_local["current_period_phase"] = PeriodPhase.TRADE
                    self.world_state_local["time_remaining"] = self.parameter_set_local["period_length_trade"]
                else:
                    await sync_to_async(session.do_period_consumption)(self.parameter_set_local)
                    
                    period_update = await sync_to_async(session.get_current_session_period)()

                    self.world_state_local["current_period"] += 1
                    self.world_state_local["current_period_phase"] = PeriodPhase.PRODUCTION
                    self.world_state_local["time_remaining"] = self.parameter_set_local["period_length_production"]                       

                    if self.world_state_local["current_period"] % self.parameter_set_local["break_period_frequency"] == 0:
                        notice_list = await sync_to_async(session.add_notice_to_all)(f"<center>*** Break period, chat only, no production. ***</center>")           
            else:
                
                if self.world_state_local["current_period_phase"] == PeriodPhase.PRODUCTION:

                    if self.world_state_local["current_period"] % self.parameter_set_local["break_period_frequency"] != 0 :
                        await do_period_production(session, self.world_state_local, self.parameter_set_local)                        

                self.world_state_local["time_remaining"] -= 1

        session.current_period=self.world_state_local["current_period"]
        session.current_period_phase=self.world_state_local["current_period_phase"]
        session.time_remaining=self.world_state_local["time_remaining"]
        session.finished=self.world_state_local["finished"]
        await session.asave()

        result = {"value" : "success",
                  "result" : await sync_to_async(session.json_for_timmer)(),
                  "period_update" : await sync_to_async(period_update.json)() if period_update else None,
                  "notice_list" : notice_list,
                  "end_game" : end_game}

        if result["value"] == "success":

            self.world_state_local["timer_history"][-1]["count"] = math.floor(ts.seconds)
            await self.store_world_state(force_store=True)

            result["result"]["group"] = {}

            for p in self.world_state_local["session_players"]:
                result["result"]["group"][str(p)] = await self.get_player_group(p, result["result"]["current_period"])

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


async def do_period_production(session, world_state_local, parameter_set_local):
    '''
    do period production
    '''
    logger = logging.getLogger(__name__)

    # logger.info(f"do_period_production: {session}")

    session_players = world_state_local["session_players"]

    #update world state
    for p in session_players:
        session_player = session_players[str(p)]
        parameter_set_type = parameter_set_local["parameter_set_players"][str(session_player["parameter_set_player_id"])]["parameter_set_type"]
    
        session_player["good_one_field_production"] += await do_period_production_function(
                                                                Decimal(parameter_set_type["good_one_production_1"]),
                                                                Decimal(parameter_set_type["good_one_production_2"]),
                                                                Decimal(parameter_set_type["good_one_production_3"]),
                                                                Decimal(session_player["good_one_production_rate"]),
                                                                parameter_set_local)

        session_player["good_two_field_production"] += await do_period_production_function(
                                                                Decimal(parameter_set_type["good_two_production_1"]),
                                                                Decimal(parameter_set_type["good_two_production_2"]),
                                                                Decimal(parameter_set_type["good_two_production_3"]),
                                                                Decimal(session_player["good_two_production_rate"]),
                                                                parameter_set_local)
        #round to int
        session_player["good_one_field"] = int(round_half_away_from_zero(session_player["good_one_field_production"], 0))
        session_player["good_two_field"] = int(round_half_away_from_zero(session_player["good_two_field_production"], 0))


    #store result in session players
    objects = []

    for p in session_players:
        session_player = session_players[str(p)]
        player = await session.session_players.aget(id=p)

        player.good_one_field_production = session_player["good_one_field_production"]
        player.good_two_field_production = session_player["good_two_field_production"]

        player.good_one_field = session_player["good_one_field"]
        player.good_two_field = session_player["good_two_field"]
        
        objects.append(player)

    await SessionPlayer.objects.abulk_update(objects, 
                                             ["good_one_field_production", 
                                              "good_two_field_production",
                                              "good_one_field", 
                                              "good_two_field"])
    

async def do_period_production_function(good_production_1: Decimal, 
                                        good_production_2: Decimal, 
                                        good_production_3 : Decimal, 
                                        production_rate: Decimal,
                                        parameter_set_local):
        '''
        return production for single good
        '''
        total_time = Decimal(parameter_set_local["period_length_production"])

        good_time =  total_time * Decimal(production_rate)/Decimal('100')
        production = good_production_1 + good_production_2 * good_time ** good_production_3
        production *= Decimal('1')/total_time

        return round(production, 9)
# def take_start_timer(session_id, data):
#     '''
#     start timer
#     '''   
#     logger = logging.getLogger(__name__) 
#     logger.info(f"Start timer {data}")

#     action = data["action"]

#     with transaction.atomic():
#         session = Session.objects.get(id=session_id)

#         if session.timer_running and action=="start":
            
#             logger.warning(f"Start timer: already started")
#             return {"value" : "fail", "result" : {"message":"timer already running"}}

#         if action == "start":
#             session.timer_running = True
#         else:
#             session.timer_running = False

#         session.save()

#     return {"value" : "success", "result" : session.json_for_timmer()}

# def take_do_period_timer(session_id):
#     '''
#     do period timer actions
#     '''
#     logger = logging.getLogger(__name__)

#     session = Session.objects.get(id=session_id)

#     if session.timer_running == False or session.finished:
#         return_json = {"value" : "fail", "result" : {"message" : "session no longer running"}}
#     else:
#         return_json = session.do_period_timer()

#     # logger.info(f"take_do_period_timer: {return_json}")

#     return return_json

