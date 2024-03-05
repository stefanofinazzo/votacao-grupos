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

def mainpage():
    st.title('Sistema de votação')
    
    conn = connect_supabase()
    app_config = get_config(conn)

    if not 'votante_autorizado' in st.session_state:
        st.session_state['votante_autorizado'] = False
      
    if not st.session_state['votante_autorizado']: 

        votante_atual = st.text_input('Coloque seu token de votação')
        
        if votante_atual in list(DICT_VOTANTES.keys()):
            st.session_state['votante_autorizado']
            st.session_state['grupo_votante'] = DICT_VOTANTES[votante_atual]
            st.success('Bem-vindo!')
            sleep(2)
            st.rerun()
    
        elif votante_atual is not None:
            st.error('Votante não localizado')
    
    else:
        #em votação
        pergunta_atual = app_config['pergunta_liberada']
        
        st.markdown('## Pergunta em votação: ' + pergunta_atual)
        st.markdown('### ' + 'PERGUNTA ATUAL AQUI')
      
        grupos_a_votar = list(range(1,8))
        grupos_a_votar.remove(st.session_state['grupo_votante'])
        
        grupo_escolhido = st.selectbox('Escolha o seu grupo', grupos_a_votar)
        
        if st.button('Votar'):
            st.write('Você escolheu o grupo ' + str(grupo_escolhido))
            #lógica para transferir o voto para db aqui
            #lógica para remover voto da lista aqui

################### PÁGINA PRINCIPAL ###################

if __name__ = '__main__':
    mainpage()

