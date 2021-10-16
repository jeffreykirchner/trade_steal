'''
core socket communication mixin
'''
import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

class SocketConsumerMixin(AsyncWebsocketConsumer):
    '''
    core socket communication functions
    '''
    room_name = None
    room_group_name = None           #channel that consumer listens on
    channel_session_user = True
    http_user = True

    async def connect(self):
        '''
        inital connection from websocket
        '''
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        
        kwargs = self.scope['url_route']['kwargs']
        room_name =  kwargs.get('room_name')
        page_key =  kwargs.get('page_key',"")

        self.room_group_name = room_name + page_key

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        logger = logging.getLogger(__name__) 
        logger.info(f"SocketConsumerMixin Connect {self.channel_name}")

        await self.accept()

    async def disconnect(self, close_code):
        '''
        disconnect websockeet
        '''
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        '''
        incoming data from websocket
        '''
        text_data_json = json.loads(text_data)

        message_type = text_data_json['messageType']   #name of child method to be called
        message_text = text_data_json['messageText']   #data passed to above method

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': message_type,
                'message_text': message_text
            }
        )