print("Check for lost goods:")
session_id = input()

from main.models import Session
from main.models import SessionPlayerPeriod

session = Session.objects.get(id=session_id)

for sp in session.session_periods.all():
    total_production = 0
    totals_at_end = 0

    for spp in sp.session_player_periods_a.all():
        total_production += spp.good_one_production + spp.good_two_production
        totals_at_end += spp.good_one_field + spp.good_two_field + spp.good_one_consumption + spp.good_two_consumption

    if total_production != totals_at_end:
        print(f"Session player period {sp.period_number} has a discrepancy of {total_production - totals_at_end}")
