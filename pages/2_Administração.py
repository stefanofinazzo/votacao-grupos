import streamlit as st
from utils import db_utils

#token de admin, se necessário implementar sistema de autenticação e autorização
#para fins de jogos corporativos, não é necessário, e um token hardcoded
#é suficiente
TOKEN = 'admin'

st.title('Página de Gerenciamento da Votação')

with st.form("my_form"):
   st.write("Inclusão de novos votantes")
   nome = st.text_input('Nome')
   email = st.text_input('E-mail')
   grupo = st.slider('Grupo', 1, 1, 7)
   
   submitted = st.form_submit_button("Cadastrar votante")
   if submitted:
      conn = db_utils.connect_supabase()
      db_utils.insert_votante(conn, nome, email, grupo)
      st.success('Votante incluído com sucesso!')
