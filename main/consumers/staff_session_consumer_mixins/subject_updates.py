
from asgiref.sync import sync_to_async

import json
import logging

from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.utils.html import strip_tags

from main.models import Session
from main.models import SessionPlayer
from main.models import SessionPlayerChat

from main.globals import ChatTypes
from main.globals import ContainerTypes
from main.globals import PeriodPhase
from main.globals import round_half_away_from_zero

from main.models import SessionPlayerMove
from main.models import SessionPlayerNotice

from main.forms import SessionPlayerMoveTwoForm
from main.forms import SessionPlayerMoveThreeForm


import main

class SubjectUpdatesMixin():
    '''
    subject updates mixin for staff session consumer
    '''

    #actions from clients
    async def chat(self, event):
        '''
        take chat from client
        '''
        if self.controlling_channel != self.channel_name:
            return
        
        logger = logging.getLogger(__name__)
        # logger.info(f'chat {event}')

        status = "success"
        message = ""
        player_id = None
        result = {}

        try:
            player_id = self.session_players_local[event["player_key"]]["id"]
            event_data = event["message_text"]
            recipients = event_data["recipients"] 
            chat_text = strip_tags(event_data["text"])
        except:
            logger.warning(f"chat: invalid data, {event['message_text']}")
            status = "fail"
            message = "Invalid data."
        
        if status == "success":
            target_list = [player_id]
            result["session_player_id"] = player_id

        session = await Session.objects.aget(id=self.session_id)
        #session_player = await session.session_players.aget(id=player_id)
        parameter_set_player_id = self.world_state_local["session_players"][str(player_id)]["parameter_set_player_id"]
        parameter_set_player = self.parameter_set_local["parameter_set_players"][str(parameter_set_player_id)]
       
        if status == "success":
            if not session.started:
                status = "fail"
                message = "Session not started."
        
        if status == "success":
            if session.finished:
                status = "fail"
                message = "Session finished."

        if status == "success":
            if session.current_experiment_phase != main.globals.ExperimentPhase.RUN:
                status = "fail"
                message = "Session not running."
        
        if status == "success":
            parameter_set = self.parameter_set_local
            current_session_period = await session.aget_current_session_period()

            session_player_chat = SessionPlayerChat()

            session_player_chat.session_player_id = player_id
            session_player_chat.session_period = current_session_period

            if recipients == "all":
                if not parameter_set["group_chat"]:
                    logger.warning(f"take chat: group chat not enabled :{self.session_id} {player_id} {event_data}")
                    status = "fail"
                    message = "Group chat not allowed."

                session_player_chat.chat_type = ChatTypes.ALL
            else:
                if not parameter_set["private_chat"]:
                    logger.warning(f"take chat: private chat not enabled :{self.session_id} {player_id} {event_data}")
                    status = "fail"
                    message = "Private chat not allowed."

                session_player_chat.chat_type = ChatTypes.INDIVIDUAL

            if status == "success":
                result["chat_type"] = session_player_chat.chat_type
                result["recipients"] = []

                session_player_chat.text = chat_text
                session_player_chat.time_remaining = session.time_remaining
                session_player_chat.current_period_phase = session.current_period_phase

                await session_player_chat.asave()

                parameter_set_player_group = await self.get_player_group(player_id, session.current_period)
                group_members = await self.get_group_members(parameter_set_player_group, session.current_period)
                
                # session_player_group_list = session_player.get_current_group_list()

                if recipients == "all":
                    await session_player_chat.session_player_recipients.aadd(*group_members)

                    result["recipients"] = group_members
                else:
                    sesson_player_target_id = recipients
                    
                    if str(sesson_player_target_id) in group_members:
                        await session_player_chat.session_player_recipients.aadd(sesson_player_target_id)
                    else:
                        await session_player_chat.adelete()
                        logger.warning(f"take chat: chat at none group member : {self.session_id} {player_id} {event_data}")
                        status = "fail"
                        message = "Player not in group."
                        
                    if status == "success":
                        result["sesson_player_target"] = sesson_player_target_id

                        # result["recipients"].append(player_id)
                        parameter_set_id_target = self.world_state_local["session_players"][str(sesson_player_target_id)]["parameter_set_player_id"]
                        parameter_set_player_target = self.parameter_set_local["parameter_set_players"][str(parameter_set_id_target)]
                        result["recipients"].append(parameter_set_player_target["id_label"])

                if status == "success":
                    result["chat"] = {"id" : session_player_chat.id,
                                      "sender_label" : parameter_set_player["id_label"],
                                      "sender_id" : player_id,
                                      "text" : chat_text,
                                      "session_player_recipients" :  result["recipients"],
                                      "chat_type" : session_player_chat.chat_type}   
                    
                    self.world_state_local["chat_all"][str(parameter_set_player["town"])].append(result["chat"])
                    if len(self.world_state_local["chat_all"][str(parameter_set_player["town"])]) > 100:
                           self.world_state_local["chat_all"][str(parameter_set_player["town"])].pop(0)

                    await self.store_world_state(force_store=True)
                    await session_player_chat.asave()

                    if recipients == "all":
                        target_list = group_members
                    else:
                        target_list = [str(sesson_player_target_id), str(player_id)]

        result["status"] = status
        result["message"] = message
        result["town"] = parameter_set_player["town"]

        await self.send_message(message_to_self=None, message_to_group=result,
                                message_type=event['type'], send_to_client=False,
                                send_to_group=True, target_list=target_list)

    async def move_goods(self, event):
        '''
        move goods between two containers
        '''

        logger = logging.getLogger(__name__)

        status = "success"
        message = ""
        target_list = []
        player_id = None

        try:
            session = await Session.objects.aget(id=self.session_id)
            player_id = self.session_players_local[event["player_key"]]["id"]
            event_data = event["message_text"]
            target_list = [player_id]
        except:
            logger.warning(f"move_goods: invalid data, {event['message_text']}")
            status = "fail"
            message = "Invalid data."
            target_list = [player_id]

        if status == "success":
            result = await sync_to_async(take_move_goods)(self.session_id, player_id, event_data)

            # Send reply to sending channel
            # await self.send_message(message_to_self=result, message_to_group=None,
            #                         message_type=event['type'], send_to_client=True, send_to_group=False)

            result["session_player_id"] = player_id

            #if success send to all connected clients
            if result["value"] == "success":
                parameter_set_player_group = await self.get_player_group(player_id, session.current_period)
                group_members = await self.get_group_members(parameter_set_player_group, session.current_period)
                target_list = group_members

            await self.send_message(message_to_self=None, message_to_group=result,
                                    message_type=event['type'], send_to_client=False, 
                                    send_to_group=True, target_list=target_list)
       
            # result = {"value" : "fail", "errors" : {}, "message" : message}

            # await self.send_message(message_to_self=None, message_to_group=group_result,
            #                         message_type=event['type'], send_to_client=False, 
            #                         send_to_group=True, target_list=target_list)

    #update functions
    async def update_chat(self, event):
        '''
        send chat to clients, if clients can view it
        '''
        result =  json.loads(event["group_data"])

        if(result["status"] == "fail"):
            return

        await self.send_message(message_to_self=result, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

    async def update_move_goods(self, event):
        '''
        update good count staff
        '''
        # logger = logging.getLogger(__name__) 
        # logger.info(f'update_goods{self.channel_name}')

        result =  json.loads(event["group_data"])
        
        if(result["value"] == "fail"):
            return

        result = json.loads(event["group_data"])

        await self.send_message(message_to_self=result, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

    async def update_groups(self, event)  :
        '''
        update groups on client
        '''

        result = await sync_to_async(take_update_groups)(self.session_id)

        await self.send_message(message_to_self=result, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

    async def update_connection_status(self, event):
        '''
        handle connection status update from group member
        '''
        # logger = logging.getLogger(__name__) 
        # logger.info("Connection update")

        #update not from a client
        if event["data"]["value"] == "fail":
            if not self.session_id:
                self.session_id = event["session_id"]

            # logger.info(f"update_connection_status: event data {event}, channel name {self.channel_name}, group name {self.room_group_name}")

            if "session" in self.room_group_name:
                #connection from staff screen
                if event["connect_or_disconnect"] == "connect":
                    # session = await Session.objects.aget(id=self.session_id)
                    self.controlling_channel = event["sender_channel_name"]

                    if self.channel_name == self.controlling_channel:
                        # logger.info(f"update_connection_status: controller {self.channel_name}, session id {self.session_id}")
                        await Session.objects.filter(id=self.session_id).aupdate(controlling_channel=self.controlling_channel) 

                        result = {"controlling_channel" : self.controlling_channel}
                        await self.send_message(message_to_self=None, message_to_group=result,
                                                message_type="set_controlling_channel", send_to_client=False, send_to_group=True)
            
                else:
                    #disconnect from staff screen
                    pass
            
            return

        result = event["data"]

        #get subject name and student id
        subject_id = result["result"]["id"]

        session_player = await SessionPlayer.objects.aget(id=subject_id)
        result["result"]["name"] = session_player.name
        result["result"]["student_id"] = session_player.student_id
        result["result"]["current_instruction"] = session_player.current_instruction
        result["result"]["survey_complete"] = session_player.survey_complete
        result["result"]["instructions_finished"] = session_player.instructions_finished

        await self.send_message(message_to_self=result, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

    async def update_name(self, event):
        '''
        send update name notice to staff screens
        '''

        # logger = logging.getLogger(__name__) 
        # logger.info("Eng game update")

        result =  json.loads(event["group_data"])

        await self.send_message(message_to_self=result, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

    async def update_avatar(self, event):
        '''
        send update avatar notice to staff screens
        '''

        # logger = logging.getLogger(__name__) 
        # logger.info("Eng game update")

        result =  json.loads(event["group_data"])

        await self.send_message(message_to_self=result, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

    async def update_next_instruction(self, event):
        '''
        send instruction status to staff
        '''

        # logger = logging.getLogger(__name__) 
        # logger.info("Eng game update")

        result =  json.loads(event["group_data"])

        await self.send_message(message_to_self=result, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

    async def update_finish_instructions(self, event):
        '''
        send instruction status to staff
        '''

        # logger = logging.getLogger(__name__) 
        # logger.info("Eng game update")

        result =  json.loads(event["group_data"])

        await self.send_message(message_to_self=result, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

    async def update_production_time(self, event):
        '''
        send production settings update
        '''

        # logger = logging.getLogger(__name__) 
        # logger.info("Eng game update")

        result =  json.loads(event["group_data"])

        await self.send_message(message_to_self=result, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

def take_update_groups(session_id):
    '''
    take update groups
    '''

    session = Session.objects.get(id=session_id)

    status = "success"
    
    return {"status" : status,
            "group_list" : session.json_for_group_update()}

def take_move_goods(session_id, session_player_id, data):
    '''
    move goods between locations (house or field)
    '''

    logger = logging.getLogger(__name__) 
    # logger.info(f"Move goods: {session_id} {session_player_id} {data}")

    try:
        form_data = data["formData"]
    
        form_data_dict = form_data

        # logger.info(f'form_data_dict : {form_data_dict}')       

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
        
        if session.current_experiment_phase != main.globals.ExperimentPhase.RUN:
            return {"value" : "fail", "errors" : {f"transfer_good_one_amount_{form_type}":["Session is not running."]},
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
            return {"value" : "fail",
                    "errors" : {f"transfer_good_one_amount_2g":[f"Move failed."], f"transfer_good_one_amount_3g":[f"Move failed."]}, 
                    "message" : "Move Error",}

    if form.is_valid():
        #print("valid form") 

        try:        
            with transaction.atomic():

                source_session_player = session.session_players.select_for_update().get(id=source_id)              
                target_session_player = session.session_players.select_for_update().get(id=target_id)

                #check that stealing is allowed
                if not session.parameter_set.allow_stealing and source_session_player != session_player:
                    return {"value" : "fail", "errors" : {f"transfer_good_one_amount_{form_type}":[f"Invalid source."]},
                            "message" : "Invalid source."}

                good_one_amount = form.cleaned_data[f"transfer_good_one_amount_{form_type}"]
                good_two_amount = form.cleaned_data[f"transfer_good_two_amount_{form_type}"]
                good_three_amount = 0

                if good_one_amount == 0 and good_two_amount == 0:
                    return {"value" : "fail", "errors" : {f"transfer_good_one_amount_{form_type}":[f"Nothing to transfer."]},
                            "message" : "Move error."}

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
                         return {"value" : "fail", "errors" : {f"transfer_good_one_amount_{form_type}":[f"House does not have enough {source_session_player.parameter_set_player.good_one.label}."]},
                                "message" : "Move Error"}
                    
                    #check enough good two
                    if round_half_away_from_zero(source_session_player.good_two_house, 0) < good_two_amount:
                        return {"value" : "fail", "errors" : {f"transfer_good_two_amount_{form_type}":[f"House does not have enough {source_session_player.parameter_set_player.good_two.label}."]},
                                "message" : "Move Error"}

                    if round_half_away_from_zero(session.parameter_set.good_count, 0) == 3:
                        if source_session_player.good_three_house < good_three_amount:
                            return {"value" : "fail", "errors" : {f"transfer_good_three_amount_{form_type}":[f"House does not have enough {source_session_player.parameter_set_player.good_three.label}."]},
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
                        return {"value" : "fail", "errors" : {f"transfer_good_one_amount_{form_type}":[f"Field does not have enough {source_session_player.parameter_set_player.good_one.label}."]},
                                "message" : "Move Error"}
                    
                    #check enough good two
                    if round_half_away_from_zero(source_session_player.good_two_field, 0) < good_two_amount:
                        return {"value" : "fail", "errors" : {f"transfer_good_two_amount_{form_type}":[f"Field does not have enough {source_session_player.parameter_set_player.good_two.label}."]},
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
                session_player_notice_1.show_on_staff = True
                session_player_notice_1.save()

                session_player.session.world_state["notices"][str(session_player.parameter_set_player.town)].append(session_player_notice_1.json())

                if len(session_player.session.world_state["notices"][str(session_player.parameter_set_player.town)]) > 100:
                    session_player.session.world_state["notices"][str(session_player.parameter_set_player.town)].pop(0)

                session_player.session.save()

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
