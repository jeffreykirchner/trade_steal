print("Store chat into world state:")
session_id = input()

from main.models import Session
from main.models import SessionPlayerPeriod
from main.models import SessionPlayerChat
from main.models import SessionPlayerNotice

import main

if session_id == "":
    sessions = Session.objects.all()
else:
    sessions = Session.objects.get(id=session_id)

for session in sessions: 
    print("Processing session: " + str(session.id))
    
    if session.world_state is None or session.world_state == {}:
        session.setup_world_state()

    if session.world_state.get("chat_all", None) is None:
        session.world_state["chat_all"] = {}

    if session.world_state.get("notices", None) is None:
        session.world_state["notices"] = {}

    for i in range(session.parameter_set.town_count):
                
                session.world_state["chat_all"][str(i+1)] = [c.json_for_staff() for c in SessionPlayerChat.objects \
                                                        .filter(session_player__in=session.session_players.all())\
                                                        .filter(session_player__parameter_set_player__town=i+1)
                                                        .prefetch_related('session_player_recipients')
                                                        .select_related('session_player__parameter_set_player')
                                                        .order_by('-timestamp')[:100:-1]
                                ]

                session.world_state["notices"][str(i+1)] = [n.json() for n in SessionPlayerNotice.objects \
                                                        .filter(session_player__in=session.session_players.all()) \
                                                        .filter(session_player__parameter_set_player__town=i+1) \
                                                        .filter(show_on_staff=True) \
                                                        .order_by('-timestamp')[:100:-1]    
                                    ]

    session.save()
