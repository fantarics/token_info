<a href="https://wakatime.com/badge/user/8ae1715c-be50-4dae-a4a0-829b3152ad8a/project/d56165a5-6fc5-4650-bd13-6ac216b80703"><img src="https://wakatime.com/badge/user/8ae1715c-be50-4dae-a4a0-829b3152ad8a/project/d56165a5-6fc5-4650-bd13-6ac216b80703.svg" alt="wakatime"></a>

Api docs link: http://localhost:8080/docs

``
pip install -r requirements.txt
``

To launch application

``
python app.py
``

To launch application tests

``
python test.py
``

P.S. Transaction fetching is the <b>most</b> expensive request, since usual rpc methods do not provide such functionality. Hence 3rd party API (ankr) had to be used in order to accomplish the task 