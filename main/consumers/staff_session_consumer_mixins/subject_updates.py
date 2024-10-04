
from asgiref.sync import sync_to_async

import json

from django.core.serializers.json import DjangoJSONEncoder

from main.models import Session
from main.models import SessionPlayer


import main

class SubjectUpdatesMixin():
    '''
    subject updates mixin for staff session consumer
    '''

    async def update_chat(self, event):
        '''
        send chat to clients, if clients can view it
        '''
        result = event["staff_result"]

        message_data = {}
        message_data["status"] = result

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def update_move_goods(self, event):
        '''
        update good count staff
        '''
        # logger = logging.getLogger(__name__) 
        # logger.info(f'update_goods{self.channel_name}')

        message_data = {}
        message_data["status"] = event["data"]

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def update_groups(self, event)  :
        '''
        update groups on client
        '''

        result = await sync_to_async(take_update_groups)(self.session_id)

        message_data = {}
        message_data["status"] = result

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

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
                        await self.channel_layer.group_send(self.room_group_name,
                                                            {"type": "update_set_controlling_channel",
                                                            "data": {"controlling_channel" : self.controlling_channel},
                                                            "sender_channel_name": self.channel_name,},
            )
                else:
                    #disconnect from staff screen
                    pass
            
            return

        message_data = {}
        message_data["status"] = event["data"]

        #get subject name and student id
        subject_id = message_data["status"]["result"]["id"]

        session_player = await SessionPlayer.objects.aget(id=subject_id)
        message_data["status"]["result"]["name"] = session_player.name
        message_data["status"]["result"]["student_id"] = session_player.student_id
        message_data["status"]["result"]["current_instruction"] = session_player.current_instruction
        message_data["status"]["result"]["survey_complete"] = session_player.survey_complete
        message_data["status"]["result"]["instructions_finished"] = session_player.instructions_finished

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def update_name(self, event):
        '''
        send update name notice to staff screens
        '''

        # logger = logging.getLogger(__name__) 
        # logger.info("Eng game update")

        message_data = {}
        message_data["status"] = event["data"]

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def update_avatar(self, event):
        '''
        send update avatar notice to staff screens
        '''

        # logger = logging.getLogger(__name__) 
        # logger.info("Eng game update")

        message_data = {}
        message_data["status"] = event["data"]

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))

    async def update_next_instruction(self, event):
        '''
        send instruction status to staff
        '''

        # logger = logging.getLogger(__name__) 
        # logger.info("Eng game update")

        message_data = {}
        message_data["status"] = event["data"]

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def update_finish_instructions(self, event):
        '''
        send instruction status to staff
        '''

        # logger = logging.getLogger(__name__) 
        # logger.info("Eng game update")

        message_data = {}
        message_data["status"] = event["data"]

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
    async def update_production_time(self, event):
        '''
        send production settings update
        '''

        # logger = logging.getLogger(__name__) 
        # logger.info("Eng game update")

        message_data = {}
        message_data["status"] = event["data"]

        message = {}
        message["messageType"] = event["type"]
        message["messageData"] = message_data

        await self.send(text_data=json.dumps({'message': message}, cls=DjangoJSONEncoder))
    
def take_update_groups(session_id):
    '''
    take update groups
    '''

    session = Session.objects.get(id=session_id)

    status = "success"
    
    return {"status" : status,
            "group_list" : session.json_for_group_update()}