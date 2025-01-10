import json
import time
from pydantic import BaseModel, Field, ValidationError
from typing import List
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import ChatPromptTemplate
from google_apis import create_service
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    HarmBlockThreshold,
    HarmCategory,
)
client_secret = 'client_secret.json'

class Evento(BaseModel):
    calendar_id: str = Field(default="primary", description="Identificador do calendário do Google Agenda onde o evento será criado. Por padrão, utiliza o calendário principal do usuário ('primary'). Para usar um calendário diferente, forneça o ID do calendário específico.")
    summary: str = Field(description="Título ou resumo conciso do evento, que será exibido no Google Agenda.")
    location: str = Field(description="Localização do evento. Pode ser um endereço físico ou um nome de local.")
    description: str = Field(description="Descrição detalhada do evento, incluindo informações adicionais, agenda, objetivos.")
    start: str = Field(description="Data e hora de início do evento no formato ISO 8601 (Exemplo: '2023-10-27T10:00:00').")
    end: str = Field(description="Data e hora de término do evento no formato ISO 8601 (Exemplo: '2023-10-27T11:00:00').")
    timezone: str = Field(default="America/Fortaleza", description="Fuso horário do evento, utilizando a nomenclatura da IANA Time Zone Database (e.g., 'America/Sao_Paulo', 'Europe/London'). O padrão é 'America/Fortaleza'.")

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
            calendarId=calendar_id,
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

def extract_event_parameters(query):
    """
    Extrai parâmetros de um evento a partir de uma descrição em linguagem natural.

    Esta função utiliza um modelo de linguagem grande para interpretar a descrição do evento
    fornecida e extrair informações como resumo, local, descrição, horário de início e fim,
    e fuso horário. A resposta é formatada como um JSON de acordo com o esquema definido pela
    classe `Evento`.

    Args:
        query (str): A descrição do evento em linguagem natural.
                      Exemplo: "Marcar reunião com o time de marketing amanhã às 10h na sala de conferência."

    Returns:
        str: Uma string JSON contendo os parâmetros extraídos do evento, ou None se a extração falhar.
             O JSON terá a seguinte estrutura:
             {
                 "calendar_id": "ID do calendário Google (padrão: 'primary')",
                 "summary": "Resumo do evento",
                 "location": "Local do evento",
                 "description": "Descrição do evento",
                 "start": "Hora de início do evento",
                 "end": "Hora de término do evento",
                 "timezone": "Fuso horário do evento (padrão: 'America/Fortaleza')"
             }
    """
    llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    convert_system_message_to_human=True,
    handle_parsing_errors=True,
    temperature=0.6,
    max_tokens= 1000,
    safety_settings = {
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
    },
)
    parser = PydanticOutputParser(pydantic_object=Evento)

    prompt = ChatPromptTemplate.from_messages([
    ("system", "Você é um assistente especialista em extrair informações de eventos de textos. Extraia os parâmetros necessários para criar um evento, incluindo data e hora de início e fim. Retorne a resposta formatada em JSON de acordo com o esquema fornecido.\n\n{format_instructions}\n"),
    ("human", "{user_query}")
    ])
    chain = prompt | llm | parser

    resposta = chain.invoke({
    "language": "Portuguese",
    "user_query": query,
    "format_instructions": parser.get_format_instructions(),
    })
    resposta_dict = {
        'summary': resposta.summary,
        'location': resposta.location,
        'description': resposta.description,
        'start': {
                "dateTime": resposta.start,
                "timeZone": resposta.timezone
            },
        'end': {
                "dateTime": resposta.end,
                "timeZone": resposta.timezone
            },
        'attendees': []
    }

    
    resposta_json = json.dumps(resposta_dict, ensure_ascii=False)
    return resposta.calendar_id, resposta_json
def insert_calendar_event(event):
    """
    Insere um evento em um calendário Google.

    Parâmetros:
    - event (str): Uma descrição em linguagem natural do evento a ser criado.
      A função `extract_event_parameters` será utilizada para extrair os detalhes
      do evento a partir desta descrição e convertê-los em um objeto `Evento`.
      Exemplos:
        - "Agendar almoço com a Maria na sexta-feira ao meio-dia no restaurante X."
        - "Criar um lembrete para pagar as contas no dia 10 às 9h da manhã."
        - "Bloquear minha agenda para foco no projeto Y na próxima segunda das 14h às 17h."

    Retorna:
    - dict: Detalhes do evento criado no Google Agenda ou mensagem de erro.
      Em caso de sucesso, o dicionário conterá informações sobre o evento criado,
      incluindo o ID do evento. Em caso de erro, retornará uma mensagem descrevendo
      o problema encontrado durante o processamento ou inserção do evento.
    """
    extracted_data = extract_event_parameters(event)
    if not extracted_data:
        return "Erro: Não foi possível extrair os detalhes do evento da descrição fornecida."

    calendar_id, event_details = extracted_data
    request_body = json.loads(event_details)
    time.sleep(5)
    event = calendar_service.events().insert(
        calendarId = calendar_id,
        body = request_body
    ).execute()
    return event