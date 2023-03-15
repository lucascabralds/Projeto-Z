import apizabbix
from pprint import pprint
from datetime import datetime
import csv
import os.path


class ZabbixAPI: #Classe responsavel por fazer os recolhimento das informações do Zabbix
    def __init__(self): #Metodo responsavel por
        self.api = apizabbix.connect()
        self.severidades = [
            'Não classificada',
            'Informação',
            'Atenção',
            'Média',
            'Alta',
            'Desastre'
        ]

    def recolhendo_eventos(self): 
        events = self.api.event.get(
            output=[
                'clock',
                'name',
                'value',
                'severity',
            ],
            sortfield='clock',
            sortorder='DESC',
        )
        return events

    def Desconectar(self):
        self.api.user.logout()


class GerenciandoCSV:
    def __init__(self, filename):
        self.filename = filename
        self.eventos_gravados = set()  # conjunto para armazenar eventos já gravados no arquivo
        self.csv_header = ['Evento', 'Data', 'Severidade']

    def carregar_csv(self):
        if os.path.isfile(self.filename):
            with open(self.filename, mode='r') as file:
                reader = csv.reader(file)
                next(reader)  # pula a primeira linha (cabeçalho)
                for row in reader:
                    self.eventos_gravados.add(tuple(row))  # adiciona evento ao conjunto

    def salvando_eventos(self, event):
        data = datetime.fromtimestamp(int(event['clock'])).strftime('%Y-%m-%d %H:%M:%S')
        severidade = self.severidades[int(event['severity'])]
        event_name = event['name']
        evento = (event_name, data, severidade)  # cria tupla com informações do evento
        if severidade == self.severidades[4] and evento not in self.eventos_gravados:
            with open(self.filename, mode='a', newline='') as file:
                writer = csv.writer(file)
                if not self.eventos_gravados:  # se conjunto estiver vazio, grava cabeçalho
                    writer.writerow(self.csv_header)
                writer.writerow([event_name, data, severidade])
                self.eventos_gravados.add(evento)  # adiciona evento ao conjunto

    def lendo_csv(self):
        with open(self.filename, mode='r') as file:
            conteudo_csv = file.read()
        return conteudo_csv


if __name__ == '__main__':
    api = ZabbixCsv()
    events = api.recolhendo_eventos()

    csv_manager = GerenciandoCSV('eventos.csv')
    csv_manager.carregar_csv()

    for event in events:
        csv_manager.salvando_eventos(event)

    api.logout()

    conteudo_csv = csv_manager.lendo_csv()
    print(conteudo_csv)
