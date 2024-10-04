from asgiref.sync import sync_to_async

import json

from django.core.serializers.json import DjangoJSONEncoder

from main.models import Session

class DataMixin():
    '''
    data mixin for staff session consumer
    '''

    async def download_summary_data(self, event):
        '''
        download summary data
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_download_summary_data)(self.session_id)

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def download_action_data(self, event):
        '''
        download summary data
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_download_action_data)(self.session_id)

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def download_recruiter_data(self, event):
        '''
        download summary data
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_download_recruiter_data)(self.session_id)

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def download_payment_data(self, event):
        '''
        download payment data
        '''

        message_data = {}
        message_data["status"] = await sync_to_async(take_download_payment_data)(self.session_id)

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    

def take_download_summary_data(session_id):
    '''
    download summary data for session
    '''

    session = Session.objects.get(id=session_id)

    return {"value" : "success", "result" : session.get_download_summary_csv()}

def take_download_action_data(session_id):
    '''
    download action data for session
    '''

    session = Session.objects.get(id=session_id)

    return {"value" : "success", "result" : session.get_download_action_csv()}

def take_download_recruiter_data(session_id):
    '''
    download recruiter data for session
    '''

    session = Session.objects.get(id=session_id)

    return {"value" : "success", "result" : session.get_download_recruiter_csv()}

def take_download_payment_data(session_id):
    '''
    download payment data for session
    '''

    session = Session.objects.get(id=session_id)

    return {"value" : "success", "result" : session.get_download_payment_csv()}
