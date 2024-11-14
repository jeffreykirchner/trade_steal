'''
websocket session list
'''
from asgiref.sync import sync_to_async

import logging
import copy
import json
import string
from copy import copy
from copy import deepcopy

from django.core.exceptions import  ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction

from main.consumers import SocketConsumerMixin
from main.consumers import StaffSubjectUpdateMixin

from main.forms import SessionPlayerMoveTwoForm
from main.forms import SessionPlayerMoveThreeForm
from main.forms import EndGameForm

from main.models import Session
from main.models import SessionPlayer
from main.models import SessionPlayerMove
from main.models import SessionPlayerChat
from main.models import SessionPlayerNotice

from main.globals import ContainerTypes
from main.globals import ChatTypes
from main.globals import PeriodPhase
from main.globals import round_half_away_from_zero

from main.decorators import check_sesison_started_ws

from .send_message_mixin import SendMessageMixin

import main

class SubjectHomeConsumer(SocketConsumerMixin, 
                          SendMessageMixin,
                          StaffSubjectUpdateMixin):
    '''
    websocket session list
    '''    

    group_number = 0        #group number player subject is in
    town_number = 0         #town number subject is in 
    session_player_id = 0   #session player id number
    
    async def get_session(self, event):
        '''
        return a list of sessions
        '''
        logger = logging.getLogger(__name__) 
        # logger.info(f"Get Session {event}")

        self.connection_uuid = event["message_text"]["playerKey"]
        self.connection_type = "subject"

        #get session id for subject
        try:
            session_player = await SessionPlayer.objects.select_related('session').aget(player_key=self.connection_uuid)
            self.session_id = session_player.session.id
            self.session_player_id = session_player.id
            self.controlling_channel =  session_player.session.controlling_channel
        except ObjectDoesNotExist:
            result = {"session" : None, "session_player" : None}
        else:        
            result = await sync_to_async(take_get_session_subject)(self.session_player_id)                

        await self.send_message(message_to_self=result, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)
    
    # async def production_time(self, event):
    #     '''
    #     take update to production time between goods one and two
    #     '''
    #     #update subject count
    #     result = await sync_to_async(take_production_time, thread_sensitive=False)(self.session_id, self.session_player_id, event["message_text"])

    #     result["session_player_id"] = self.session_player_id

    #     # Send reply to sending channel
    #     await self.send_message(message_to_self=result, message_to_group=None,
    #                             message_type=event['type'], send_to_client=True, send_to_group=False)

    #     if result["value"] == "success":
    #         await self.send_message(message_to_self=None, message_to_group=result,
    #                                 message_type=event['type'], send_to_client=False, send_to_group=True)

    async def name(self, event):
        '''
        take name and id number
        '''
        result = await sync_to_async(take_name)(self.session_id, self.session_player_id, event["message_text"])
       
        await self.send_message(message_to_self=result, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

        if result["value"] == "success":
            await self.send_message(message_to_self=None, message_to_group=result,
                                    message_type=event['type'], send_to_client=False, send_to_group=True)

    async def avatar(self, event):
        '''
        take avatar number
        '''
        result = await sync_to_async(take_avatar, thread_sensitive=False)(self.session_id, self.session_player_id, event["message_text"])
        
        await self.send_message(message_to_self=result, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

        if result["value"] == "success":
           await self.send_message(message_to_self=None, message_to_group=result,
                                    message_type=event['type'], send_to_client=False, send_to_group=True)

    async def next_instruction(self, event):
        '''
        advance instruction page
        '''
        result = await sync_to_async(take_next_instruction, thread_sensitive=False)(self.session_id, self.session_player_id, event["message_text"])
        
        await self.send_message(message_to_self=result, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

        if result["value"] == "success":
           await self.send_message(message_to_self=None, message_to_group=result,
                                    message_type=event['type'], send_to_client=False, send_to_group=True)
    
    async def finish_instructions(self, event):
        '''
        fisish instructions
        '''
        result = await sync_to_async(take_finish_instructions, thread_sensitive=False)(self.session_id, self.session_player_id, event["message_text"])
       
        await self.send_message(message_to_self=result, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

        if result["value"] == "success":
           await self.send_message(message_to_self=None, message_to_group=result,
                                    message_type=event['type'], send_to_client=False, send_to_group=True)

    async def update_set_controlling_channel(self, event):
        '''
        only for subject screens
        '''
        event_data = json.loads(event["group_data"])
        self.controlling_channel = event_data["controlling_channel"]

    #consumer updates
    async def update_start_experiment(self, event):
        '''
        start experiment on subjects
        '''
        #logger = logging.getLogger(__name__) 
        #logger.info(f'update start subjects {self.channel_name}')

        await self.update_local_info(event)

        result = await sync_to_async(take_get_session_subject)(self.session_player_id)

        await self.send_message(message_to_self=result, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)
    
    async def update_reset_experiment(self, event):
        '''
        reset experiment on subjects
        '''
        #logger = logging.getLogger(__name__) 
        #logger.info(f'update start subjects {self.channel_name}')

        result = await sync_to_async(take_get_session_subject)(self.session_player_id)

        await self.send_message(message_to_self=result, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

    async def update_chat(self, event):
        '''
        send chat to clients, if clients can view it
        '''

        if not str(self.session_player_id) in event["target_list"]:
            return

        result = json.loads(event["group_data"])

        await self.send_message(message_to_self=result, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

    async def update_local_info(self, event):
        '''
        update connection's town and group information
        '''
        result = await sync_to_async(take_update_local_info)(self.session_id, self.connection_uuid, event)

        logger = logging.getLogger(__name__) 
        logger.info(f"update_local_info {result}")

        self.group_number = result["group_number"]
        self.town_number = result["town_number"]
        self.session_player_id = result["session_player_id"]
    
    async def update_move_goods(self, event):
        '''
        update good count on all but sender
        '''
        # logger = logging.getLogger(__name__) 
        # logger.info(f'update_goods{self.channel_name}')

        if not str(self.session_player_id) in event["target_list"]:
            return

        result =  json.loads(event["group_data"])

        await self.send_message(message_to_self=result, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

    async def update_time(self, event):
        '''
        update running, phase and time status
        '''

        event_data = json.loads(deepcopy(event["group_data"]))

        #if new period is starting, update local info
        if event_data["result"]["do_group_update"]:
             await self.update_local_info(event)

        #remove other player earnings
        for session_players_earnings in event_data["result"]["session_player_earnings"]:
            if session_players_earnings["id"] == self.session_player_id:
                event_data["result"]["session_player_earnings"] = session_players_earnings
                break
        
        #remove none group memebers
        session_players = []
        if len(event_data["result"]["session_players"]) > 0:
            group_number =  event_data["result"]["group"][str(self.session_player_id)]
            for session_player in event_data["result"]["session_players"]:
                if session_player["group_number"] == group_number:
                    session_players.append(session_player)
        
        #remove other player notices
        notice_list = []
        for session_player_notice in event_data.get("notice_list", []):
            if session_player_notice["session_player_id"] == self.session_player_id:
                notice_list.append(session_player_notice)
                break

        event_data["notice_list"] = notice_list   

        event_data["result"]["session_players"] = session_players

        await self.send_message(message_to_self=event_data, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

    async def update_groups(self, event)  :
        '''
        update groups on client
        '''

        result = await sync_to_async(take_update_groups)(self.session_id, self.session_player_id)

        await self.send_message(message_to_self=result, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

    async def update_connection_status(self, event):
        '''
        handle connection status update from group member
        '''
        pass

    async def update_name(self, event):
        '''
        no group broadcast of name to subjects
        '''
        pass
    
    async def update_avatar(self, event):
        '''
        no group broadcast of avatar to subjects
        '''
        pass
    
    async def update_next_phase(self, event):
        '''
        update session phase
        '''

        result = await sync_to_async(take_update_next_phase)(self.session_id, self.session_player_id)

        await self.send_message(message_to_self=result, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

    async def update_next_instruction(self, event):
        '''
        no group broadcast of avatar to current instruction
        '''
        pass
    
    async def update_finish_instructions(self, event):
        '''
        no group broadcast of avatar to current instruction
        '''
        pass

    async def update_production_time(self, event):
        '''
        update production time
        '''
        if not str(self.session_player_id) in event["target_list"]:
            return

        result =  json.loads(event["group_data"])

        await self.send_message(message_to_self=result, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)
    
    async def update_anonymize_data(self, event):
        '''
        no anonmyize data update on client
        '''
        pass
    
    async def update_update_subject(self, event):
        '''
        do not update subject screens when staff updates subject name
        '''
        pass

    async def update_survey_complete(self, event):
        '''
        no group broadcast of survey complete
        '''
        pass
    
    async def update_refresh_screens(self, event):
        '''
        refresh staff screen
        '''
        pass

    async def update_reset_connections(self, event):
        '''
        update reset experiment
        '''
        pass
       
#local sync functions  
def take_get_session_subject(session_player_id):
    '''
    get session info for subject
    '''
    #session_id = data["sessionID"]
    #uuid = data["uuid"]

    #session = Session.objects.get(id=session_id)
    try:
        session_player = SessionPlayer.objects.get(id=session_player_id)

        return {"session" : session_player.session.json_for_subject(session_player), 
                "session_player" : session_player.json() }

    except ObjectDoesNotExist:
        return {"session" : None, 
                "session_player" : None}

def take_get_session_id(player_key):
    '''
    get the session id for the player_key
    '''
    session_player = SessionPlayer.objects.get(player_key=player_key)

    return session_player.session.id
  
def take_update_local_info(session_id, player_key, data):
    '''
    update connection's town and group information
    '''

    try:
        session_player = SessionPlayer.objects.get(player_key=player_key)
        session_player.save()

        return {"group_number" : session_player.get_current_group_number(), 
                "session_player_id" : session_player.id,
                "town_number" : session_player.get_current_town_number() }
    except ObjectDoesNotExist:      
        return {"group_number" : None, 
                "session_player_id" : None,
                "town_number" : None}

# def take_production_time(session_id, session_player_id, data):
#     '''
#     update subjects production time split between good one and two
#     '''

#     logger = logging.getLogger(__name__) 
#     # logger.info(f"take production time: {session_id} {session_player_id} {data}")

#     try:
#         good_one_production_rate = int(data["production_slider_one"])
#         good_two_production_rate = int(data["production_slider_two"])
#     except KeyError:
#         message = "Invalid values."
#         logger.warning(f"take production time: {message}")
#         return {"value" : "fail", "result" : {}, "message" : message}
#     except ValueError:
#         message = "Invalid values."
#         logger.warning(f"take production time: {message}")
#         return {"value" : "fail", "result" : {}, "message" : message}

#     if good_one_production_rate + good_two_production_rate != 100 or \
#        good_one_production_rate < 0 or good_two_production_rate < 0:

#         message = "Invalid values."
#         logger.warning(f"take production time: {message}")
#         return {"value" : "fail", "result" : {}, "message" : message}

#     try:
#         session = Session.objects.get(id=session_id)
#         session_player = SessionPlayer.objects.get(id=session_player_id)

#         if session.current_period_phase == PeriodPhase.PRODUCTION and \
#            session.current_period > 1:

#             message = "Not updates during production."
#             logger.warning(f"take production time: {message}")
#             return {"value" : "fail", "result" : {}, "message" : message}

#         session_player.good_one_production_rate = good_one_production_rate
#         session_player.good_two_production_rate = good_two_production_rate

#         session_player.save()

#         return {"value" : "success", 
#                 "result" : {"good_one_production_rate" : session_player.good_one_production_rate,
#                             "good_two_production_rate" : session_player.good_two_production_rate,
#                             "id" : session_player_id }} 
                            
#     except ObjectDoesNotExist:      
#         return {"value" : "fail", "result" : {}, "message" : "Invalid player."} 

def take_update_groups(session_id, session_player_id):
    '''
    update groups on the client screen
    '''
    logger = logging.getLogger(__name__) 

    try:
        session_player = SessionPlayer.objects.get(id=session_player_id)

        group_list = session_player.get_current_group_list()

        return {"value" : "success",
                "result" : {"session_players" : {str(p.id):p.json_for_subject(session_player) for p in group_list},
                            "session_players_order" : [p.id for p in group_list]}}

    except ObjectDoesNotExist:
        logger.warning(f"take_update_groups: session not found, session {session_id}, session_player_id {session_player_id}")
        return {"value" : "fail", "result" : {}, "message" : "Group update error"}

def take_name(session_id, session_player_id, data):
    '''
    take name and student id at end of game
    '''

    logger = logging.getLogger(__name__) 
    # logger.info(f"Take name: {session_id} {session_player_id} {data}")

    try:
        form_data = data["formData"]

        form_data_dict = form_data

    except KeyError:
        logger.warning(f"take_name , setup form: {session_player_id}")
        return {"value" : "fail", "errors" : {f"name":["Invalid entry."]}}
    
    session = Session.objects.get(id=session_id)
    session_player = session.session_players.get(id=session_player_id)

    if not session.finished:
        return {"value" : "fail", "errors" : {f"name":["Session not complete."]},
                "message" : "Session not complete."}

    # logger.info(f'form_data_dict : {form_data_dict}')       

    form = EndGameForm(form_data_dict)
        
    if form.is_valid():
        #print("valid form") 

        session_player.name = form.cleaned_data["name"]
        session_player.student_id = form.cleaned_data["student_id"]

        session_player.name = string.capwords(session_player.name)

        session_player.save()    
        
        return {"value" : "success",
                "result" : {"id" : session_player_id,
                            "name" : session_player.name, 
                            "student_id" : session_player.student_id}}                      
                                
    logger.info("Invalid session form")
    return {"value" : "fail", "errors" : dict(form.errors.items()), "message" : ""}

def take_avatar(session_id, session_player_id, data):
    '''
    take name and student id at end of game
    '''

    logger = logging.getLogger(__name__) 
    logger.info(f"Take avatar: {session_id} {session_player_id} {data}")

    try:       
        row = data.get("row")
        col = data.get("col")

        session = Session.objects.get(id=session_id)
        session_player = session.session_players.get(id=session_player_id)

        if not session.started:
           return {"value" : "fail", "errors" : {}, "message" : "Session not started."}

        parameter_set_avatar = session.parameter_set.parameter_set_avatars_a.get(grid_location_row=row, grid_location_col=col)

        if parameter_set_avatar.avatar == None:
            logger.warning(f"blank avatar choosen : {session_player_id}")
            return {"value" : "fail", "errors" : {}, "message" : "Avatar is blank."}

        session_player.avatar = parameter_set_avatar.avatar        
        session_player.save()

    except ObjectDoesNotExist:
        logger.warning(f"take_avatar : {session_player_id}")
        return {"value" : "fail", "errors" : {}, "message" : "Avatar choice error."}       
    
    return {"value" : "success",
            "result" : {"id" : session_player_id,
                        "avatar" : session_player.avatar.json(), 
                        }}                      

def take_update_next_phase(session_id, session_player_id):
    '''
    return information about next phase of experiment
    '''

    logger = logging.getLogger(__name__) 

    try:
        session = Session.objects.get(id=session_id)
        session_player = SessionPlayer.objects.get(id=session_player_id)

        group_list = session_player.get_current_group_list()

        return {"value" : "success",
                "session" : session_player.session.json_for_subject(session_player),
                "session_player" : session_player.json(),
                "session_players" : {str(p.id):p.json_for_subject(session_player) for p in group_list}}

    except ObjectDoesNotExist:
        logger.warning(f"take_update_next_phase: session not found, session {session_id}, session_player_id {session_player_id}")
        return {"value" : "fail", "result" : {}, "message" : "Update next phase error"}

def take_next_instruction(session_id, session_player_id, data):
    '''
    take show next instruction page
    '''

    logger = logging.getLogger(__name__) 
    logger.info(f"Take next instruction: {session_id} {session_player_id} {data}")

    try:       

        session = Session.objects.get(id=session_id)
        session_player = session.session_players.get(id=session_player_id)

        direction = data["direction"]

        #move to next instruction
        if direction == 1:
            #advance furthest instruction complete
            if session_player.current_instruction_complete < session_player.current_instruction:
                session_player.current_instruction_complete = copy(session_player.current_instruction)

            if session_player.current_instruction < session.parameter_set.instruction_set.instructions.count():
                session_player.current_instruction += 1
        elif session_player.current_instruction > 1:
             session_player.current_instruction -= 1

        session_player.save()

    except ObjectDoesNotExist:
        logger.warning(f"take_next_instruction not found: {session_player_id}")
        return {"value" : "fail", "errors" : {}, "message" : "Instruction Error."} 
    except KeyError:
        logger.warning(f"take_next_instruction key error: {session_player_id}")
        return {"value" : "fail", "errors" : {}, "message" : "Instruction Error."}       
    
    return {"value" : "success",
            "result" : {"current_instruction" : session_player.current_instruction,
                        "id" : session_player_id,
                        "current_instruction_complete" : session_player.current_instruction_complete, 
                        }}

def take_finish_instructions(session_id, session_player_id, data):
    '''
    take finish instructions
    '''

    logger = logging.getLogger(__name__) 
    logger.info(f"Take finish instructions: {session_id} {session_player_id} {data}")

    try:       

        session = Session.objects.get(id=session_id)
        session_player = session.session_players.get(id=session_player_id)

        session_player.current_instruction_complete = session.parameter_set.instruction_set.instructions.count()
        session_player.instructions_finished = True
        session_player.save()

    except ObjectDoesNotExist:
        logger.warning(f"take_next_instruction : {session_player_id}")
        return {"value" : "fail", "errors" : {}, "message" : "Move Error"}       
    
    return {"value" : "success",
            "result" : {"instructions_finished" : session_player.instructions_finished,
                        "id" : session_player_id,
                        "current_instruction_complete" : session_player.current_instruction_complete, 
                        }}