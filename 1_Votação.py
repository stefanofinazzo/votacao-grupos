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
    
    conn = db_utils.connect_supabase()
    app_config = db_utils.get_config(conn)

    if not 'votante_autorizado' in st.session_state:
        st.session_state['votante_autorizado'] = False
      
    if not st.session_state['votante_autorizado']: 
      
        with st.form("auth_votante_form"):
                                
            email_votante = st.text_input('E-mail funcional', placeholder='Insira seu e-mail funcional aqui')
            token = st.text_input('Senha de acesso', placeholder='Insira o token de votação')
        
            submitted = st.form_submit_button("Entrar", type="primary")
              
            if submitted:
              
                 votante_localizado = db_utils.delete_perguntalocaliza_votante(conn, email_votante)

                 st.write(votante_localizado)
              
                 #st.success('Pergunta excluída com sucesso!')
                 #sleep(5)
                 #st.rerun()
              
    else:
        #em votação
        pergunta_atual = app_config['pergunta_liberada']
        
        st.markdown('## Pergunta em votação: ' + pergunta_atual)
        st.markdown('### ' + 'PERGUNTA ATUAL AQUI')
        
        if st.button('Votar'):
            pass

################### PÁGINA PRINCIPAL ###################

if __name__ == '__main__':
    mainpage()

