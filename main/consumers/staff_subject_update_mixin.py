
import json
import logging
from asgiref.sync import sync_to_async

from django.core.serializers.json import DjangoJSONEncoder

import main

class StaffSubjectUpdateMixin():

    connection_type = None            #staff or subject
    connection_uuid = None            #uuid of connected object   
    session_id = None                 #id of session

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
