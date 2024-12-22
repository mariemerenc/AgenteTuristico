# Agente de Planejamento de Viagens para Natal - RN

## Descrição do Projeto

Natal, capital do Rio Grande do Norte, é um destino turístico muito procurado no Brasil, famoso por suas belas praias e cultura nordestina. Muitos turistas que desejam explorar a região preferem planejar suas próprias viagens para economizar dinheiro, em vez de contratar guias turísticos.

Este projeto tem como objetivo auxiliar esses viajantes independentes, oferecendo um guia turístico personalizado através de uma interface conversacional baseada em inteligência artificial. O sistema utiliza um conjunto de agentes para interagir com os usuários em linguagem natural e, com base nas preferências e informações fornecidas, gerar um roteiro de viagem detalhado, incluindo atividades e sugestões de locais.

O diferencial deste projeto é a capacidade de criar um planejamento personalizado e, opcionalmente, agendar automaticamente os eventos da viagem no Google Calendar do usuário.

## Funcionalidades Principais

*   **Interface Conversacional:** Permite aos usuários interagir com o sistema utilizando linguagem natural para planejar suas viagens.
*   **Agente de Planejamento:** Cria roteiros de viagem personalizados com base nas preferências e interesses do usuário.
*   **Sugestões Detalhadas:** Inclui sugestões de atividades, atrações turísticas, restaurantes e horários para cada dia da viagem.
*   **Previsão do Tempo:** Integra a previsão do tempo para os dias da viagem, auxiliando no planejamento.
*   **Agendamento no Google Calendar (Opcional):** Permite que os usuários agendem automaticamente as atividades do roteiro no Google Calendar.
*   **Adaptação Personalizada:** Gera roteiros que se adaptam ao perfil e preferências do usuário, incluindo sugestões de acordo com o orçamento e gostos.
*   **Busca de Informações:** Utiliza ferramentas de busca para obter informações atualizadas sobre atrações, restaurantes e clima.

## Tecnologias e Ferramentas Utilizadas

Este projeto utiliza diversas ferramentas de Processamento de Linguagem Natural (PLN) e modelos de linguagem (LLM), juntamente com outras tecnologias essenciais para o funcionamento do sistema:

*   **Modelos de Linguagem (LLM):**
    *   `gemini-1.5-flash` (Google): Modelo para processamento de linguagem natural e geração de respostas.
*   **Framework de Agentes:**
    *   `Langchain`: Framework para criação de agentes e pipelines de processamento de linguagem natural.
*   **Ferramentas de Busca e Informação:**
    *   `Retrieval-Augmented Generation (RAG)`: Sistema de busca e recuperação de informações baseado em banco de dados vetoriais.
    *   `DuckDuckGo Search API`: Para busca de informações atualizadas na internet.
    *   `WeatherAPI`: Para obter informações meteorológicas detalhadas de uma determinada data.
*   **Bancos de Dados Vetoriais:**
    *   `Chroma`: Banco de dados vetorial para armazenamento de documentos e busca semântica.
