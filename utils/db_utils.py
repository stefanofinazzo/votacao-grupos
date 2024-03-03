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

def insert_votante(nome: str, email: str, grupo: int): 

  token = create_token()
  
  _, _ = (supabase.table('votantes')
             .insert({"nome": nome, 
               "email": email,
               "grupo": grupo,
               "token": token,
               "votou": False})
            .execute()
         )
