############# PACOTES ##################

from time import sleep

import streamlit as st
from utils import db_utils

############# VARIÁVEIS GLOBAIS ########

#token de admin, se necessário implementar sistema de autenticação e autorização
#para fins de jogos corporativos, não é necessário, e um token hardcoded
#é suficiente

ADMIN_PASSWORD = 'admin'


############# WIDGETS ##################

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

def widget_incluir_votante():
   
   with st.form("incluir_votante"):
         st.write("Inclusão de novos votantes")
         nome = st.text_input('Nome')
         email = st.text_input('E-mail')
         grupo = st.slider('Grupo', 1, 1, 7)
         
         submitted = st.form_submit_button("Cadastrar votante")
      
         if submitted:
            conn = db_utils.connect_supabase()
            db_utils.insert_votante(conn, nome, email, grupo)
            st.success('Votante incluído com sucesso!')

def widget_excluir_votante():
   
   with st.form("excluir_votante"):
      st.write("Exclusão de votante")
      email = st.text_input('E-mail')
      
      submitted = st.form_submit_button("Excluir votante")
      
      if submitted:
         conn = db_utils.connect_supabase()
         db_utils.delete_votante(conn, email)
         st.success('Votante excluído com sucesso!')

def widget_lista_votantes():

   conn = db_utils.connect_supabase()
   votantes_list = db_utils.get_list_votantes(conn)
   votantes_df = db_utils.list_votantes_para_df(votantes_list)
   st.write(votantes_list)
   st.dataframe(votantes_df)
   
def widget_resultados():
   pass

def widget_reiniciar_votacao():
   pass
   
############# PÁGINA PRINCIPAL #########

def mainpage():
   st.title('Página de Gerenciamento da Votação')

   if 'admin_user' not in st.session_state or not st.session_state['admin_user']:
      widget_autenticacao_admin()
               
   else:
      funcoes_tab = st.tabs(['Lista de Votantes', 'Inclusão', 'Exclusão', 'Resultados', 'Reiniciar votação'])

      with funcoes_tab[0]:
         widget_lista_votantes()
         
      with funcoes_tab[1]:
         widget_incluir_votante()

      with funcoes_tab[2]:
         widget_excluir_votante()

      with funcoes_tab[3]:
         widget_resultados()

      with funcoes_tab[4]:
         widget_reiniciar_votacao()

if __name__ == '__main__':
   mainpage()
