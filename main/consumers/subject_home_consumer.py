'''
websocket session list
'''
from asgiref.sync import sync_to_async

import logging
import copy
import json
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

from main.models import Session, avatar
from main.models import SessionPlayer
from main.models import SessionPlayerMove
from main.models import SessionPlayerChat
from main.models import SessionPlayerNotice

from main.globals import ContainerTypes
from main.globals import ChatTypes
from main.globals import PeriodPhase
from main.globals import round_half_away_from_zero

class SubjectHomeConsumer(SocketConsumerMixin, StaffSubjectUpdateMixin):
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
        logger.info(f"Get Session {event}")

        self.connection_uuid = event["message_text"]["playerKey"]
        self.connection_type = "subject"
        self.session_id = await sync_to_async(take_get_session_id)(self.connection_uuid)

        await self.update_local_info(event)

        result = await sync_to_async(take_get_session_subject)(self.session_player_id)

        #build response
        message_data = {"status":{}}
        message_data["status"] = result

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message,}, cls=DjangoJSONEncoder))

    async def move_goods(self, event):
        '''
        move goods between two containers
        '''
        #update subject count
        result = await sync_to_async(take_move_goods)(self.session_id, self.session_player_id, event["message_text"])

        message_data = {}
        message_data["status"] = result

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        # Send reply to sending channel
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

        #if success send to all connected clients
        if result["value"] == "success":
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "update_move_goods",
                 "data": result,
                 'sender_channel_name': self.channel_name,
                 'sender_group' : self.group_number,
                 "sender_town" : self.town_number,},
            )
        
    async def chat(self, event):
        '''
        take chat from client
        '''        
        result = await sync_to_async(take_chat)(self.session_id, self.session_player_id, event["message_text"])

        if result["value"] == "fail":
            await self.send(text_data=json.dumps({'message': result}, cls=DjangoJSONEncoder))
            return

        event_result = result["result"]

        subject_result = {}
        subject_result["chat_type"] = event_result["chat_type"]
        subject_result["sesson_player_target"] = event_result.get("sesson_player_target", -1)
        subject_result["chat"] = event_result["chat_for_subject"]
        subject_result["value"] = result["value"]

        staff_result = {}
        staff_result["town"] = self.town_number
        staff_result["chat"] = event_result["chat_for_staff"]

        message_data = {}
        message_data["status"] = subject_result

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        # Send reply to sending channel
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

        #if success send to all connected clients
        if result["value"] == "success":
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "update_chat",
                 "subject_result": subject_result,
                 "staff_result": staff_result,
                 "sender_group" : self.group_number,
                 "sender_town" : self.town_number,
                 "sender_channel_name": self.channel_name},
            )
    
    async def production_time(self, event):
        '''
        take update to production time between goods one and two
        '''
        #update subject count
        result = await sync_to_async(take_production_time)(self.session_id, self.session_player_id, event["message_text"])

        message_data = {}
        message_data["status"] = result

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        # Send reply to sending channel
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def name(self, event):
        '''
        take name and id number
        '''
        result = await sync_to_async(take_name)(self.session_id, self.session_player_id, event["message_text"])
        message_data = {}
        message_data["status"] = result

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

        if result["value"] == "success":
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "update_name",
                 "data": result,
                 "sender_channel_name": self.channel_name},
            )

    async def avatar(self, event):
        '''
        take avatar number
        '''
        result = await sync_to_async(take_avatar)(self.session_id, self.session_player_id, event["message_text"])
        message_data = {}
        message_data["status"] = result

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

        if result["value"] == "success":
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "update_avatar",
                 "data": result,
                 "sender_channel_name": self.channel_name},
            )

    async def next_instruction(self, event):
        '''
        advance instruction page
        '''
        result = await sync_to_async(take_next_instruction)(self.session_id, self.session_player_id, event["message_text"])
        message_data = {}
        message_data["status"] = result

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

        if result["value"] == "success":
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "update_next_instruction",
                 "data": result,
                 "sender_channel_name": self.channel_name},
            )
    
    async def finish_instructions(self, event):
        '''
        fisish instructions
        '''
        result = await sync_to_async(take_finish_instructions)(self.session_id, self.session_player_id, event["message_text"])
        message_data = {}
        message_data["status"] = result

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

        if result["value"] == "success":
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "update_finish_instructions",
                 "data": result,
                 "sender_channel_name": self.channel_name},
            )

    #consumer updates
    async def update_start_experiment(self, event):
        '''
        start experiment on subjects
        '''
        #logger = logging.getLogger(__name__) 
        #logger.info(f'update start subjects {self.channel_name}')

        await self.update_local_info(event)

        #get session json object
        result = await sync_to_async(take_get_session_subject)(self.session_player_id)

        message_data = {}
        message_data["status"] = result

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        #if self.channel_name != event['sender_channel_name']:
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def update_reset_experiment(self, event):
        '''
        reset experiment on subjects
        '''
        #logger = logging.getLogger(__name__) 
        #logger.info(f'update start subjects {self.channel_name}')

        #get session json object
        result = await sync_to_async(take_get_session_subject)(self.session_player_id)

        message_data = {}
        message_data["status"] = result

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def update_chat(self, event):
        '''
        send chat to clients, if clients can view it
        '''

        message_data = {}
        message_data["status"] =  event["subject_result"]

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        if self.group_number != event['sender_group'] or \
           self.town_number != event['sender_town'] or \
           self.channel_name == event['sender_channel_name']:

            return
        

        if message_data['status']['chat_type'] == "Individual" and \
           message_data['status']['sesson_player_target'] != self.session_player_id and \
           message_data['status']['chat']['send_id'] != self.session_player_id:

           return

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

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

        message_data = {}
        message_data["status"] = event["data"]

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        if self.channel_name == event['sender_channel_name']:
            return

        if self.group_number != event['sender_group']:
            return
        
        if self.town_number != event['sender_town']:
            return

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def update_time(self, event):
        '''
        update running, phase and time status
        '''

        event_data = deepcopy(event["data"])

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
        for session_player in event_data["result"]["session_players"]:
            if session_player["group_number"] == self.group_number:
                session_players.append(session_player)
        
        #remove other player notices
        notice_list = []
        for session_player_notice in event_data.get("notice_list", []):
            if session_player_notice["session_player_id"] == self.session_player_id:
                notice_list.append(session_player_notice)
                break

        event_data["notice_list"] = notice_list   

        event_data["result"]["session_players"] = session_players

        message_data = {}
        message_data["status"] = event_data

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def update_groups(self, event)  :
        '''
        update groups on client
        '''

        result = await sync_to_async(take_update_groups)(self.session_id, self.session_player_id)

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

    async def update_name(self, event):
        '''
        no group broadcast of name to subjects
        '''

        # logger = logging.getLogger(__name__) 
        # logger.info("Eng game update")
    
    async def update_avatar(self, event):
        '''
        no group broadcast of avatar to subjects
        '''

        # logger = logging.getLogger(__name__) 
        # logger.info("Eng game update")
    
    async def update_next_phase(self, event):
        '''
        update session phase
        '''

        result = await sync_to_async(take_update_next_phase)(self.session_id, self.session_player_id)

        message_data = {}
        message_data["status"] = result

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def update_next_instruction(self, event):
        '''
        no group broadcast of avatar to current instruction
        '''

        # logger = logging.getLogger(__name__) 
        # logger.info("Eng game update")
    
    async def update_finish_instructions(self, event):
        '''
        no group broadcast of avatar to current instruction
        '''

        # logger = logging.getLogger(__name__) 
        # logger.info("Eng game update")

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
  
def take_move_goods(session_id, session_player_id, data):
    '''
    move goods between locations (house or field)
    '''

    logger = logging.getLogger(__name__) 
    logger.info(f"Move goods: {session_id} {session_player_id} {data}")

    #session_id = data["sessionID"]
    #uuid = data["uuid"]

    form_data = data["formData"]
    
    form_data_dict = {}

    for field in form_data:            
        form_data_dict[field["name"]] = field["value"]

    try:
        logger.info(f'form_data_dict : {form_data_dict}')       

        source_type = data["sourceType"]
        source_id = data["sourceID"]

        target_type = data["targetType"]
        target_id = data["targetID"]

        session = Session.objects.get(id=session_id)
        session_player = session.session_players.get(id=session_player_id)

        form_type = ""       #form suffix for 2 or three goods        
        if source_type == "house" and session.parameter_set.good_count == 3:
            form = SessionPlayerMoveThreeForm(form_data_dict)
            form_type = "3g"
        else:
            form = SessionPlayerMoveTwoForm(form_data_dict)
            form_type = "2g"

        if not session.started:
            return {"value" : "fail", "errors" : {f"transfer_good_one_amount_{form_type}":["Session has not started."]},
                    "message" : "Move Error"}
        
        if session.finished:
            return {"value" : "fail", "errors" : {f"transfer_good_one_amount_{form_type}":["Session complete."]},
                    "message" : "Move Error"}
        
        if session.current_period_phase == PeriodPhase.PRODUCTION:
             return {"value" : "fail", "errors" : {f"transfer_good_one_amount_{form_type}":["No transfers during production phase."]},
                     "message" : "Move Error"}
        
        if not session.parameter_set.allow_stealing:
            if target_type == "field":
                return {"value" : "fail", "errors" : {f"transfer_good_one_amount_{form_type}":["No transfers to fields."]},
                        "message" : "Move Error"}
        
    except KeyError:
            logger.warning(f"take_move_goods session, setup form: {session_id}")
            return {"value" : "fail", "errors" : {}, "message" : "Move Error"}

    if form.is_valid():
        #print("valid form") 

        try:        
            with transaction.atomic():

                source_session_player = session.session_players.get(id=source_id)              
                target_session_player = session.session_players.get(id=target_id)

                #check that stealing is allowed
                if not session.parameter_set.allow_stealing and source_session_player != session_player:
                    return {"value" : "fail", "errors" : {f"transfer_good_one_amount_{form_type}":[f"Invalid source."]},
                            "message" : "Move Error"}

                good_one_amount = form.cleaned_data[f"transfer_good_one_amount_{form_type}"]
                good_two_amount = form.cleaned_data[f"transfer_good_two_amount_{form_type}"]
                good_three_amount = 0

                #check that target can accept goods
                if good_one_amount > 0:
                    if not target_session_player.check_good_available_at_location(target_type, source_session_player.parameter_set_player.good_one):
                        return {"value" : "fail", "errors" : {f"transfer_good_one_amount_{form_type}":[f"Target cannot accept {source_session_player.parameter_set_player.good_one.label}."]},
                                "message" : "Move Error"}
                
                if good_two_amount > 0:
                    if not target_session_player.check_good_available_at_location(target_type, source_session_player.parameter_set_player.good_two):
                        return {"value" : "fail", "errors" : {f"transfer_good_two_amount_{form_type}":[f"Target cannot accept {source_session_player.parameter_set_player.good_two.label}."]},
                                "message" : "Move Error"}

                if session.parameter_set.good_count == 3 and source_type == "house":
                    good_three_amount = form.cleaned_data[f"transfer_good_three_amount_{form_type}"]
                    if good_three_amount > 0:
                        if not target_session_player.check_good_available_at_location(target_type, source_session_player.parameter_set_player.good_three):
                            return {"value" : "fail", "errors" : {f"transfer_good_three_amount_{form_type}":[f"Target cannot accept {source_session_player.parameter_set_player.good_three.label}."]},
                                    "message" : "Move Error"}

                #handle source
                if source_type == "house":
                    if round_half_away_from_zero(source_session_player.good_one_house, 0) < good_one_amount:
                         return {"value" : "fail", "errors" : {f"transfer_good_one_amount_{form_type}":[f"Source does not have enough {source_session_player.parameter_set_player.good_one.label}."]},
                                "message" : "Move Error"}
                    
                    #check enough good two
                    if round_half_away_from_zero(source_session_player.good_two_house, 0) < good_two_amount:
                        return {"value" : "fail", "errors" : {f"transfer_good_two_amount_{form_type}":[f"Source does not have enough {source_session_player.parameter_set_player.good_two.label}."]},
                                "message" : "Move Error"}

                    if round_half_away_from_zero(session.parameter_set.good_count, 0) == 3:
                        if source_session_player.good_three_house < good_three_amount:
                            return {"value" : "fail", "errors" : {f"transfer_good_three_amount_{form_type}":[f"Source does not have enough {source_session_player.parameter_set_player.good_three.label}."]},
                                    "message" : "Move Error"}

                        source_session_player.good_three_house -= good_three_amount

                    source_session_player.good_one_house -= good_one_amount
                    source_session_player.good_two_house -= good_two_amount 

                    if source_session_player.good_one_house < 0:
                        source_session_player.good_one_house = 0
                    
                    if source_session_player.good_two_house < 0:
                        source_session_player.good_two_house = 0
                    
                    if source_session_player.good_three_house < 0:
                        source_session_player.good_three_house = 0

                else:
                    #check enough good one
                    if round_half_away_from_zero(source_session_player.good_one_field, 0) < good_one_amount:
                        return {"value" : "fail", "errors" : {f"transfer_good_one_amount_{form_type}":[f"Source does not have enough {source_session_player.parameter_set_player.good_one.label}."]},
                                "message" : "Move Error"}
                    
                    #check enough good two
                    if round_half_away_from_zero(source_session_player.good_two_field, 0) < good_two_amount:
                        return {"value" : "fail", "errors" : {f"transfer_good_two_amount_{form_type}":[f"Source does not have enough {source_session_player.parameter_set_player.good_two.label}."]},
                                "message" : "Move Error"}
                    
                    source_session_player.good_one_field -= good_one_amount
                    source_session_player.good_two_field -= good_two_amount

                    if source_session_player.good_one_field < 0:
                        source_session_player.good_one_field = 0

                    if source_session_player.good_two_field < 0:
                        source_session_player.good_two_field = 0

                source_session_player.save()

                #handle target
                target_session_player = session.session_players.get(id=target_id)

                target_session_player.add_good_by_type(good_one_amount, target_type, source_session_player.parameter_set_player.good_one)
                target_session_player.add_good_by_type(good_two_amount, target_type, source_session_player.parameter_set_player.good_two)
                
                if session.parameter_set.good_count == 3 and source_type == "house":
                    target_session_player.add_good_by_type(good_three_amount, target_type, source_session_player.parameter_set_player.good_three)
                
                #record move
                session_player_move = SessionPlayerMove()

                session_player_move.session_period = session.get_current_session_period()
                session_player_move.session_player_source = source_session_player
                session_player_move.session_player_target = target_session_player

                session_player_move.good_one_amount = good_one_amount   
                session_player_move.good_two_amount = good_two_amount
                session_player_move.good_three_amount = good_three_amount        

                session_player_move.time_remaining = session.time_remaining
                session_player_move.current_period_phase = session.current_period_phase

                if source_type == "house":
                    session_player_move.source_container = ContainerTypes.HOUSE
                else:
                    session_player_move.source_container = ContainerTypes.FIELD
                
                if target_type == "house":
                    session_player_move.target_container = ContainerTypes.HOUSE
                else:
                    session_player_move.target_container = ContainerTypes.FIELD

                session_player_move.save()

                #record notice for source player
                transfer_list = []
                if good_one_amount > 0:
                    transfer_list.append(f"{good_one_amount} {source_session_player.parameter_set_player.good_one.get_html()}")
                
                if good_two_amount > 0:
                    transfer_list.append(f"{good_two_amount} {source_session_player.parameter_set_player.good_two.get_html()}")
                
                if good_three_amount > 0:
                    transfer_list.append(f"{good_three_amount} {source_session_player.parameter_set_player.good_three.get_html()}")

                transfer_string = ""
                if len(transfer_list) == 1:
                    transfer_string = f'{transfer_list[0]}'
                elif len(transfer_list) == 2:
                    transfer_string = f'{transfer_list[0]} and {transfer_list[1]}'
                elif len(transfer_list) == 3:
                    transfer_string = f'{transfer_list[0]}, {transfer_list[1]}, and {transfer_list[2]}'
                else:
                    transfer_string = "no goods"

                #check for steal
                if source_session_player != session_player:
                    transfer_string = f"moved {transfer_string} from <u>Person {source_session_player.parameter_set_player.id_label}'s {source_type}</u> to <u>Person {target_session_player.parameter_set_player.id_label}'s {target_type}</u>."
                else:
                    transfer_string = f"moved {transfer_string} from Person {source_session_player.parameter_set_player.id_label}'s {source_type} to Person {target_session_player.parameter_set_player.id_label}'s {target_type}."

                session_player_notice_1 = SessionPlayerNotice()

                session_player_notice_1.session_period = session.get_current_session_period()
                session_player_notice_1.session_player = session_player
                session_player_notice_1.text = f"You {transfer_string}"
                session_player_notice_1.text = session_player_notice_1.text.replace(f"Person {session_player.parameter_set_player.id_label}'s", "your")
                session_player_notice_1.save()

                #record notice for source player if source does not match mover
                if source_session_player != session_player:
                    session_player_notice_2 = SessionPlayerNotice()

                    session_player_notice_2.session_period = session.get_current_session_period()
                    session_player_notice_2.session_player = source_session_player
                    session_player_notice_2.text = f"Person {session_player.parameter_set_player.id_label} {transfer_string}"
                    session_player_notice_2.text = session_player_notice_2.text.replace(f"Person {source_session_player.parameter_set_player.id_label}'s", "your")
                    session_player_notice_2.text = session_player_notice_2.text.replace(f"Person {session_player.parameter_set_player.id_label}'s", "their")
                    session_player_notice_2.save()
                
                if target_session_player != session_player:
                    session_player_notice_3 = SessionPlayerNotice()

                    session_player_notice_3.session_period = session.get_current_session_period()
                    session_player_notice_3.session_player = target_session_player
                    session_player_notice_3.text = f"Person {session_player.parameter_set_player.id_label} {transfer_string}"
                    session_player_notice_3.text = session_player_notice_3.text.replace(f"Person {target_session_player.parameter_set_player.id_label}'s", "your")
                    session_player_notice_3.text = session_player_notice_3.text.replace(f"Person {session_player.parameter_set_player.id_label}'s", "their")
                    session_player_notice_3.save()

        except ObjectDoesNotExist:
            logger.warning(f"take_move_goods session, not found ID: {session_id}")
            return {"value" : "fail", "errors" : {}, "message" : "Move Error"}       
        
        result = []
        session_player = session.session_players.get(id=session_player_id)
        result.append(session_player.json_min(session_player_notice_1))

        if source_session_player != session_player:
            result.append(source_session_player.json_min(session_player_notice_2))

        if target_session_player != session_player:
            result.append(target_session_player.json_min(session_player_notice_3))
        
        
        return {"value" : "success", "result" : result}                      
                                
    logger.info("Invalid session form")
    return {"value" : "fail", "errors" : dict(form.errors.items()), "message" : ""}

def take_chat(session_id, session_player_id, data):
    '''
    take chat from client
    sesson_id : int : id of session
    session_player_id : int : id of session player
    data : json : incoming json data
    '''
    logger = logging.getLogger(__name__) 
    logger.info(f"take chat: {session_id} {session_player_id} {data}")

    recipients = data["recipients"] 
    chat_text = data["text"]

    result = {}
    #result["recipients"] = []

    session = Session.objects.get(id=session_id)
    session_player = session.session_players.get(id=session_player_id)
    
    session_player_chat = SessionPlayerChat()

    session_player_chat.session_player = session_player
    session_player_chat.session_period = session.get_current_session_period()

    if not session.started:
        return  {"value" : "fail", "result" : {}}
        
    if session.finished:
        return {"value" : "fail", "result" : {}}

    if recipients == "all":
        session_player_chat.chat_type = ChatTypes.ALL
    else:
        if not session.parameter_set.private_chat:
            logger.warning(f"take chat: private chat not enabled :{session_id} {session_player_id} {data}")
            return {"value" : "fail",
                    "result" : {"message" : "Private chat not enabled"}}

        session_player_chat.chat_type = ChatTypes.INDIVIDUAL

    result["chat_type"] = session_player_chat.chat_type
    result["recipients"] = []

    session_player_chat.text = chat_text
    session_player_chat.time_remaining = session.time_remaining
    session_player_chat.current_period_phase = session.current_period_phase

    session_player_chat.save()

    session_player_group_list = session_player.get_current_group_list()
    if recipients == "all":
        session_player_chat.session_player_recipients.add(*session_player_group_list)

        result["recipients"] = [i.id for i in session_player_group_list]
    else:
        sesson_player_target = SessionPlayer.objects.get(id=recipients)
        if sesson_player_target in session_player_group_list:
            session_player_chat.session_player_recipients.add(sesson_player_target)
        else:
            session_player_chat.delete()
            logger.warning(f"take chat: chat at none group member : {session_id} {session_player_id} {data}")
            return {"value" : "fail", "result" : {}}

        result["sesson_player_target"] = sesson_player_target.id

        result["recipients"].append(session_player.id)
        result["recipients"].append(sesson_player_target.id)
    
    result["chat_for_subject"] = session_player_chat.json_for_subject()
    result["chat_for_staff"] = session_player_chat.json_for_staff()

    session_player_chat.save()

    return {"value" : "success", "result" : result}

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

def take_production_time(session_id, session_player_id, data):
    '''
    update subjects production time split between good one and two
    '''

    logger = logging.getLogger(__name__) 
    logger.info(f"take production time: {session_id} {session_player_id} {data}")

    try:
        good_one_production_rate =  data["production_slider_one"]
        good_two_production_rate = data["production_slider_two"]
    except KeyError:
        message = "Invalid values."
        logger.warning(f"take production time: {message}")
        return {"value" : "fail", "result" : {}, "message" : message}
    
    if good_one_production_rate + good_two_production_rate != 100:
        message = "Invalid values."
        logger.warning(f"take production time: {message}")
        return {"value" : "fail", "result" : {}, "message" : message}

    try:
        session = Session.objects.get(id=session_id)
        session_player = SessionPlayer.objects.get(id=session_player_id)

        if session.current_period_phase == PeriodPhase.PRODUCTION and \
           session.current_period > 1:

            message = "Not updates during production."
            logger.warning(f"take production time: {message}")
            return {"value" : "fail", "result" : {}, "message" : message}

        session_player.good_one_production_rate = good_one_production_rate
        session_player.good_two_production_rate = good_two_production_rate

        session_player.save()

        return {"value" : "success", "result" : {"good_one_production_rate" : session_player.good_one_production_rate,
                                                 "good_two_production_rate" : session_player.good_two_production_rate }} 
    except ObjectDoesNotExist:      
        return {"value" : "fail", "result" : {}, "message" : "Invalid player."} 

def take_update_groups(session_id, session_player_id):
    '''
    update groups on the client screen
    '''
    logger = logging.getLogger(__name__) 

    try:
        session_player = SessionPlayer.objects.get(id=session_player_id)

        group_list = session_player.get_current_group_list()

        return {"value" : "success",
                "result" : {"session_players" : [p.json_for_subject(session_player) for p in group_list]}}

    except ObjectDoesNotExist:
        logger.warning(f"take_update_groups: session not found, session {session_id}, session_player_id {session_player_id}")
        return {"value" : "fail", "result" : {}, "message" : "Group update error"}

def take_name(session_id, session_player_id, data):
    '''
    take name and student id at end of game
    '''

    logger = logging.getLogger(__name__) 
    logger.info(f"Take name: {session_id} {session_player_id} {data}")

    form_data = data["formData"]
    
    form_data_dict = {}

    for field in form_data:            
        form_data_dict[field["name"]] = field["value"]

    try:
        session = Session.objects.get(id=session_id)
        session_player = session.session_players.get(id=session_player_id)

        logger.info(f'form_data_dict : {form_data_dict}')       

        form = EndGameForm(form_data_dict)
        
        if not session.finished:
            return {"value" : "fail", "errors" : {f"name":["Session not complete."]},
                    "message" : "Move Error"}
        
    except KeyError:
            logger.warning(f"take_name , setup form: {session_player_id}")
            return {"value" : "fail", "errors" : {}, "message" : "Move Error"}

    if form.is_valid():
        #print("valid form") 

        try:        
            session_player.name = form.cleaned_data["name"]
            session_player.student_id = form.cleaned_data["student_id"]

            session_player.save()
        except ObjectDoesNotExist:
            logger.warning(f"take_name : {session_player_id}")
            return {"value" : "fail", "errors" : {}, "message" : "Move Error"}       
        
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

        parameter_set_avatar = session.parameter_set.parameter_set_avatars_a.get(grid_location_row=row, grid_location_col=col)

        if parameter_set_avatar.avatar == None:
            logger.warning(f"blank avatar choosen : {session_player_id}")
            return {"value" : "fail", "errors" : {}, "message" : "Avatar Error"}

        session_player.avatar = parameter_set_avatar.avatar        
        session_player.save()

    except ObjectDoesNotExist:
        logger.warning(f"take_avatar : {session_player_id}")
        return {"value" : "fail", "errors" : {}, "message" : "Avatar Choice Error"}       
    
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
                "session_players" : [p.json_for_subject(session_player) for p in group_list]}

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
        logger.warning(f"take_next_instruction : {session_player_id}")
        return {"value" : "fail", "errors" : {}, "message" : "Move Error"}       
    
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