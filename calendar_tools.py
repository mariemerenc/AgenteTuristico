import json
from google_apis import create_service

client_secret = 'client_secret.json'

def construct_google_calendar_client(client_secret):
    """
    Constrói um cliente para a API Google Calendar.

    Parâmetros:
    - client_secret (str): O caminho para o arquivo client secret JSON.

    Retorna:
    - service: A instância de serviço com o API do Google Calendar.
    """

    API_NAME = 'calendar'
    API_VERSION = 'v3'
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    service = create_service(client_secret, API_NAME, API_VERSION, SCOPES)
    return service

calendar_service = construct_google_calendar_client(client_secret)

def create_calendar(calendar_name):
    """
    Criar uma nova lista de calendários.

    Parâmetros:
    - calendar_name (str): O nome da nova lista de calendário.

    Retorno:
    - dict: Um dicionário contendo o ID da nova lista de calendário.
    """
    calendar_name = calendar_name.replace("'", "").replace('"', "")
    calendar_list = {
        'summary': calendar_name
    }
    created_calendar_list = calendar_service.calendars().insert(body=calendar_list).execute()
    return created_calendar_list

def list_calendar_list(max_capacity=200):
    """
    Lista todas as listas de calendários disponíveis, com limite de capacidade.

    Parâmetros:
    - max_capacity (int, opcional): O número máximo de calendários a serem retornados. 
      Padrão: 200.

    Retorna:
    - list: Uma lista de dicionários, onde cada dicionário contém os detalhes 
      de um calendário (ID, nome e descrição).
    """
    if isinstance(max_capacity, str):
        max_capacity = int(max_capacity)

    all_calendars = []
    all_calendars_cleaned = []
    next_page_token = None
    capacity_tracker = 0

    while True:
        calendar_list = calendar_service.calendarList().list(
            maxResults = min(200, max_capacity - capacity_tracker),
            pageToken = next_page_token
        ).execute()
        calendars = calendar_list.get('items', [])
        all_calendars.extend(calendars)
        capacity_tracker += len(calendars)
        if capacity_tracker >= max_capacity:
            break
        next_page_token = calendar_list.get('nextPageToken')
        if not next_page_token:
            break
    
    for calendar in all_calendars:
        all_calendars_cleaned.append(
            {
                'id': calendar['id'],
                'name': calendar['summary'],
                'description': calendar.get('description', '')
            })
    return all_calendars_cleaned

def list_calendar_events(calendar_id, max_capacity=20):
    """
    Lista os eventos de um calendário específico.

    Parâmetros:
    - calendar_id (str): O ID do calendário para listar os eventos.
    - max_capacity (int, opcional): O número máximo de eventos a serem retornados.
      Padrão: 20.

    Retorna:
    - list: Uma lista de dicionários contendo os detalhes dos eventos.
    """
    if isinstance(max_capacity, str):
        max_capacity = int(max_capacity)

    all_events = []
    next_page_token = None
    capacity_tracker = 0
    while True:
        events_list = calendar_service.events().list(
            calendarId=calendar_id,  # Corrigido para 'calendarId'
            maxResults=min(250, max_capacity - capacity_tracker),
            pageToken=next_page_token
        ).execute()
        events = events_list.get('items', [])
        all_events.extend(events)
        capacity_tracker += len(events)
        if capacity_tracker >= max_capacity:
            break
        if not next_page_token:
            break
    return all_events


def insert_calendar_event(event_details):
    """
    Insere ou manipula eventos em um calendário Google.

    Parâmetros:
    - event_details (str ou dict): Uma string JSON ou um dicionário Python contendo os detalhes do evento, incluindo 'calendar_id'.

    Formato esperado:
    {
        "calendar_id": "ID do calendário",
        "summary": "Resumo do evento",
        "location": "Localização",
        "description": "Descrição do evento",
        "start": {"date": "YYYY-MM-DD"} ou {"dateTime": "YYYY-MM-DDTHH:MM:SS", "timeZone": "America/Fortaleza"},
        "end": {"date": "YYYY-MM-DD"} ou {"dateTime": "YYYY-MM-DDTHH:MM:SS", "timeZone": "America/Fortaleza"},
        "attendees": [{"email": "exemplo@dominio.com"}]
    }

    Retorna:
    - dict: Detalhes do evento criado ou mensagem de erro.
    """
    try:
        if isinstance(event_details, str):
            event_details = json.loads(event_details)

        calendar_id = event_details.pop('calendar_id', None)
        if not calendar_id:
            return "Erro: 'calendar_id' não encontrado nos detalhes do evento."

        for key in ['start', 'end']:
            if key in event_details:
                if 'dateTime' not in event_details[key]:
                    if 'date' in event_details[key]:
                        default_time = "T00:00:00" if key == 'start' else "T23:59:59"
                        event_details[key] = {
                            'dateTime': f"{event_details[key]['date']}{default_time}",
                            'timeZone': 'America/Fortaleza'
                        }
                    else:
                        return f"Erro: '{key}' deve conter 'dateTime' ou 'date'."
            else:
                return f"Erro: '{key}' faltando nos detalhes do evento."

        event = {k: v for k, v in event_details.items() if v is not None}

        created_event = calendar_service.events().insert(calendarId=calendar_id, body=event).execute()
        return created_event

    except json.JSONDecodeError as e:
        return f"Erro ao decodificar JSON: {e}"
    except TypeError as e:
        return f"Erro de tipo ao passar argumentos: {e}. Verifique a estrutura do JSON ou dicionário."
    except Exception as e:
        return f"Ocorreu um erro: {e}"


