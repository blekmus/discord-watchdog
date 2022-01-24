import requests
from operator import itemgetter
from modules.user_agents import get_agent

def get_entries(current_entry):
    verified = requests.get('https://watchdogapi.paladinanalytics.com/public/feed?type=verified', headers=get_agent())
    fake = requests.get('https://watchdogapi.paladinanalytics.com/public/feed?type=fake', headers=get_agent())

    # return if data isn't returned
    if (verified.status_code != 200 or fake.status_code != 200):
        return

    entries = []

    # convert verified entries to object and append to entries
    for entry in verified.json()['body']:
        entries.append({
            'id': entry['id'],
            'timestamp': entry['timestamp'],
            'title': entry['en_title'],
            'description': entry['en_description'],
            'type': 'verified',
            'url': entry['source_link'],
            'source_name': entry['source_name'],
        })

    # convert fake entries to object and append to entries
    for entry in fake.json()['body']:
        entries.append({
            'id': entry['id'],
            'timestamp': entry['timestamp'],
            'title': entry['en_title'],
            'description': entry['en_description'],
            'type': 'fake',
            'url': entry['source_link'],
            'source_name': entry['source_name'],
        })

    # sort entries in descending order
    entries = sorted(entries, key=itemgetter('id'), reverse=True)

    # remove older entries
    entries = [entry for entry in entries if int(entry['id']) > current_entry]

    return entries
