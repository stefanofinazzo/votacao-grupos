############# PACOTES ##################

from time import sleep

from typing import List

import pandas as pd
import streamlit as st

from utils import db_utils

############# VARIÁVEIS GLOBAIS ########

#token de admin, se necessário implementar sistema de autenticação e autorização
#para fins de jogos corporativos, não é necessário, e um token hardcoded
#é suficiente

ADMIN_PASSWORD = 'admin'
MAX_QUESTOES = 10

############# FUNÇÕES AUXILIARES #######

def lista_perguntas_no_banco(perguntas_df: pd.DataFrame) -> List:

      lista_perguntas = perguntas_df['pergunta_id'].unique().tolist()

      return lista_perguntas
      
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
               
def widget_incluir_pergunta(perguntas_df: pd.DataFrame) -> None:
   
   with st.form("incluir_pergunta"):
         st.write("Inclusão de novas perguntas")

         lista_perguntas_atuais = lista_perguntas_no_banco(perguntas_df)
         lista_perguntas_total = list(range(1, MAX_QUESTOES + 1))
         lista_perguntas_ausentes = [pergunta_id for pergunta_id in lista_perguntas_total if pergunta_id not in lista_perguntas_atuais]
         
         st.write(lista_perguntas_atuais)
         
         n_pergunta = st.selectbox('Número da pergunta', lista_perguntas_ausentes)
         nome_pergunta = st.text_input('Nome da pergunta')
         
         submitted = st.form_submit_button("Cadastrar pergunta", type="primary")
      
         if submitted:
            conn = db_utils.connect_supabase()
            db_utils.insert_pergunta(conn, n_pergunta, nome_pergunta)
            st.success('Pergunta incluída com sucesso!')
            sleep(2)
            st.rerun()

def widget_excluir_pergunta():
   
   with st.form("excluir_pergunta"):
      st.write("Exclusão de pergunta")
      n_pergunta = st.text_input('Número da Pergunta')
      
      submitted = st.form_submit_button("Excluir Pergunta", type="primary")
      
      if submitted:
         conn = db_utils.connect_supabase()
         db_utils.delete_pergunta(conn, n_pergunta)
         st.success('Pergunta excluída com sucesso!')
         sleep(2)
         st.rerun()

def widget_lista_perguntas() -> pd.DataFrame:
      
   st.markdown('### Lista de Perguntas')
   conn = db_utils.connect_supabase()
   perguntas_list = db_utils.get_list_table(conn, table='perguntas')
   perguntas_df = db_utils.list_para_df(perguntas_list)
   perguntas_df = perguntas_df.sort_values(by='pergunta_id')
   st.dataframe(perguntas_df)
   return perguntas_df
      
def widget_incluir_votante():
   
   with st.form("incluir_votante"):
         st.write("Inclusão de novos votantes")
         nome = st.text_input('Nome')
         email = st.text_input('E-mail')
         grupo = st.slider('Grupo', 1, 1, 7)
         
         submitted = st.form_submit_button("Cadastrar votante", type="primary")
      
         if submitted:
            conn = db_utils.connect_supabase()
            db_utils.insert_votante(conn, nome, email, grupo)
            st.success('Votante incluído com sucesso!')
            sleep(2)
            st.rerun()

def widget_excluir_votante():
   
   with st.form("excluir_votante"):
      st.write("Exclusão de votante")
      email = st.text_input('E-mail')
      
      submitted = st.form_submit_button("Excluir votante", type="primary")
      
      if submitted:
         conn = db_utils.connect_supabase()
         db_utils.delete_votante(conn, email)
         st.success('Votante excluído com sucesso!')
         sleep(2)
         st.rerun()    

def widget_lista_votantes():
   st.markdown('### Lista de Votantes')
   conn = db_utils.connect_supabase()
   votantes_list = db_utils.get_list_table(conn, table='votantes')
   votantes_df = db_utils.list_para_df(votantes_list)
   votantes_df = votantes_df.sort_values(by='nome')
   st.dataframe(votantes_df)
   
def widget_resultados():
   pass

def widget_configurar_votacao():
      
   numero_grupos = st.slider('Número de grupos', 1, 20)
      

   
   
############# PÁGINA PRINCIPAL #########

def mainpage():      
      
   st.title('Página de Gerenciamento da Votação')

   if 'admin_user' not in st.session_state or not st.session_state['admin_user']:
      widget_autenticacao_admin()
               
   else:
      funcoes_tab = st.tabs(['Gerenciar Questões', 'Gerenciar Votantes', 'Resultados', 'Reiniciar votação'])

      with funcoes_tab[0]:
         colunas_incluir_pergunta = st.columns(2)
         with colunas_incluir_pergunta[0]:
               perguntas_df = widget_lista_perguntas()
         with colunas_incluir_pergunta[1]:
               widget_incluir_pergunta(perguntas_df)
               widget_excluir_pergunta()
         
      with funcoes_tab[1]:
         colunas_incluir_votante = st.columns(2)
         with colunas_incluir_votante[0]:
               widget_lista_votantes()
         with colunas_incluir_votante[1]:
               widget_incluir_votante()
               widget_excluir_votante()

      with funcoes_tab[2]:
         widget_resultados()

      with funcoes_tab[3]:
         widget_configurar_votacao()

if __name__ == '__main__':
   mainpage()
