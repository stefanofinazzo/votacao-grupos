################ PACOTES ############################

from time import sleep

import streamlit as st

from utils import db_utils

########## CONFIGURAÇÃO DO STREAMLIT ################

st.set_page_config(page_title='Sistema de Votação', 
                   page_icon=None, 
                   layout="wide", 
                   initial_sidebar_state="collapsed", 
                   menu_items=None)

################### WIDGETS #########################

def widget_verifica_votante(conn):
  
    with st.form("auth_votante_form"):
                            
        email_votante = st.text_input('E-mail funcional', placeholder='Insira seu e-mail funcional aqui')
        token = st.text_input('Senha de acesso', placeholder='Insira o token de votação')
    
        submitted = st.form_submit_button("Entrar", type="primary")
          
        if submitted:
             st.write(email_votante)
          
             votante, votante_localizado = db_utils.localiza_votante(conn, email_votante)
    
             if votante_localizado:
                 if token == votante['token']
                     st.session_state['votante_autorizado'] = True
                     st.session_state['votante_atual'] = votante
                     st.success('Bem-vindo!')
                     sleep(2.5)
                     st.rerun()
                 else:
                     st.error('Token incorreto')
             else:
                 st.error('E-mail não cadastrado')

def widget_em_votacao(app_config: dict) -> None:

    pergunta_atual = app_config['pergunta_liberada']
    
    st.markdown('## Pergunta em votação: ' + pergunta_atual)
    st.markdown('### ' + 'PERGUNTA ATUAL AQUI')
    
    if st.button('Votar'):
        pass

def mainpage():
    st.title('Sistema de votação')

    if not 'votante_autorizado' in st.session_state:
        st.session_state['votante_autorizado'] = False
            
    conn = db_utils.connect_supabase()
    app_config = db_utils.get_config(conn)

    st.write(app_config)
    
    if app_config['votacao_ativa']:
        if not st.session_state['votante_autorizado']: 
            widget_verifica_votante(conn)
        else:
            widget_em_votacao(app_config)

    else:
        st.header('Votação ainda não liberada!\nPor favor, aguarde!')


################### PÁGINA PRINCIPAL ###################

if __name__ == '__main__':
    mainpage()

