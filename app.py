import streamlit as st
from agents import travel_agent_executor

if __name__ == '__main__':

    st.title('Agente Turístico')

    if 'messages' not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message['role']):
            st.markdown(message['content'])

    if prompt := st.chat_input('Digite a sua mensagem.'):
        st.session_state.messages.append({'role': 'user', 'content': prompt})

        with st.chat_message('user', avatar='🧑‍💻'):
            st.markdown(prompt)

        with st.chat_message('ai', avatar='🤖'):
            response = travel_agent_executor.invoke({"input": prompt})
            agent_response = response['output']
            st.markdown(agent_response)

        st.session_state.messages.append({'role': 'assistant', 'content': agent_response})