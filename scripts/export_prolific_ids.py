print("Exporting Prolific IDs...")

from main.models import SessionPlayer

session_players = SessionPlayer.objects.filter(session__parameter_set__prolific_mode=True) \
                                       .filter(session__creator__id=4) \
                                       .values("student_id", "player_key") \
                                       .order_by("student_id")\

with open("database_dumps/prolific_ids.csv", "w") as f:
    f.write("Prolific Subject ID, Study Subject ID\n")
    for sp in session_players:
        f.write(f"{sp['student_id']}, {sp['player_key']}\n")