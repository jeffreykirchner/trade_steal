print("Update abbreviations")

from main.models import ParameterSetGood

ParameterSetGood.objects.filter(label="Orange").update(abbreviation="O")
ParameterSetGood.objects.filter(label="Blue").update(abbreviation="B")
ParameterSetGood.objects.filter(label="Pink").update(abbreviation="P")
