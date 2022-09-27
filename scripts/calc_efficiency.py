print("Calc efficiency for session:")
session_id = input()

from main.models import Session
from main.models import SessionPlayerPeriod

session_player_period_list = SessionPlayerPeriod.objects.filter(session_player__session__id=session_id)

for p in session_player_period_list:
    p.update_efficiency()
