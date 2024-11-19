print("Update Session Player Move for stealing")

from main.models import SessionPlayerMove
from django.db.models import F

SessionPlayerMove.objects.filter(session_player_source__session__parameter_set__allow_stealing=False)\
                         .update(session_player=F('session_player_source'))
