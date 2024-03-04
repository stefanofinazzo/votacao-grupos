import string
import secrets

import streamlit as st
from st_supabase_connection import SupabaseConnection

ALPHABET = string.ascii_letters

def create_token(digits: int = 4):
  
  token = ''.join(secrets.choice(ALPHABET) for i in range(digits)).upper()
   
  return token

def connect_supabase():
  
  conn = st.connection("supabase",type=SupabaseConnection)

  return conn

def get_dict_votantes(conn):
    
  rows = conn.query("*", table="votantes", ttl="10m").execute()
  
  return rows

def dict_votantes_para_df(votantes_dict):

  pass
  
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
