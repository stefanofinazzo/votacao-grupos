import string
import secrets

import pandas as pd

import streamlit as st
from st_supabase_connection import SupabaseConnection

ALPHABET = string.ascii_letters

def create_token(digits: int = 4):
  
  token = ''.join(secrets.choice(ALPHABET) for i in range(digits)).upper()
   
  return token

@st.cache_resource
def connect_supabase():
  
  conn = st.connection("supabase",type=SupabaseConnection)

  return conn

def get_list_table(conn, table: str):
    
  data, _ = conn.query("*", table=table, ttl="10m").execute()

  rows = data[1]
  
  return rows

def get_config(conn):

  data, _ = conn.query("*", table='config', ttl="10m").execute()
  app_config = data[1][0]
  app_config.pop('onerow_id')     #esta coluna apenas força o trigger de unicidade de uma linha

  return app_config

def update_config(conn, app_config: dict) -> None:

    _, _ = (conn.table('config')
              .update(app_config)
              .eq('onerow_id', True)
              .execute()
         )

def delete_perguntas_acima_limite(conn, app_config: dict) -> None:
  
    _, _ = (conn.table('perguntas')
          .delete()
          .gt('pergunta_id', app_config['numero_perguntas'])
          .execute()
         )
  
def list_para_df(data_dict):

  df = pd.DataFrame.from_dict(data_dict)

  return df

def insert_pergunta(conn, n_pergunta: int, nome_pergunta: str): 
  
  _, _ = (conn.table('perguntas')
             .insert({"pergunta_id": n_pergunta, 
               "pergunta_texto": nome_pergunta})
            .execute()
         )

def delete_pergunta(conn, n_pergunta: int): 

  _, _ = (conn.table('perguntas')
          .delete()
          .eq('pergunta_id', n_pergunta)
          .execute()
         )

def localiza_votante(conn, email: str):

  data, test = (conn
             .query("*", table='votantes', ttl="10m")
             .eq('email', email)
             .execute()
            )

  st.write(data)
  st.write(test)

  votante = data[1][0]
  
  #if data[1] != []:
  #  votante = data[1][0]
  #else:
  #  votante = None

  return votante

def insert_votante(conn, nome: str, email: str, grupo: int): 

  token = create_token()
  
  _, _ = (conn.table('votantes')
             .insert({"nome": nome, 
               "email": email,
               "grupo": grupo,
               "token": token,
               "votou": False})
            .execute()
         )

def delete_votante(conn, email: str): 

  _, _ = (conn.table('votantes')
          .delete()
          .eq('email', email)
          .execute()
         )
