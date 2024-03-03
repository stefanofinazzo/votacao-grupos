import streamlit as st
from utils import db_utils

#token de admin, se necessário implementar sistema de autenticação e autorização
#para fins de jogos corporativos, não é necessário, e um token hardcoded
#é suficiente
ADMIN_PASSWORD = 'admin'

st.title('Página de Gerenciamento da Votação')

funcoes_tab = st.tabs(['Inclusão', 'Exclusão'])

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
            
############# PÁGINA PRINCIPAL #########

def mainpage():
   
   if 'admin_user' not in st.session_state or not st.session_state['admin_user']:
      widget_autenticacao_admin()
               
   else:
      with funcoes_tab[0]:
         widget_incluir_votante()

if __name__ == '__main__':
   mainpage()
