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

if os.path.isfile('eventos.csv'):
    with open('eventos.csv', mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # pula a primeira linha (cabeçalho)
        for row in reader:
            eventos_gravados.add(tuple(row))  # adiciona evento ao conjunto

with open('eventos.csv', mode='a', newline='') as file:
    writer = csv.writer(file)

    if not eventos_gravados:  # se conjunto estiver vazio, grava cabeçalho
        writer.writerow(['Evento', 'Data', 'Severidade'])

    for event in events:
        data = datetime.fromtimestamp(
            int(event['clock'])).strftime('%Y-%m-%d %H:%M:%S')
        severidade = severidades[(int(event['severity']))]
        event_name = event['name']
        evento = (event_name, data, severidade)  # cria tupla com informações do evento
        if severidade == severidades[4] and evento not in eventos_gravados:
            writer.writerow([event_name, data, severidade])
            eventos_gravados.add(evento)  # adiciona evento ao conjunto

api.user.logout()

# Open the CSV file and read its contents into a string variable
with open('eventos.csv', mode='r') as file:
    csv_contents = file.read()
