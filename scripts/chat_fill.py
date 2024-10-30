print("Fill session with random chat:")
session_id = input()

from main.models import Session
from main.models import SessionPlayerPeriod
from main.models import SessionPlayerChat
from main.models import SessionPlayerNotice

from main.globals import ChatTypes

import main

if session_id == "":
    exit("Please provide a session ID")

session = Session.objects.get(id=session_id)

session_player_chats = []
for i in range(100):
    session_player_chat = SessionPlayerChat()

    session_player_chat.session = session
    session_player_chat.session_period = session.session_periods.all()[0]
    session_player_chat.session_player = session.session_players.all()[0]

    session_player_chat.text = F"This is a test chat message: {i}"
    session_player_chat.chat_type = ChatTypes.ALL

    session_player_chat.save()

    session_player_chat.session_player_recipients.add(*session.session_players.all())
    session_player_chat.save()

    
session.world_state["chat_all"]["1"] = [c.json_for_staff() for c in SessionPlayerChat.objects \
                                        .filter(session_player__in=session.session_players.all())\
                                        .filter(session_player__parameter_set_player__town=1)
                                        .prefetch_related('session_player_recipients')
                                        .select_related('session_player__parameter_set_player')
                                        .order_by('-timestamp')[:100:-1]
                ]

session.save()
