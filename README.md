# Specialization_and_Trade
Web version of the Exchange and Specialization experiment.  https://papers.ssrn.com/sol3/papers.cfm?abstract_id=930078

Setup Guide:
https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-18-04

local_settings.py:<br>
Copy local_settings_sample.py to local_settings.py<br>
local_settings.py is used for local development and will be excluded from the repo.<br>
Update the DATABASES section of this file with the info from your locally run instance of Postgresql.<br>
Update the CHANNEL_LAYERS layers section of this file with the info from your locally run instance of Redis.<br>

Update Python installers:<br>
	sudo add-apt-repository ppa:deadsnakes/ppa<br>
	sudo apt update <br>
	sudo apt install python3.11<br>
	sudo apt-get install python3.11-distutils<br>

Activate virtual environment and install requirments:<br>
    virtualenv --python=python3.11 _trade_steal_env<br>
    source _trade_steal_env/bin/activate<br>
    pip install -U -r requirements.txt<br>

Setup Environment:<br>
sh setup.sh<br>

Run Environment:<br>
python manage.py runserver<br>
