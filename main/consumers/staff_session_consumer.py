'''
websocket session list
'''
from asgiref.sync import sync_to_async

import json
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.db import transaction

from main.consumers import SocketConsumerMixin
from main.consumers import get_session

from main.forms import SessionForm
from main.forms import SessionPlayerMoveTwoForm
from main.forms import SessionPlayerMoveThreeForm

from main.models import Session

class StaffSessionConsumer(SocketConsumerMixin):
    '''
    websocket session list
    '''    

    async def get_session(self, event):
        '''
        return a list of sessions
        '''
        logger = logging.getLogger(__name__) 
        logger.info(f"Get Session {event}")

        #build response
        message_data = {}
        message_data["session"] = await get_session(event["message_text"]["sessionID"])

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message,}, cls=DjangoJSONEncoder))
    
    async def update_session(self, event):
        '''
        return a list of sessions
        '''
        logger = logging.getLogger(__name__) 
        logger.info(f"Update Session: {event}")

        #build response
        message_data = {}
        message_data =  await sync_to_async(take_update_session_form)(event["message_text"])

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def start_experiment(self, event):
        '''
        start experiment
        '''
        #update subject count
        message_data = {}
        message_data["status"] = await take_start_experiment(event["message_text"])
        message_data["session"] = await get_session(event["message_text"]["sessionID"])

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def reset_experiment(self, event):
        '''
        reset experiment, removes all trades, bids and asks
        '''
        #update subject count
        message_data = {}
        message_data["status"] = await take_reset_experiment(event["message_text"])
        message_data["session"] = await get_session(event["message_text"]["sessionID"])

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def next_period(self, event):
        '''
        advance to next period in experiment
        '''
        #update subject count
        message_data = {}
        message_data["data"] = await sync_to_async(take_next_period)(event["message_text"])

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def move_goods(self, event):
        '''
        advance to next period in experiment
        '''
        #update subject count
        message_data = {}
        message_data["status"] = await sync_to_async(take_move_goods)(event["message_text"])

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))


#local sync functions    
def take_update_session_form(data):
    '''
    take session form data and update session or return errors
    param: data {json} incoming form and session data
    '''

    logger = logging.getLogger(__name__)
    logger.info(f'take_update_session_form: {data}')

    session_id = data["sessionID"]
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

def take_start_experiment(data):
    '''
    start experiment
    '''   

    logger = logging.getLogger(__name__) 
    logger.info(f"Start Experiment: {data}")

    session_id = data["sessionID"]
    session = Session.objects.get(id=session_id)

    if not session.started:
        session.start_experiment()

    status = "success"
    
    return {"status" : status}

def take_reset_experiment(data):
    '''
    reset experiment remove bids and asks
    '''   

    logger = logging.getLogger(__name__) 
    logger.info(f"Reset Experiment: {data}")

    session_id = data["sessionID"]
    session = Session.objects.get(id=session_id)

    if session.started:
        session.started = False
        session.finished = False
        session.current_period = 1

        session.save()
        session.session_periods.all().delete()  
        session.session_subjects.all().delete() 

    status = "success"
    
    return {"status" : status}

def take_next_period(data):
    '''
    advance to next period in the experiment
    '''   

    logger = logging.getLogger(__name__) 
    logger.info(f"Advance to Next Period: {data}")

    session_id = data["sessionID"]
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

def take_move_goods(data):
    '''
    move goods between locations (house or field)
    '''

    logger = logging.getLogger(__name__) 
    logger.info(f"Move goods: {data}")

    session_id = data["sessionID"]

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

       
        form_type = ""       #form suffix for 2 or three goods        
        if source_type == "house" and session.parameter_set.good_count == 3:
            form = SessionPlayerMoveThreeForm(form_data_dict)
            form_type = "3g"
        else:
            form = SessionPlayerMoveTwoForm(form_data_dict)
            form_type = "2g"
        
    except KeyError:
            logger.warning(f"take_move_goods session, setup form: {session_id}")
            return {"value" : "fail", "errors" : {}, "message" : "Move Error"}

    if form.is_valid():
        #print("valid form") 

        try:        
            with transaction.atomic():

                source_session_player = session.session_players.get(id=source_id)              
                target_session_player = session.session_players.get(id=target_id)

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
                    #check enough good one
                    if source_session_player.good_one_house < good_one_amount:
                        return {"value" : "fail", "errors" : {}, "message" : "Source Error Good One"}
                    
                    #check enough good two
                    if source_session_player.good_two_house < good_two_amount:
                        return {"value" : "fail", "errors" : {}, "message" : "Source Error Good Two"}

                    source_session_player.good_one_house -= good_one_amount
                    source_session_player.good_two_house -= good_two_amount

                    if session.parameter_set.good_count == 3:
                        source_session_player.good_three_house -= good_three_amount

                else:
                    #check enough good one
                    if source_session_player.good_one_field < good_one_amount:
                        return {"value" : "fail", "errors" : {}, "message" : "Source Error Good One"}
                    
                    #check enough good two
                    if source_session_player.good_two_field < good_two_amount:
                        return {"value" : "fail", "errors" : {}, "message" : "Source Error Good Two"}
                    
                    source_session_player.good_one_field -= good_one_amount
                    source_session_player.good_two_field -= good_two_amount

                source_session_player.save()

                #handle target
                target_session_player = session.session_players.get(id=target_id)

                target_session_player.add_good_by_type(good_one_amount, target_type, source_session_player.parameter_set_player.good_one)
                target_session_player.add_good_by_type(good_two_amount, target_type, source_session_player.parameter_set_player.good_two)
                
                if session.parameter_set.good_count == 3 and source_type == "house":
                    target_session_player.add_good_by_type(good_three_amount, target_type, source_session_player.parameter_set_player.good_three)
                
        except ObjectDoesNotExist:
            logger.warning(f"take_move_goods session, not found ID: {session_id}")
            return {"value" : "fail", "errors" : {}, "message" : "Move Error"}       
        
        result = []
        result.append(source_session_player.json_min())
        result.append(target_session_player.json_min())
        
        return {"value" : "success", "result" : result}                      
                                
    logger.info("Invalid session form")
    return {"value" : "fail", "errors" : dict(form.errors.items()), "message" : ""}
