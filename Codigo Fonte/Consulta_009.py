import apizabbix
from pprint import pprint
from datetime import datetime
import csv
import os.path

api = apizabbix.connect()

hostgroups = api.hostgroup.get(output=['name'])
host = api.host.get(output=['name'])

events = api.event.get(
    output=[
        'clock',
        'name',
        'value',
        'severity',
        'r_eventid',
        'acknowledged',
        'r_clock',
        'r_eventid',
        'duration',
        'tags',
    ],
    sortfield='clock',
    sortorder='DESC',
)

severidades = [
    'Não classificada',
    'Informação',
    'Atenção',
    'Média',
    'Alta',
    'Desastre'
]

eventos_gravados = set()  # conjunto para armazenar eventos já gravados no arquivo

csv_header = ['Time', 'Recovery Time', 'Status', 'Problem', 'Duration', 'Ack', 'Action', 'Tags']

# verifique se o arquivo CSV já existe e adicione o cabeçalho se não existir
if not os.path.isfile('eventos.csv'):
    with open('eventos.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(csv_header)

# para cada evento, extraia as informações relevantes e grave no arquivo CSV
for event in events:
    timestamp = datetime.fromtimestamp(int(event['clock']))
    recovery_time = datetime.fromtimestamp(int(event['r_clock'])) if 'r_clock' in event and event['r_clock'] else ''
    status = 'PROBLEM' if event['value'] == '1' else 'OK'
    problem = event['name']
    duration = event['duration'] if 'duration' in event else ''
    ack = 'YES' if event['acknowledged'] == '1' else 'NO'
    action = 'RESOLVE' if 'r_eventid' in event and event['r_eventid'] else 'TRIGGER'
    tags = event['tags'] if 'tags' in event else ''

    # verifique se o evento já foi gravado no arquivo CSV
    if event['eventid'] not in eventos_gravados:
        eventos_gravados.add(event['eventid'])

        # grave o evento no arquivo CSV
        with open('eventos.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, recovery_time, status, problem, duration, ack, action, tags])