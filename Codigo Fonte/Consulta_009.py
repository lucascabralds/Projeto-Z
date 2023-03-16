import apizabbix
from pprint import pprint
from datetime import datetime
import csv
import os.path



class ZabbixEventos:
    def __init__(self):
        self.api = apizabbix.connect() #Api conewctando com o Zabbix
        self.hostgroups = self.api.hostgroup.get(output=['name'])
        self.hosts = self.api.host.get(output=['name'])
        self.severidades = [#Classificando Serveridades
            'Não classificada',
            'Informação',
            'Atenção',
            'Média',
            'Alta',
            'Desastre'
        ]
        self.título_csv = ['Time', 'Recovery Time', 'Status', 'Problem', 'Duration', 'Ack', 'Action', 'Tags']
        self.eventos_gravados = set()  # conjunto para armazenar eventos já gravados no arquivo

    def pegar_eventos(self, ultima_execucao=None):
        '''
            Link: https://www.zabbix.com/documentation/current/en/manual/api/reference/event/get
            Com base nas informações obtidas a partir do link fornecido, podemos entender mais sobre o assunto em questão.
            Com base na documentação consigos extrair as informações necessaria.
            '''
        filtro = {}  # filtro vazio para obter todos os eventos
        if ultima_execucao:  # se a última execução foi especificada, adicione filtro de data
            filtro['time_from'] = ultima_execucao.timestamp()

        eventos = self.api.event.get(
            filter=filtro,
            output=[
                'clock',#Coluna de data/hora que indica quando o evento ocorreu.
                'name',#nome do evento
                'value',#valor associado ao evento
                'severity',#Qual e a gravidade do evento
                'r_eventid',#ID do evento relacionado
                'acknowledged', #indicação se o evento foi reconhecido ou não
                'r_clock', #um carimbo de data/hora que indica quando o evento relacionado ocorreu
                'r_eventid',
                'duration',#duração do evento
                'tags',#palavras-chave ou etiquetas associadas ao evento para ajudar na organização e pesquisa dos dados
                'severity'
            ],
            sortfield='clock',#Ordenando de forma decrescente as datas
            sortorder='DESC',
        )
        return eventos
    
    def executar(self):
        eventos = self.pegar_eventos()
        self.escreva_csv(eventos)

    
class Gravar_CSV:

    #|Severity|Time|Recovery Time|Status|Problem|Duration|Ack|Action|Tags

    def escreva_csv(self, eventos):
          # verifique se o arquivo CSV já existe e adicione o cabeçalho se não existir
        if not os.path.isfile('eventos.csv'):
            with open('eventos.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(self.título_csv)
        if os.path.isfile('eventos.csv'):
            with open('eventos.csv', mode='r') as file:
                reader = csv.reader(file)
                next(reader)  # pula a primeira linha (cabeçalho)
                for row in reader:
                    eventos_gravados.add(tuple(row))  # adiciona evento ao conjunto
                    
        # para cada evento, extraia as informações relevantes e grave no arquivo CSV
        with open('eventos.csv', 'a', newline='') as f:
            writer = csv.writer(f)
            for event in eventos:
                timestamp = datetime.fromtimestamp(int(event['clock']))
                recovery_time = datetime.fromtimestamp(int(event['r_clock'])) if 'r_clock' in event and event['r_clock'] else ''
                severidade = self.severidades[(int(event['severity']))]
                status = 'PROBLEM' if event['value'] == '1' else 'OK'
                problem = event['name']
                duration = event['duration'] if 'duration' in event else ''
                ack = 'YES' if event['acknowledged'] == '1' else 'NO'
                action = 'RESOLVE' if 'r_eventid' in event and event['r_eventid'] else 'TRIGGER'
                tags = event['tags'] if 'tags' in event else ''
                evento = (timestamp, recovery_time, status, problem, duration, ack, action, tags)
                if severidade == self.severidades[4] and evento not in self.eventos_gravados:
                    writer.writerow([severidade, timestamp, recovery_time, status, problem, duration, ack, action, tags])
                    self.eventos_gravados.add(evento)