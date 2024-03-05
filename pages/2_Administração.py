############# PACOTES ##################

from time import sleep

from typing import List

import pandas as pd
import plotly.express as px
import streamlit as st

from utils import db_utils

############# VARIÁVEIS GLOBAIS ########

#token de admin, se necessário implementar sistema de autenticação e autorização
#para fins de jogos corporativos, não é necessário, e um token hardcoded
#é suficiente

ADMIN_PASSWORD = 'admin'

############# FUNÇÕES AUXILIARES #######

def lista_perguntas_no_banco(perguntas_df: pd.DataFrame):

      lista_perguntas = perguntas_df['pergunta_id'].unique().tolist()
            
      return lista_perguntas

def alterar_tab(tab_choice: str) -> None:

      st.session_state['admin_tab'] = tab_choice

def votos_bar_plot(votos_pergunta_df: pd.DataFrame):

      fig = px.bar(votos_pergunta_df, x='voto', y='n_votos')
      fig.show()

      st.plotly_chart(fig, use_container_width=True)

def calcula_pontuacao(votos_pergunta_df: pd.DataFrame, total_grupos: int):

      ranking_df = votos_pergunta_df.copy()
      ranking_df['ranking'] = ranking_df['n_votos'].rank(method='dense', ascending=True)
      ranking_df['pontuacao'] = total_grupos+ 1 - ranking_df['ranking'] 
      ranking_df = ranking_df.sort_values(by='ranking', ascending=True)

      return ranking_df
      
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
               
def widget_incluir_pergunta(app_config: dict, perguntas_df: pd.DataFrame) -> None:
   
   with st.form("incluir_pergunta"):
         
         st.write("Inclusão de novas perguntas")

         if not perguntas_df.empty:
               lista_perguntas_atuais = lista_perguntas_no_banco(perguntas_df)
               lista_perguntas_total = list(range(1, app_config['numero_perguntas'] + 1))
               lista_perguntas_ausentes = [pergunta_id for pergunta_id in lista_perguntas_total if pergunta_id not in lista_perguntas_atuais]
         else:
               lista_perguntas_ausentes = list(range(1, app_config['numero_perguntas']  + 1))

         if len(lista_perguntas_atuais) < app_config['numero_perguntas']:
               n_pergunta = st.selectbox('Número da pergunta', lista_perguntas_ausentes)
               nome_pergunta = st.text_input('Nome da pergunta')
               submitted = st.form_submit_button("Cadastrar pergunta", type="primary", disabled=False)
               
         else:
               st.markdown('#### Todas perguntas já cadastradas!')
               submitted = st.form_submit_button("Cadastrar pergunta", type="primary", disabled=True)
      
         if submitted:
            conn = db_utils.connect_supabase()
            db_utils.insert_pergunta(conn, n_pergunta, nome_pergunta)
            st.success('Pergunta incluída com sucesso!')
            sleep(2)
            st.rerun()

def widget_excluir_pergunta(perguntas_df: pd.DataFrame) -> None:

      st.write("Exclusão de pergunta")
      
      if not perguntas_df.empty:
         
            with st.form("excluir_pergunta"):
                                    
                  lista_perguntas_atuais = lista_perguntas_no_banco(perguntas_df)
                  n_pergunta = st.selectbox('Número da pergunta', lista_perguntas_atuais)
            
                  submitted = st.form_submit_button("Excluir Pergunta", type="primary")
                  
                  if submitted:
                     conn = db_utils.connect_supabase()
                     db_utils.delete_pergunta(conn, n_pergunta)
                     st.success('Pergunta excluída com sucesso!')
                     sleep(2)
                     st.rerun()
                        
      else:
            st.markdown('#### Sem perguntas cadastradas no momento!')
            
def widget_lista_perguntas() -> pd.DataFrame:
      
   st.markdown('### Lista de Perguntas')
   conn = db_utils.connect_supabase()
   perguntas_list = db_utils.get_list_table(conn, table='perguntas')
   perguntas_df = db_utils.list_para_df(perguntas_list)
   if not perguntas_df.empty:
         perguntas_df = perguntas_df.sort_values(by='pergunta_id')
         st.dataframe(perguntas_df)
   else:
         st.markdown('#### Sem perguntas cadastradas no momento!')
         
   return perguntas_df
      
def widget_incluir_votante(app_config):
   
   with st.form("incluir_votante"):
         st.write("Inclusão de novos votantes")
         nome = st.text_input('Nome')
         email = st.text_input('E-mail')
         grupo = st.slider('Grupo', 1, 1, app_config['numero_grupos'])
         
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

def widget_lista_votantes(conn):
   st.markdown('### Lista de Votantes')
   votantes_list = db_utils.get_list_table(conn, table='votantes')
   votantes_df = db_utils.list_para_df(votantes_list)
   votantes_df = votantes_df.sort_values(by='nome')
   st.dataframe(votantes_df)
   
def widget_resultados(conn):
      st.markdown('## Resultados')
      
      votos_list = db_utils.get_list_table(conn, table='contagem_votos')
      votos_df = db_utils.list_para_df(votos_list)
      
      if not votos_df.empty:
            
            colunas_resultados = st.columns(2)
            
            perguntas_com_votos = votos_df['pergunta_id'].unique().tolist()
            
            for pergunta in perguntas_com_votos:

                  st.markdown('##### Pergunta ' + str(pergunta))
                  
                  colunas_resultados = st.columns(2)
                  
                  filtro_pergunta = votos_df['pergunta_id'] == pergunta
                  votos_pergunta_df = votos_df[filtro_pergunta]
                  
                  with colunas_resultados[0]:
                        st.dataframe(votos_pergunta_df)
                        ranking_df = calcula_pontuacao(votos_pergunta_df)
                        st.dataframe(ranking_df)
                        
                  with colunas_resultados[1]:
                        votos_bar_plot(votos_pergunta_df)
                        
      else:
            st.markdown('#### Urna vazia!')
      
def display_metrics(app_config: dict) -> None:

      metrics = st.columns(3)
      
      with metrics[0]:
            st.metric('Número de grupos', app_config['numero_grupos'])
      with metrics[1]:
            st.metric('Número de perguntas', app_config['numero_perguntas'])
      with metrics[2]:
            if app_config['votacao_ativa']:
                  st.metric('Votação', 'ATIVA')
            else:
                   st.metric('Votação', 'FECHADA')
                  
def widget_set_grupos(conn, app_config: dict) -> None: 

      st.markdown('#### Configuração de grupos')
      
      with st.form("numero_grupos"):
      
            if not app_config['votacao_ativa']:
                  numero_grupos = st.slider('Número de grupos', 1, 10, app_config['numero_grupos'])
                  submitted_grupos = st.form_submit_button("Configurar", type="primary")
            else:
                  numero_grupos = st.slider('Número de grupos', 1, 10, app_config['numero_grupos'], disabled=True)
                  submitted_grupos = st.form_submit_button("Configurar", type="primary", disabled=True)
                  
            if submitted_grupos:
                  app_config['numero_grupos'] = numero_grupos
                  db_utils.update_config(conn, app_config)
                  st.successs('Configuração atualizada com sucesso!')
                  sleep(2.5)
                  st.rerun()

def widget_set_perguntas(conn, app_config: dict) -> None:

      st.markdown('#### Configuração de perguntas')
      
      with st.form("numero_perguntas"):
      
            st.warning('Atenção: as perguntas já cadastradas acima do limite serão eliminadas!')
      
            if not app_config['votacao_ativa']:
                  numero_perguntas = st.slider('Número de perguntas', 1, 20, app_config['numero_perguntas'])
                  submitted_perguntas = st.form_submit_button("Configurar", type="primary")
            else:
                  numero_perguntas = st.slider('Número de perguntas', 1, 20, app_config['numero_perguntas'], disabled=True)
                  submitted_perguntas = st.form_submit_button("Configurar", type="primary", disabled=True)
                  
            if submitted_perguntas:
                  app_config['numero_perguntas'] = numero_perguntas
                  db_utils.delete_perguntas_acima_limite(conn, app_config)     #eliminando as perguntas acima do limite
                  db_utils.update_config(conn, app_config)
                  st.success('Configuração atualizada com sucesso!')
                  sleep(2.5)
                  st.rerun()

def widget_liberar_votacao(conn, app_config: dict):

      st.markdown('#### Liberar votação')
      
      with st.form("liberar_votacao"):

            if not app_config['votacao_ativa']:
                  numero_pergunta_a_liberar = st.slider('Número da pergunta a liberar', 
                                                        1, 
                                                        app_config['numero_perguntas'],
                                                        app_config['pergunta_liberada'],
                                                        disabled=False)
                  submitted_liberar_votacao = st.form_submit_button("Liberar votação", type="primary")
            else:
                  numero_pergunta_a_liberar = st.slider('Número da pergunta a liberar', 
                                                        1, 
                                                        app_config['numero_perguntas'],
                                                        app_config['pergunta_liberada'],
                                                        disabled=True)
                  submitted_liberar_votacao = st.form_submit_button("Liberar votação", type="primary", disabled=True)
            
            if submitted_liberar_votacao:
                  
                  perguntas_list = db_utils.get_list_table(conn, table='perguntas')
                  perguntas_df = db_utils.list_para_df(perguntas_list)
                  lista_perguntas_atuais = lista_perguntas_no_banco(perguntas_df)
                  pergunta_valida = True if (numero_pergunta_a_liberar in lista_perguntas_atuais) else False
      
                  if pergunta_valida:
                        app_config['votacao_ativa'] = True
                        app_config['pergunta_liberada'] = numero_pergunta_a_liberar
                        
                        db_utils.update_config(conn, app_config)
                        st.success('Votação liberada com sucesso!')
                        sleep(2.5)
                        st.rerun()
                  else:
                        st.error('Pergunta ' + str(numero_pergunta_a_liberar) + 'não cadastrada!')

def widget_fechar_votacao(conn, app_config: dict):

      st.markdown('#### Fechar votação')
      
      with st.form("fechar_votacao"):

            if app_config['votacao_ativa']:
                  submitted_fechar_votacao = st.form_submit_button("Fechar votação", type="primary")
            else:
                  submitted_fechar_votacao = st.form_submit_button("Fechar votação", type="primary", disabled=True)
                              
            if submitted_fechar_votacao:
                  app_config['votacao_ativa'] = False
                  db_utils.update_config(conn, app_config)
                  st.success('Votação fechada com sucesso!')
                  sleep(2.5)
                  st.rerun()

def widget_reinicializar_votantes(conn, app_config: dict):

      st.markdown('#### Reinicializar votantes')
      
      with st.form("reinicializar_votantes"):

            if app_config['votacao_ativa']:
                  submitted_reinicializar_votantes = st.form_submit_button("Reinicializar votantes", type="primary", disabled=True)
            else:
                  submitted_reinicializar_votantes = st.form_submit_button("Reinicializar votantes", type="primary", disabled=False)
                              
            if submitted_reinicializar_votantes:
                  db_utils.reinicia_votantes(conn)
                  st.success('Votantes liberados para votação!')
                  sleep(2.5)
                  st.rerun()
                        
def widget_configurar_votacao(app_config: dict):

      conn = db_utils.connect_supabase()

      display_metrics(app_config)

      colunas_config = st.columns(2)

      with colunas_config[0]:
            widget_set_grupos(conn, app_config)
            widget_set_perguntas(conn, app_config)

      with colunas_config[1]:
            widget_reinicializar_votantes(conn, app_config)
            widget_liberar_votacao(conn, app_config)
            widget_fechar_votacao(conn, app_config)
                 
############# PÁGINA PRINCIPAL #########

def mainpage():      

   st.title('Página de Gerenciamento da Votação')

   if 'admin_user' not in st.session_state or not st.session_state['admin_user']:
      widget_autenticacao_admin()
               
   else:
      conn = db_utils.connect_supabase()
      app_config = db_utils.get_config(conn)
         
      funcoes_tab = st.columns(4)

      if not 'admin_tab' in st.session_state:
            st.session_state['admin_tab'] = 'perguntas'
            
      with funcoes_tab[0]:
            st.button('Gerenciar Perguntas', on_click=(lambda: alterar_tab('perguntas')))

      with funcoes_tab[1]:
            st.button('Gerenciar Votantes', on_click=(lambda: alterar_tab('votantes')))

      with funcoes_tab[2]:
            st.button('Resultados', on_click=(lambda: alterar_tab('resultados')))

      with funcoes_tab[3]:
            st.button('Configurações', on_click=(lambda: alterar_tab('configuracao')))
      
      if st.session_state['admin_tab'] == 'perguntas':
         colunas_incluir_pergunta = st.columns(2)
         with colunas_incluir_pergunta[0]:
               perguntas_df = widget_lista_perguntas()
         with colunas_incluir_pergunta[1]:
               widget_incluir_pergunta(app_config, perguntas_df)
               widget_excluir_pergunta(perguntas_df)

      elif st.session_state['admin_tab'] == 'votantes':
         colunas_incluir_votante = st.columns(2)
         with colunas_incluir_votante[0]:
               widget_lista_votantes(conn)
         with colunas_incluir_votante[1]:
               widget_incluir_votante(app_config)
               widget_excluir_votante()

      elif st.session_state['admin_tab'] == 'resultados':   
         widget_resultados(conn)

      elif st.session_state['admin_tab'] == 'configuracao':  
         widget_configurar_votacao(app_config)

if __name__ == '__main__':
   mainpage()
