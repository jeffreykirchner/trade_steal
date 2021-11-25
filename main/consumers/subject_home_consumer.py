'''
websocket session list
'''
from asgiref.sync import sync_to_async

import json
import logging

from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction

from main.consumers import SocketConsumerMixin
from main.consumers import StaffSubjectUpdateMixin
from main.consumers import get_session

from main.forms import SessionPlayerMoveTwoForm
from main.forms import SessionPlayerMoveThreeForm

from main.models import Session
from main.models import SessionPlayer
from main.models import SessionPlayerMove
from main.models import SessionPlayerChat

from main.globals import ContainerTypes
from main.globals import ChatTypes

class SubjectHomeConsumer(SocketConsumerMixin, StaffSubjectUpdateMixin):
    '''
    websocket session list
    '''    

    group_number = 0      #group number player subject is in
    town_number = 0       #town number subject is in 

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

        result = await sync_to_async(take_get_session_subject)(self.connection_uuid)

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
        result = await sync_to_async(take_move_goods)(self.session_id, self.connection_uuid, event["message_text"])

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
                 'sender_group' : self.group_number},
            )
        
    async def chat(self, event):
        '''
        take chat from client
        '''
        #update subject count
        result = await sync_to_async(take_chat)(self.session_id, self.connection_uuid, event["message_text"])

        message_data = {}
        message_data["status"] = result

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        # Send reply to sending channel
        

        #if success send to all connected clients
        if result["value"] == "fail":
            await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
        elif result["value"] == "success":
            await self.channel_layer.group_send(
                self.room_group_name,
                {"type": "update_chat",
                 "data": result,
                 'sender_group' : self.group_number,
                 'sender_channel_name': self.channel_name},
            )
    
    async def update_start_experiment(self, event):
        '''
        start experiment on subjects
        '''
        #logger = logging.getLogger(__name__) 
        #logger.info(f'update start subjects {self.channel_name}')

        #get session json object
        result = await sync_to_async(take_get_session_subject)(self.connection_uuid)

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
        result = await sync_to_async(take_get_session_subject)(self.connection_uuid)

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
        result = event["data"]

        message_data = {}
        message_data["status"] = result

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        if self.group_number != event['sender_group']:
            return

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def update_local_info(self, event):
        '''
        update connection's town and group information
        '''
        result = await sync_to_async(take_update_local_info)(self.session_id, self.connection_uuid, event["message_text"])

        logger = logging.getLogger(__name__) 
        logger.info(f"update_local_info {result}")

        self.group_number = result["group_number"]
        self.town_number = result["town_number"]
    
    async def update_move_goods(self, event):
        '''
        update good count on all but sender
        '''
        logger = logging.getLogger(__name__) 
        logger.info(f'update_goods{self.channel_name}')

        message_data = {}
        message_data["status"] = event["data"]

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        if self.channel_name == event['sender_channel_name']:
            return

        if self.group_number != event['sender_group']:
            return

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

#local sync functions  
def take_get_session_subject(player_key):
    '''
    get session info for subject
    '''
    #session_id = data["sessionID"]
    #uuid = data["uuid"]

    #session = Session.objects.get(id=session_id)
    session_player = SessionPlayer.objects.get(player_key=player_key)

    return {"session" : session_player.session.json_for_subject(session_player), 
            "session_player" : session_player.json() }

def take_get_session_id(player_key):
    '''
    get the session id for the player_key
    '''
    session_player = SessionPlayer.objects.get(player_key=player_key)

    return session_player.session.id
  
def take_move_goods(session_id, player_key, data):
    '''
    move goods between locations (house or field)
    '''

    logger = logging.getLogger(__name__) 
    logger.info(f"Move goods: {session_id} {player_key} {data}")

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
        session_player = session.session_players.get(player_key=player_key)

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
                    if source_session_player.good_one_house < good_one_amount:
                         return {"value" : "fail", "errors" : {f"transfer_good_one_amount_{form_type}":[f"Source does not have enough {source_session_player.parameter_set_player.good_one.label}."]},
                                "message" : "Move Error"}
                    
                    #check enough good two
                    if source_session_player.good_two_house < good_two_amount:
                        return {"value" : "fail", "errors" : {f"transfer_good_two_amount_{form_type}":[f"Source does not have enough {source_session_player.parameter_set_player.good_two.label}."]},
                                "message" : "Move Error"}

                    if session.parameter_set.good_count == 3:
                        if source_session_player.good_three_house < good_three_amount:
                            return {"value" : "fail", "errors" : {f"transfer_good_three_amount_{form_type}":[f"Source does not have enough {source_session_player.parameter_set_player.good_three.label}."]},
                                    "message" : "Move Error"}

                        source_session_player.good_three_house -= good_three_amount

                    source_session_player.good_one_house -= good_one_amount
                    source_session_player.good_two_house -= good_two_amount 

                else:
                    #check enough good one
                    if source_session_player.good_one_field < good_one_amount:
                        return {"value" : "fail", "errors" : {f"transfer_good_one_amount_{form_type}":[f"Source does not have enough {source_session_player.parameter_set_player.good_one.label}."]},
                                "message" : "Move Error"}
                    
                    #check enough good two
                    if source_session_player.good_two_field < good_two_amount:
                        return {"value" : "fail", "errors" : {f"transfer_good_two_amount_{form_type}":[f"Source does not have enough {source_session_player.parameter_set_player.good_two.label}."]},
                                "message" : "Move Error"}
                    
                    source_session_player.good_one_field -= good_one_amount
                    source_session_player.good_two_field -= good_two_amount

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

                if source_type == "house":
                    session_player_move.source_container = ContainerTypes.HOUSE
                else:
                    session_player_move.source_container = ContainerTypes.FIELD
                
                if target_type == "house":
                    session_player_move.target_container = ContainerTypes.HOUSE
                else:
                    session_player_move.target_container = ContainerTypes.FIELD

                session_player_move.save()
                
        except ObjectDoesNotExist:
            logger.warning(f"take_move_goods session, not found ID: {session_id}")
            return {"value" : "fail", "errors" : {}, "message" : "Move Error"}       
        
        result = []
        result.append(source_session_player.json_min())
        result.append(target_session_player.json_min())
        
        return {"value" : "success", "result" : result}                      
                                
    logger.info("Invalid session form")
    return {"value" : "fail", "errors" : dict(form.errors.items()), "message" : ""}

def take_chat(session_id, player_key, data):
    '''
    take chat from client
    sesson_id : int : id of session
    player_key : uuid : uuid of session player
    data : json : incoming json data
    '''
    logger = logging.getLogger(__name__) 
    logger.info(f"take chat: {session_id} {player_key} {data}")

    recipients = data["recipients"] 
    chat_text = data["text"]

    result = {}

    session = Session.objects.get(id=session_id)
    session_player = session.session_players.get(player_key=player_key)
    
    session_player_chat = SessionPlayerChat()

    session_player_chat.session_player = session_player
    session_player_chat.session_period = session.get_current_session_period()

    if recipients == "all":
        session_player_chat.chat_type = ChatTypes.ALL
    else:
        session_player_chat.chat_type = ChatTypes.INDIVIDUAL

    session_player_chat.text = chat_text

    session_player_chat.save()

    session_player_group_list = session_player.get_current_group_list()
    if recipients == "all":
        session_player_chat.session_player_recipients.add(*session_player_group_list)
    else:
        sesson_player_target = SessionPlayer.objects.get(id=recipients)
        if sesson_player_target in session_player_group_list:
            session_player_chat.session_player_recipients.add(sesson_player_target)
        else:
            session_player_chat.delete()
            return {"value" : "fail", "result" : {}}

    session_player_chat.save()

    return {"value" : "success", "result" : result}

def take_update_local_info(session_id, player_key, data):
    '''
    update connection's town and group information
    '''

    session_player = SessionPlayer.objects.get(player_key=player_key)

    return {"group_number" : session_player.get_current_group_number(), 
            "town_number" : session_player.get_current_town_number() }
     