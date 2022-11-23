# simple monitoring for chain proposal


## prepare

create env
```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

create conf.py

```python
class Conf:

    monitoring_period = 30 # in mins
    start_date_monitoring = "2022-11-10" # YYYY-MM-DD

    tg_token = "..."
    
    trello_sec = "..."
    trello_key = "..."
    trello_board = "..."
```

all done ))

## run 

```bash
python3 bot.py
```

## usage

go to bot and /add_chain for adding 
/start - for start monitoring



see content of db - db.json