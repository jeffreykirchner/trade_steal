<b>Web version of the following experiments</b><br>
<p align="center">
Crockett, Sean and Smith, Vernon L. and Wilson, Bart J., Exchange and Specialization as a Discovery Process (May 1, 2006). The Economic Journal, Vol. 119, pp. 1162-1188, 2009, Available at SSRN: https://ssrn.com/abstract=930078 or http://dx.doi.org/10.2139/ssrn.930078
</p>
<p align="center">
Kimbrough, E. O., Smith, V. L., & Wilson, B. J. (2010). Exchange, theft, and the social formation of property. Journal of Economic Behavior & Organization, 74(3), 206–229. https://doi.org/10.1016/j.jebo.2010.03.017
</p>
<p align="center">
Levine, S. S., Siegenthaler, S., & Wilson, B. J. (2026). Linguistic intervention unlocks the economic gains of diversity. Proceedings of the National Academy of Sciences, 123(43), e2534825123. https://doi.org/10.1073/pnas.2534825123
</p>


<b>Setup Guide</b><br>
https://www.digitalocean.com/community/tutorials/how-to-set-up-django-with-postgres-nginx-and-gunicorn-on-ubuntu-18-04

local_settings.py:<br>
Copy local_settings_sample.py to local_settings.py<br>
local_settings.py is used for local development and will be excluded from the repo.<br>
Update the DATABASES section of this file with the info from your locally run instance of Postgresql.<br>
Update the CHANNEL_LAYERS section of this file with the info from your locally running Redis instance.<br>

Update Python installers:<br>
	sudo add-apt-repository ppa:deadsnakes/ppa<br>
	sudo apt update <br>
	sudo apt install python3.11<br>
	sudo apt-get install python3.11-distutils<br>

Activate virtual environment and install requirements:<br>
    virtualenv --python=python3.11 _trade_steal_env<br>
    source _trade_steal_env/bin/activate<br>
    pip install -U -r requirements.txt<br>

Set up Environment:<br>
sh setup.sh<br>

Run Environment:<br>
python manage.py runserver<br>
