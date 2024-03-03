import string
import secrets

ALPHABET = string.ascii_letters

from st_supabase_connection import SupabaseConnection

def create_token(digits: int = 4):
  
  token = ''.join(secrets.choice(alphabet) for i in range(digits)).upper()
   
  return token

def connect_supabase():
  conn = st.connection("supabase",type=SupabaseConnection)

return conn

def insert_votante(nome: str, email: str): 

  token = create_token()
  
  _, _ = supabase.table('votantes')
    .insert({"nome": nome, 
             "email": email,
             "token": token,
             "votou": False})
    .execute()
