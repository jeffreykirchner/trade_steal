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

from main.forms import SessionForm
from main.forms import ParameterSetForm
from main.forms import ParameterSetTypeForm
from main.forms import ParameterSetPlayerForm
from main.forms import ParameterSetPlayerGroupForm
from main.forms import SessionPlayerMoveForm

from main.models import Session
from main.models import ParameterSetType
from main.models import ParameterSetPlayer
from main.models import ParameterSetPlayerGroup

import main

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
    
    async def update_parameterset(self, event):
        '''
        update a parameterset
        '''
        #build response
        message_data = {}
        message_data["status"] = await sync_to_async(take_update_parameterset)(event["message_text"])
        message_data["session"] = await get_session(event["message_text"]["sessionID"])

        message = {}
        message["messageType"] = "update_parameterset"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def update_parameterset_type(self, event):
        '''
        update a parameterset type
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_update_parameterset_type)(event["message_text"])
        message_data["session"] = await get_session(event["message_text"]["sessionID"])

        message = {}
        message["messageType"] = "update_parameterset_type"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def update_parameterset_player(self, event):
        '''
        update a parameterset player
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_update_parameterset_player)(event["message_text"])
        message_data["session"] = await get_session(event["message_text"]["sessionID"])

        message = {}
        message["messageType"] = "update_parameterset_player"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder)) 

    async def remove_parameterset_player(self, event):
        '''
        remove a parameterset player
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_remove_parameterset_player)(event["message_text"])
        message_data["session"] = await get_session(event["message_text"]["sessionID"])

        message = {}
        message["messageType"] = "remove_parameterset_player"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))   
    
    async def add_parameterset_player(self, event):
        '''
        add a parameterset player
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_add_paramterset_player)(event["message_text"])
        message_data["session"] = await get_session(event["message_text"]["sessionID"])

        message = {}
        message["messageType"] = "add_parameterset_player"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def update_parameterset_player_group(self, event):
        '''
        update a parameterset group
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_update_parameterset_player_group)(event["message_text"])
        message_data["session"] = await get_session(event["message_text"]["sessionID"])

        message = {}
        message["messageType"] = "update_parameterset_player_group"
        message["messageData"] = message_data

        # Send message to WebSocket
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder)) 
    
    async def copy_group_forward(self, event):
        '''
        copy groupds forward from the specified period
        '''
        message_data = {}
        message_data["status"] = await sync_to_async(take_copy_groups_forward)(event["message_text"])
        message_data["session"] = await get_session(event["message_text"]["sessionID"])

        message = {}
        message["messageType"] = "copy_group_forward"
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
        message["messageData"] = await sync_to_async(take_download_parameters)(event["message_text"])

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
        message_data["data"] = await sync_to_async(take_move_goods)(event["message_text"])

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

def take_update_parameterset(data):
    '''
    update parameterset
    '''   

    logger = logging.getLogger(__name__) 
    logger.info(f"Update parameters: {data}")

    session_id = data["sessionID"]
    form_data = data["formData"]

    try:        
        session = Session.objects.get(id=session_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_update_take_update_parameterset session, not found ID: {session_id}")
        return
    
    form_data_dict = {}

    for field in form_data:            
        form_data_dict[field["name"]] = field["value"]

    form = ParameterSetForm(form_data_dict, instance=session.parameter_set)

    if form.is_valid():
        #print("valid form")                
        form.save() 

        session.parameter_set.update_group_counts()             

        return {"value" : "success"}                      
                                
    logger.info("Invalid session form")
    return {"value" : "fail", "errors" : dict(form.errors.items())}

def take_update_parameterset_type(data):
    '''
    update parameterset type
    '''   

    logger = logging.getLogger(__name__) 
    logger.info(f"Update parameterset type: {data}")

    session_id = data["sessionID"]
    paramterset_type_id = data["parameterset_type_id"]
    form_data = data["formData"]

    try:        
        parameter_set_type = ParameterSetType.objects.get(id=paramterset_type_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_update_parameterset_type paramterset_type, not found ID: {paramterset_type_id}")
        return
    
    form_data_dict = {}

    for field in form_data:            
        form_data_dict[field["name"]] = field["value"]

    form = ParameterSetTypeForm(form_data_dict, instance=parameter_set_type)

    if form.is_valid():
        #print("valid form")             
        form.save()              

        return {"value" : "success"}                      
                                
    logger.info("Invalid session form")
    return {"value" : "fail", "errors" : dict(form.errors.items())}

def take_update_parameterset_player(data):
    '''
    update parameterset player
    '''   
    logger = logging.getLogger(__name__) 
    logger.info(f"Update parameterset player: {data}")

    session_id = data["sessionID"]
    paramterset_player_id = data["paramterset_player_id"]
    form_data = data["formData"]

    try:        
        parameter_set_player = ParameterSetPlayer.objects.get(id=paramterset_player_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_update_parameterset_type paramterset_player, not found ID: {paramterset_player_id}")
        return
    
    form_data_dict = {}

    for field in form_data:            
        form_data_dict[field["name"]] = field["value"]

    logger.info(f'form_data_dict : {form_data_dict}')

    form = ParameterSetPlayerForm(form_data_dict, instance=parameter_set_player)

    if form.is_valid():
        #print("valid form")             
        form.save()              

        return {"value" : "success"}                      
                                
    logger.info("Invalid session form")
    return {"value" : "fail", "errors" : dict(form.errors.items())}

def take_update_parameterset_player_group(data):
    '''
    update parameterset player group
    '''   
    logger = logging.getLogger(__name__) 
    logger.info(f"Update parameterset player group: {data}")

    session_id = data["sessionID"]
    paramterset_player_group_id = data["paramterset_player_group_id"]
    form_data = data["formData"]

    try:        
        parameter_set_player_group = ParameterSetPlayerGroup.objects.get(id=paramterset_player_group_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_update_parameterset_type paramterset_type, not found ID: {paramterset_player_group_id}")
        return
    
    form_data_dict = {}

    for field in form_data:            
        form_data_dict[field["name"]] = field["value"]

    logger.info(f'form_data_dict : {form_data_dict}')

    form = ParameterSetPlayerGroupForm(form_data_dict, instance=parameter_set_player_group)

    if form.is_valid():
        #print("valid form")             
        form.save()              

        return {"value" : "success"}                      
                                
    logger.info("Invalid session form")
    return {"value" : "fail", "errors" : dict(form.errors.items())}

def take_remove_parameterset_player(data):
    '''
    remove the specifed parmeterset player
    '''
    logger = logging.getLogger(__name__) 
    logger.info(f"Remove parameterset player: {data}")

    session_id = data["sessionID"]
    paramterset_player_id = data["paramterset_player_id"]

    try:        
        session = Session.objects.get(id=session_id)
        session.parameter_set.parameter_set_players.get(id=paramterset_player_id).delete()
        session.update_player_count()
    except ObjectDoesNotExist:
        logger.warning(f"take_remove_parameterset_player paramterset_player, not found ID: {paramterset_player_id}")
        return
    
    return {"value" : "success"}

def take_add_paramterset_player(data):
    '''
    add a new parameter player to the parameter set
    '''
    logger = logging.getLogger(__name__) 
    logger.info(f"Add parameterset player: {data}")

    session_id = data["sessionID"]

    try:        
        session = Session.objects.get(id=session_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_update_take_update_parameterset session, not found ID: {session_id}")
        return

    session.parameter_set.add_new_player(main.globals.SubjectType.ONE, 0)
    session.parameter_set.update_group_counts()
    session.update_player_count()

def take_copy_groups_forward(data):
    '''
    copy groups forward from the specified period
    '''   
    logger = logging.getLogger(__name__) 
    logger.info(f"Copy groups forward: {data}")

    session_id = data["sessionID"]
    period_number = data["period_number"]

    try:        
        session = Session.objects.get(id=session_id)
    except ObjectDoesNotExist:
        logger.warning(f"take_copy_groups_forward, session not found ID: {session_id}")
        return

    session.parameter_set.copy_groups_forward(period_number)
    
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

    status = target_session.parameter_set.from_dict(source_session.parameter_set.json()) 
    target_session.update_player_count()

    return status      

    # return {"value" : "fail" if "Failed" in message else "success",
    #         "message" : message}

def take_download_parameters(data):
    '''
    download parameters to a file
    '''   
    logger = logging.getLogger(__name__) 
    logger.info(f"Download parameters: {data}")

    session_id = data["sessionID"]

    session = Session.objects.get(id=session_id)
   
    return {"status" : "success", "parameter_set":session.parameter_set.json()}                      
                                
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

    logger.info(f'form_data_dict : {form_data_dict}')

    form = SessionPlayerMoveForm(form_data_dict)

    if form.is_valid():
        #print("valid form") 

        try:        
            session = Session.objects.get(id=session_id)
            source_type = data["sourceType"]
            source_id = data["sourceID"]
            target_type = data["targetType"]
            target_id = data["targetID"]
        except ObjectDoesNotExist:
            logger.warning(f"take_move_goods session, not found ID: {session_id}")
            return {"status" : "fail", "errors" : {}}       
                      
        return {"status" : "success"}                      
                                
    logger.info("Invalid session form")
    return {"status" : "fail", "errors" : dict(form.errors.items())}