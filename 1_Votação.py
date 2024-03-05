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
          
             votante, votante_localizado = db_utils.localiza_votante(conn, email_votante)
             st.write(votante)
          
             if votante_localizado:
                 if token == votante['token']:
                     st.session_state['votante_autorizado'] = True
                     st.session_state['votante_atual'] = votante
                     st.success('Bem-vindo!')
                     sleep(2.5)
                     st.rerun()
                 else:
                     st.error('Token incorreto')
             else:
                 st.error('E-mail não cadastrado')

def widget_em_votacao(conn, app_config: dict) -> None:

    pergunta_atual_id = app_config['pergunta_liberada']
    pergunta_atual_nome = db_utils.localiza_pergunta(conn, pergunta_atual_id)
  
    st.markdown('## Pergunta em votação: ' + str(pergunta_atual))
    st.markdown('### ' + pergunta_atual_nome)
    
    if st.button('Votar'):
        pass

def mainpage():
    st.title('Sistema de votação')

    if not 'votante_autorizado' in st.session_state:
        st.session_state['votante_autorizado'] = False
            
    conn = db_utils.connect_supabase()
    app_config = db_utils.get_config(conn)
    
    if app_config['votacao_ativa']:
        if not st.session_state['votante_autorizado']: 
            widget_verifica_votante(conn)
        else:
            widget_em_votacao(conn, app_config)

    else:
        st.header('Votação ainda não liberada!')
        st.subheader('Por favor, aguarde a liberação!')


################### PÁGINA PRINCIPAL ###################

if __name__ == '__main__':
    mainpage()

