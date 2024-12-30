import os
from datetime import datetime
from langchain import hub
from langchain.agents import Tool, AgentExecutor
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.memory import ChatMessageHistory, ConversationBufferWindowMemory
from langchain.tools.render import render_text_description
from langchain.utilities import DuckDuckGoSearchAPIWrapper
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    HarmBlockThreshold,
    HarmCategory,
)

from planing_tools import weatherapi_forecast_periods, query_rag
from calendar_tools import list_calendar_list, list_calendar_events, insert_calendar_event, create_calendar



hoje = datetime.today()

data_formatada = hoje.strftime("%Y/%m/%d")
# Pega o dia da semana em inglês
dia_da_semana_ingles = hoje.strftime("%A")

# Dicionário para mapear os dias da semana de inglês para português
dias_da_semana_pt = {
    "Monday": "segunda-feira",
    "Tuesday": "terça-feira",
    "Wednesday": "quarta-feira",
    "Thursday": "quinta-feira",
    "Friday": "sexta-feira",
    "Saturday": "sábado",
    "Sunday": "domingo"
}

# Traduz o dia da semana para português
dia_da_semana_pt = dias_da_semana_pt.get(dia_da_semana_ingles, dia_da_semana_ingles)

# Formata a data para utilizar no prompt
data_atual = f"{dia_da_semana_pt}, {data_formatada}"


from dotenv import load_dotenv

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv('GENERATIVE_LANGUAGE_API_KEY')
os.environ["LANGCHAIN_API_KEY"] = os.getenv('LANGCHAIN_API_KEY')

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

def transfer_to_calendar_agent(input_str):
    return calendar_agent_executor.invoke({"input": input_str})
def transfer_to_travel_agent(input_str):
    return travel_agent_executor.invoke({"input": input_str})

ddg_search = DuckDuckGoSearchAPIWrapper()

travel_planing_tools = [
    Tool(
        name="DuckDuckGo Search",
        func=ddg_search.run,
        description="""Essa ferramenta DEVE ser utilizada para buscar eventos relevantes no período fornecido pelo usuário. 
        Ela é útil para obter informações sobre eventos ou atividades especiais que estão acontecendo na cidade de destino nas datas que o usuário informou. 
        O modelo deve usá-la para complementar as sugestões de atividades."""
    ),
    Tool(
        name="Weather Forecast",
        func=weatherapi_forecast_periods,
        description="""Essa ferramenta DEVE ser usada *antes* de gerar o roteiro turístico, após o modelo coletar todas as informações necessárias do usuário, incluindo as datas exatas. 
    O modelo deve consultar o clima separadamente para cada dia do período informado, garantindo que as atividades do roteiro sejam planejadas de acordo com as condições climáticas. 
    A previsão do tempo é um passo obrigatório quando é um fator relevante para o planejamento."""
    ),
    Tool(
        name="Query RAG",
        func=query_rag,
        description="""Esta ferramenta deve ser usada quando o modelo souber a cidade de destino e os interesses do usuário, com o objetivo de fornecer informações sobre pontos turísticos e atrações que se alinham com esses interesses. 
        O modelo deve utilizar essa ferramenta para sugerir atividades e lugares específicos a visitar, baseados na cidade e nos interesses fornecidos."""
    ),
    Tool(
        name="Calendar Agent",
        func=transfer_to_calendar_agent,
        description="Esse agente lida com tudo relacionado ao calendário."
    ),
]

google_calendar_tools = [
    Tool(
        name="Create Calendar List",
        func=create_calendar,
        description="""
        Use a função create_calendar_list para criar um novo calendário.
        Forneça o resumo (título) do calendário que você deseja criar.
        - Exemplo de uso: 'Meu Calendário de Viagens'
        - Essa função vai criar um novo calendário com o resumo fornecido.
        """
    ),
    Tool(
        name="List Calendar List",
        func=list_calendar_list,
        description="""
        Use a função list_calendar_list para obter a lista dos seus calendários disponíveis no Google Calendar.
        Se você quiser limitar o número de calendários retornados, forneça o número máximo desejado.
        - Exemplo de uso: Forneça o número máximo de calendários a serem listados, como 50. Se não quiser um limite, apenas diga para listar 200 o máximo por padrão.
        """
    ),
    Tool(
        name="List Calendar Events",
        func=list_calendar_events,
        description="""
        Use a função list_calendar_events para obter a lista de eventos de um calendário específico.
        Você precisa fornecer o ID do calendário e, opcionalmente, o número máximo de eventos a serem listados.
        - Exemplo de uso para o calendário principal: forneça 'primary' como o ID do calendário.
        - Exemplo de uso com limite: forneça o ID do calendário e o número máximo de eventos, como 'primary', 20.
        - Para listar eventos de um calendário específico, primeiro liste seus calendários para encontrar o ID correto.
        """
    ),
    Tool(
        name="Insert Calendar Event",
        func=insert_calendar_event,
        description="""
        Use a função Insert Calendar Event para adicionar um evento a um calendário.
        Você precisa fornecer um dicionário Python contendo os detalhes do evento.
        Se o timezone não for mencionado utilize "America/Fortaleza"
        Se o usuário informar o nome do calendário para inserir o evento chame a função list_calendar_list primeiro para adquirir a informação de calendar_id
        O dicionário deve ter a seguinte estrutura:
        {
            "calendar_id": "primary",
            "summary": "Jantar em restaurante regional em Ponta Negra",
            "location": "Restaurante regional em Ponta Negra",
            "description": "",
            "start": {
                "dateTime": "2024-01-01T19:00:00",
                "timeZone": "America/Fortaleza"
            },
            "end": {
                "dateTime": "2024-01-01T22:00:00",
                "timeZone": "America/Fortaleza"
            },
            "attendees": []
        }
        Ao final você DEVE fornecer o link do evento criado ao usuário além das informações do evento criado.
        """
    ),
    Tool(
        name="Main Agent",
        func=transfer_to_travel_agent,
        description="Transfere ao agente de turismo para perguntas não relacionadas a calendário"
    )
]

travel_planing_prompt = hub.pull("tales/agente_turismo")
google_calendar_prompt = hub.pull("tales/agente_calendario")

llm_with_stop = llm.bind(stop=["\nObservation"])

planing_prompt = travel_planing_prompt.partial(
    tools=render_text_description(travel_planing_tools),
    tool_names=", ".join([t.name for t in travel_planing_tools]),
)

calendar_prompt = google_calendar_prompt.partial(
    tools=render_text_description(google_calendar_tools),
    tool_names=", ".join([t.name for t in google_calendar_tools]),
)

history = ChatMessageHistory()
memory = ConversationBufferWindowMemory(k=20, chat_memory=history, memory_key="chat_history")

travel_planing_agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_log_to_str(x["intermediate_steps"]),
        "chat_history": lambda x: x["chat_history"],
        "data_atual": lambda x: data_atual,
    }
    | planing_prompt
    | llm_with_stop
    | ReActSingleInputOutputParser()
)

travel_agent_executor = AgentExecutor(agent=travel_planing_agent, tools=travel_planing_tools, verbose=True, memory=memory)

google_calendar_agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_log_to_str(x["intermediate_steps"]),
        "chat_history": lambda x: x["chat_history"],
        "data_atual": lambda x: data_atual,
    }
    | calendar_prompt
    | llm_with_stop
    | ReActSingleInputOutputParser()
)

calendar_agent_executor = AgentExecutor(agent=google_calendar_agent, tools=google_calendar_tools, verbose=True, memory=memory)
