
import json
import logging

from django.core.serializers.json import DjangoJSONEncoder

class StaffSubjectUpdateMixin():
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

        if self.channel_name != event['sender_channel_name']:
            await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

     async def update_start_experiment(self, event):
        '''
        start experiment on all
        '''
        logger = logging.getLogger(__name__) 
        logger.info(f'update_goods{self.channel_name}')

        message_data = {}
        message_data["status"] = event["data"]

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        #if self.channel_name != event['sender_channel_name']:
        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))