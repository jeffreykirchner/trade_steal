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

class SubjectHomeConsumer(SocketConsumerMixin, StaffSubjectUpdateMixin):
    '''
    websocket session list
    '''    

    async def get_session(self, event):
        '''
        return a list of sessions
        '''
        logger = logging.getLogger(__name__) 
        logger.info(f"Get Session {event}")

        self.connection_uuid = event["message_text"]["playerKey"]
        self.connection_type = "subject"
        self.session_id = await sync_to_async(take_get_session_id)(self.connection_uuid)

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
        advance to next period in experiment
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


def take_get_session_subject(player_key):
    '''
    get session info for subject
    '''
    #session_id = data["sessionID"]
    #uuid = data["uuid"]

    #session = Session.objects.get(id=session_id)
    session_player = SessionPlayer.objects.get(player_key=player_key)

    return {"session" : session_player.session.json_for_subject(), 
            "session_player" : session_player.json() }

def take_get_session_id(player_key):
    '''
    get the session id for the player_key
    '''
    session_player = SessionPlayer.objects.get(player_key=player_key)

    return session_player.session.id

#local sync functions    
def take_move_goods(session_id, player_key, data):
    '''
    move goods between locations (house or field)
    '''

    logger = logging.getLogger(__name__) 
    logger.info(f"Move goods: {data}")

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
                # session_player_move = SessionPlayerMove()
                # session_player_move.save()
                
        except ObjectDoesNotExist:
            logger.warning(f"take_move_goods session, not found ID: {session_id}")
            return {"value" : "fail", "errors" : {}, "message" : "Move Error"}       
        
        result = []
        result.append(source_session_player.json_min())
        result.append(target_session_player.json_min())
        
        return {"value" : "success", "result" : result}                      
                                
    logger.info("Invalid session form")
    return {"value" : "fail", "errors" : dict(form.errors.items()), "message" : ""}