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

    monitoring_period = 1 # in mins

    tg_token = "..."
    
    trello_sec = "..."
    trello_key = "..."
    trello_board = "..."
```

all done ))

## run 

python3 bot.py

## usage

go to bot and /add_chain for adding 
/start - for start monitoring



see content of db - db.json