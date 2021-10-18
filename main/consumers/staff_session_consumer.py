'''
websocket session list
'''
from decimal import Decimal, DecimalException

from asgiref.sync import sync_to_async

import json
import logging

from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder

from main.consumers import SocketConsumerMixin
from main.consumers import get_session

from main.views import StaffSessionView

from main.forms import SessionForm
from main.forms import PeriodForm

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
        message_data = await take_update_session_form(event["message_text"])

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def update_subject_count(self, event):
        '''
        add or remove a buyer or seller
        '''                
        #update subject count
        message_data = {}
        message_data["status"] = await sync_to_async(take_update_subject_count)(event["message_text"])
        message_data["session"] = await get_session(event["message_text"]["sessionID"])

        message = {}
        message["messageType"] = "update_session"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def update_period_count(self, event):
        '''
        change the number of periods in a session
        '''
        #update subject count
        message_data = {}
        message_data["status"] = await sync_to_async(take_update_period_count)(event["message_text"])

        message_data["session"] = await get_session(event["message_text"]["sessionID"])

        message = {}
        message["messageType"] = "update_session"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def update_period(self, event):
        '''
        update a period parameters
        '''
        #update subject count
        message_data = {}
        message_data["status"] = await sync_to_async(take_update_period)(event["message_text"])

        message_data["session"] = await get_session(event["message_text"]["sessionID"])

        message = {}
        message["messageType"] = "update_period"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def import_parameters(self, event):
        '''
        import parameters from another session
        '''
        #update subject count
        message_data = {}
        message_data["status"] = await sync_to_async(take_import_parameters)(event["message_text"])

        message_data["session"] = await get_session(event["message_text"]["sessionID"])

        message = {}
        message["messageType"] = "import_parameters"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def download_parameters(self, event):
        '''
        download parameters to a file
        '''
        #download parameters to a file
        message = {}
        message["messageType"] = "download_parameters"
        message["messageData"] = await take_download_parameters(event["message_text"])

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
    
#local sync_to_asyncs
@sync_to_async
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

def take_update_subject_count(data):
    '''
    take update to buyer or seller count for sessio
    param: data {"type":"buyer or seller","adjustment":"-1 or 1"} update to buyer or seller count
    '''
    logger = logging.getLogger(__name__) 
    logger.info(f"Update Buyer or Seller count: {data}")

    subject_type = data["type"]
    adjustment = data["adjustment"]
    session_id = data["sessionID"]

    session = Session.objects.get(id=session_id)

    parameter_set = session.parameter_set

    if parameter_set == None:
        return "fail"

    if subject_type == "SELLER":
        if adjustment == 1:
           parameter_set.number_of_sellers += 1
        elif parameter_set.number_of_sellers > 1 :
            parameter_set.number_of_sellers -= 1
        else:
            return "fail"
    else:
        if adjustment == 1:
           parameter_set.number_of_buyers += 1
        elif parameter_set.number_of_buyers > 1 :
            parameter_set.number_of_buyers -= 1
        else:
            return "fail"    

    parameter_set.save()
    
    return parameter_set.update_subject_counts()

def take_update_period_count(data):
    '''
    update the number of periods
    '''   

    logger = logging.getLogger(__name__) 
    logger.info(f"Update period count: {data}")

    adjustment = data["adjustment"]
    session_id = data["sessionID"]

    session = Session.objects.get(id=session_id)

    parameter_set = session.parameter_set

    if adjustment == 1:
        return parameter_set.add_session_period()
    else:
        return parameter_set.remove_session_period()

def take_update_period(data):
    '''
    update period parameters
    '''   

    logger = logging.getLogger(__name__) 
    logger.info(f"Update period parameters: {data}")

    session_id = data["sessionID"]
    period_id = data["periodID"]

    form_data = data["formData"]

    try:        
        session_period = ParameterSetPeriod.objects.get(id=period_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_update_period session period, not found ID: {period_id}")
    
    form_data_dict = {}

    for field in form_data:            
        form_data_dict[field["name"]] = field["value"]

    form = PeriodForm(form_data_dict, instance=session_period)

    if form.is_valid():
        #print("valid form")                
        form.save()              

        return {"value" : "success"}                      
                                
    logger.info("Invalid session form")
    return {"value" : "fail", "errors" : dict(form.errors.items())}

def take_import_parameters(data):
    '''
    import parameters from another session
    '''   
    logger = logging.getLogger(__name__) 
    logger.info(f"Import parameters: {data}")

    session_id = data["sessionID"]
    form_data = data["formData"]
    
    form_data_dict = {}

    for field in form_data:            
        form_data_dict[field["name"]] = field["value"]

    source_session = Session.objects.get(id=form_data_dict["session"])
    target_session = Session.objects.get(id=session_id)

    return target_session.parameter_set.from_dict(source_session.parameter_set.json())          

    # return {"value" : "fail" if "Failed" in message else "success",
    #         "message" : message}

@sync_to_async
def take_download_parameters(data):
    '''
    download parameters to a file
    '''   
    logger = logging.getLogger(__name__) 
    logger.info(f"Download parameters: {data}")

    session_id = data["sessionID"]

    session = Session.objects.get(id=session_id)
   
    return {"status" : "success", "parameter_set":session.parameter_set.json()}                      
                                
@sync_to_async
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

@sync_to_async
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


    '''
    take add to all values or costs
    '''   

    logger = logging.getLogger(__name__) 
    logger.info(f"Take add to all values or costs: {data}")

    session_id = data["sessionID"]
    period = data["currentPeriod"]
    values_or_costs = data["valueOrCost"]
    amount = data["amount"]

    session = Session.objects.get(id=session_id)
    parameter_set = session.parameter_set

    #check amount is a valid deciamal amount
    try:
        amount = Decimal(amount)
    except DecimalException: 
              
        message = f"Error: Invalid amount, not a decimal."
        logger.warning(f'take_submit_bid_offer: {message}')

        return "fail"

    status = parameter_set.add_to_values_or_costs(values_or_costs, period, amount)

    return status