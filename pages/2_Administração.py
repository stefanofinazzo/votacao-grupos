############# PACOTES ##########################
from time import sleep

import streamlit as st

from utils import db_utils
from utils import vot_widgets

############# VARIÁVEIS GLOBAIS #################

#token de admin, se necessário implementar sistema de autenticação e autorização
#para fins de jogos corporativos, não é necessário, e um token hardcoded
#é suficiente

ADMIN_PASSWORD = st.secrets['admin_config']['ADMIN_PASSWORD']

############# FUNÇÕES E WIDGETS AUXILIARES ######

def alterar_tab(tab_choice: str) -> None:

      st.session_state['admin_tab'] = tab_choice

def widget_autenticacao_admin():
   
   with st.form("autenticar_admin"):
      st.write("Insira a senha de administrador")
      admin_password = st.text_input('Senha')
      
      submitted = st.form_submit_button("Enviar")
      
      if submitted:
         if admin_password == ADMIN_PASSWORD:
            st.session_state['admin_user'] = True
            st.success('Bem-vindo!')
            sleep(2.5)
            st.rerun()
         else:
            st.error('Senha inválida')

def logout_admin() -> None:
      st.session_state['admin_user'] = False
      st.success('Logout realizado')
      sleep(1)

############# PÁGINA PRINCIPAL ##################

def mainpage() -> None:      

      st.title('Gerenciamento da Votação')

      if 'admin_user' not in st.session_state or not st.session_state['admin_user']:
            widget_autenticacao_admin()
               
      else:
            conn = db_utils.connect_supabase()
            app_config = db_utils.get_config(conn)
               
            funcoes_tab = st.columns(5)
            
            if not 'admin_tab' in st.session_state:
                  st.session_state['admin_tab'] = 'configuracao'
                  
            with funcoes_tab[0]:
                  st.button('Configurações', on_click=(lambda: alterar_tab('configuracao')))
            
            with funcoes_tab[1]:
                  st.button('Gerenciar Perguntas', on_click=(lambda: alterar_tab('perguntas')))
            
            with funcoes_tab[2]:
                  st.button('Gerenciar Votantes', on_click=(lambda: alterar_tab('votantes')))
                  
            with funcoes_tab[3]:
                  st.button('Resultados', on_click=(lambda: alterar_tab('resultados')))
            
            with funcoes_tab[4]:
                  if st.button('Logout', on_click=(lambda: logout_admin())):
                        st.rerun()        #o st.rerun não pode aparecer dentro de um callback, por limitação do streamlit
            
            
            match st.session_state['admin_tab']:
                  case 'configuracao':
                        vot_widgets.widget_configurar_votacao(conn, app_config)
            
                  case'perguntas':
                        colunas_incluir_pergunta = st.columns(2)
                        with colunas_incluir_pergunta[0]:
                              st.markdown('#### Lista de Perguntas')
                              perguntas_df = vot_widgets.widget_lista_perguntas(conn)
                        with colunas_incluir_pergunta[1]:
                              st.markdown('#### Incluir Perguntas')
                              vot_widgets.widget_incluir_pergunta(conn, app_config, perguntas_df)
                              st.markdown('#### Excluir Perguntas')
                              vot_widgets.widget_excluir_pergunta(conn, app_config, perguntas_df)
            
                  case 'votantes':
                        colunas_incluir_votante = st.columns(2)
                        with colunas_incluir_votante[0]:
                              st.markdown('#### Lista de Votantes')
                              vot_widgets.widget_lista_votantes(conn)
                        with colunas_incluir_votante[1]:
                              st.markdown('#### Incluir, Alterar ou Excluir Votantes')
                              vot_widgets.widget_incluir_votante(conn, app_config)
                              vot_widgets.widget_excluir_votante(conn, app_config)
            
                  case 'resultados':   
                        vot_widgets.widget_resultados(conn, app_config)



if __name__ == '__main__':
   mainpage()
