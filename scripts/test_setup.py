print("Fill add goods with 10")
print("Enter Session ID:")
session_id = input()

from main.models import Session
session = Session.objects.get(id=session_id)
session.session_players.all().update(good_one_house=10)
session.session_players.all().update(good_two_house=10)
session.session_players.all().update(good_three_house=10)
session.session_players.all().update(good_one_field=10)
session.session_players.all().update(good_two_field=10)