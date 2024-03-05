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
                     if not votante['votou']:
                       st.session_state['votante_autorizado'] = True
                       st.session_state['votante_atual'] = votante
                       st.success('Bem-vindo!')
                       sleep(2.5)
                       st.rerun()
                     else:
                       st.error('Seu voto já foi computado!')
                 else:
                     st.error('Token incorreto')
             else:
                 st.error('E-mail não cadastrado')

def widget_em_votacao(conn, app_config: dict) -> None:

    pergunta_atual_id = app_config['pergunta_liberada']
    pergunta_atual_text = db_utils.localiza_pergunta(conn, pergunta_atual_id)['pergunta_texto']
  
    st.markdown('## Pergunta ' + str(pergunta_atual_id))
    st.markdown('### ' + pergunta_atual_text)

    email_votante_atual = st.session_state['votante_atual']['email']
    grupo_votante_atual = st.session_state['votante_atual']['grupo']

    lista_grupos_passiveis_voto = list(range(1,app_config['numero_grupos']+1))
    lista_grupos_passiveis_voto.remove(grupo_votante_atual)                                        

    grupo_selecionado = st.selectbox('Escolha a sua opção: ', lista_grupos_passiveis_voto)
  
    if st.button('Votar'):
        db_utils.insert_voto(conn, str(grupo_selecionado), pergunta_atual_id)
        st.session_state['votante_atual']['votou'] = True
        db_utils.atualiza_votante(conn, st.session_state['votante_atual'])
        st.session_state['votante_autorizado'] = False
        
        st.success('Voto realizado com sucesso!')
        sleep(2.5)
        st.rerun()

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

