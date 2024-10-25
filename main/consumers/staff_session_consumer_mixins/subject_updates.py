
from asgiref.sync import sync_to_async

import json
import logging

from django.core.serializers.json import DjangoJSONEncoder

from main.models import Session
from main.models import SessionPlayer
from main.models import SessionPlayerChat

from main.globals import ChatTypes


import main

class SubjectUpdatesMixin():
    '''
    subject updates mixin for staff session consumer
    '''

    async def chat(self, event):
        '''
        take chat from client
        '''
        if self.controlling_channel != self.channel_name:
            return
        
        logger = logging.getLogger(__name__)
        logger.info(f'chat {event}')

        status = "success"
        message = ""
        player_id = None
        result = {}


        try:
            player_id = self.session_players_local[event["player_key"]]["id"]
            event_data = event["message_text"]
        except:
            logger.warning(f"chat: invalid data, {event['message_text']}")
            status = "fail"
            message = "Invalid data."
        
        target_list = [player_id]

        if status == "success":
            try:
                recipients = event_data["recipients"] 
                chat_text = event_data["text"]
            except KeyError:
                message =  "Invalid chat."

        result = {}
        #result["recipients"] = []

        session = await Session.objects.aget(id=self.session_id)
        session_player = await session.session_players.aget(id=player_id)

        if status == "success":
            if not session.started:
                status = "fail"
                message = "Session not started."
        
        if status == "success":
            if session.finished:
                status = "fail"
                message = "Session finished."

        if status == "success":
            if session.current_experiment_phase != main.globals.ExperimentPhase.RUN:
                status = "fail"
                message = "Session not running."
        
        if status == "success":
            parameter_set = self.parameter_set_local
            current_session_period = await session.aget_current_session_period()

            session_player_chat = SessionPlayerChat()

            session_player_chat.session_player = session_player
            session_player_chat.session_period = current_session_period

            if recipients == "all":
                if not parameter_set["group_chat"]:
                    logger.warning(f"take chat: group chat not enabled :{self.session_id} {player_id} {event_data}")
                    status = "fail"
                    message = "Group chat not allowed."

                session_player_chat.chat_type = ChatTypes.ALL
            else:
                if not session.parameter_set.private_chat:
                    logger.warning(f"take chat: private chat not enabled :{self.session_id} {player_id} {event_data}")
                    status = "fail"
                    message = "Private chat not allowed."

                session_player_chat.chat_type = ChatTypes.INDIVIDUAL

            if status == "success":
                result["chat_type"] = session_player_chat.chat_type
                result["recipients"] = []

                session_player_chat.text = chat_text
                session_player_chat.time_remaining = session.time_remaining
                session_player_chat.current_period_phase = session.current_period_phase

                await session_player_chat.asave()

                session.world_state["chat_all"][str(session_player.parameter_set_player.town)].append(session_player_chat.json_for_staff())

                if len(session_player.session.world_state["chat_all"][str(session_player.parameter_set_player.town)]) > 100:
                    session_player.session.world_state["chat_all"][str(session_player.parameter_set_player.town)].pop(0)

                await session.asave()

                parameter_set_player_group = await self.get_player_group(player_id, session.current_period)
                groups = await self.get_group_memebers(parameter_set_player_group, session.current_period)
                
                # session_player_group_list = session_player.get_current_group_list()

                if recipients == "all":
                    session_player_chat.session_player_recipients.add(groups[str(parameter_set_player_group)])

                    result["recipients"] = groups[str(parameter_set_player_group)]
                else:
                    sesson_player_target = await SessionPlayer.objects.aget(id=recipients)
                    if recipients in groups[str(parameter_set_player_group)]:
                        session_player_chat.session_player_recipients.add(recipients)
                    else:
                        session_player_chat.delete()
                        logger.warning(f"take chat: chat at none group member : {self.session_id} {player_id} {event_data}")
                        status = "fail"
                        message = "Player not in group."
                        

                    if status == "success":
                        result["sesson_player_target"] = sesson_player_target.id

                        result["recipients"].append(session_player.id)
                        result["recipients"].append(sesson_player_target.id)
                
                if status == "success":
                    result["chat_for_subject"] = session_player_chat.json_for_subject()
                    result["chat_for_staff"] = session_player_chat.json_for_staff()

                    await session_player_chat.asave()

        await self.send_message(message_to_self=None, message_to_group=result,
                                message_type=event['type'], send_to_client=False,
                                send_to_group=True, target_list=target_list)

    async def get_group_memebers(self, group_number, period_number):
        '''
        return a list of group members for this period.
        '''
        groups = {}

        for p in self.parameter_set_local["parameter_set_players"]:
            group = await self.get_player_group(p, period_number)

            if not groups.get(str(group), None):
                groups[str(group)] = []

            groups[str(group)].append(p)
        
        return groups
    
    async def get_player_group(self, player_id, period_number):
        '''
        return the group number for this player
        '''
        group_id = self.parameter_set_local["parameter_set_players"][str(player_id)]["period_groups_order"][period_number-1]
        group = self.parameter_set_local["parameter_set_players"][str(player_id)]["period_groups_order"][str(group_id)]["group_number"]

        return group
        

    async def update_chat(self, event):
        '''
        send chat to clients, if clients can view it
        '''
        result =  json.loads(event["group_data"])

        await self.send_message(message_to_self=result["staff_result"], message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

    async def update_move_goods(self, event):
        '''
        update good count staff
        '''
        # logger = logging.getLogger(__name__) 
        # logger.info(f'update_goods{self.channel_name}')

        result =  json.loads(event["group_data"])

        await self.send_message(message_to_self=result["data"], message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

    async def update_groups(self, event)  :
        '''
        update groups on client
        '''

        result = await sync_to_async(take_update_groups)(self.session_id)

        await self.send_message(message_to_self=result, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)


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

                        result = {"controlling_channel" : self.controlling_channel}
                        await self.send_message(message_to_self=None, message_to_group=result,
                                                message_type="set_controlling_channel", send_to_client=False, send_to_group=True)
            
                else:
                    #disconnect from staff screen
                    pass
            
            return

        result = event["data"]

        #get subject name and student id
        subject_id = result["result"]["id"]

        session_player = await SessionPlayer.objects.aget(id=subject_id)
        result["result"]["name"] = session_player.name
        result["result"]["student_id"] = session_player.student_id
        result["result"]["current_instruction"] = session_player.current_instruction
        result["result"]["survey_complete"] = session_player.survey_complete
        result["result"]["instructions_finished"] = session_player.instructions_finished

        await self.send_message(message_to_self=result, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

    async def update_name(self, event):
        '''
        send update name notice to staff screens
        '''

        # logger = logging.getLogger(__name__) 
        # logger.info("Eng game update")

        result =  json.loads(event["group_data"])

        await self.send_message(message_to_self=result, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

    
    async def update_avatar(self, event):
        '''
        send update avatar notice to staff screens
        '''

        # logger = logging.getLogger(__name__) 
        # logger.info("Eng game update")

        result =  json.loads(event["group_data"])

        await self.send_message(message_to_self=result, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

    async def update_next_instruction(self, event):
        '''
        send instruction status to staff
        '''

        # logger = logging.getLogger(__name__) 
        # logger.info("Eng game update")

        result =  json.loads(event["group_data"])

        await self.send_message(message_to_self=result, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

    
    async def update_finish_instructions(self, event):
        '''
        send instruction status to staff
        '''

        # logger = logging.getLogger(__name__) 
        # logger.info("Eng game update")

        result =  json.loads(event["group_data"])

        await self.send_message(message_to_self=result, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

    
    async def update_production_time(self, event):
        '''
        send production settings update
        '''

        # logger = logging.getLogger(__name__) 
        # logger.info("Eng game update")

        result =  json.loads(event["group_data"])

        await self.send_message(message_to_self=result, message_to_group=None,
                                message_type=event['type'], send_to_client=True, send_to_group=False)

    
def take_update_groups(session_id):
    '''
    take update groups
    '''

    session = Session.objects.get(id=session_id)

    status = "success"
    
    return {"status" : status,
            "group_list" : session.json_for_group_update()}