import streamlit as st
from utils import db_utils

#token de admin, se necessário implementar sistema de autenticação e autorização
#para fins de jogos corporativos, não é necessário, e um token hardcoded
#é suficiente
TOKEN = 'admin'

st.title('Página de Gerenciamento da Votação')

with st.form("my_form"):
   st.write("Inside the form")
   nome = st.text_input('Nome')
   email = st.text_input('E-mail')
   
   submitted = st.form_submit_button("Cadastrar votante")
   if submitted:
       db_utils.insert_votante(nome: str, email: str)
