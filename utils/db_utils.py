# -*- coding: utf-8 -*-

################ PACOTES #################

from typing import List, Dict, Tuple

import pandas as pd

import streamlit as st
from st_supabase_connection import SupabaseConnection

############## FUNÇÕES ###################

@st.cache_resource
def connect_supabase() -> SupabaseConnection:
    """
    Wrapper para criar conexão ao banco de dados em Supabase.

    Returns
    -------
    SupabaseConnection
        Conexão criada.

    """
  
    conn = st.connection("supabase",type=SupabaseConnection)
    
    return conn

def get_list_table(conn: SupabaseConnection, table: str) -> List:
    """
    Faz uma query SELECT * numa tabela do banco de dados,
    e retorna a lista de rows de saída.

    Parameters
    ----------
    conn : SupabaseConnection
        Conexão ao banco de dados.
    table : str
        Tabela a ser consultada.

    Returns
    -------
    rows : List
        Lista com os rows da consulta.

    """
    
    data, _ = conn.query("*", table=table, ttl="10m").execute()
    
    rows = data[1]
    
    return rows

def get_config(conn: SupabaseConnection) -> Dict:
    """
    Obtém a configuração atual do aplicativo armazenada no banco de dados.

    Parameters
    ----------
    conn : SupabaseConnection
        Conexão ao banco de dados.

    Returns
    -------
    app_config : Dict
        Dicionário com as configurações do app.

    """

    data, _ = conn.query("*", table='config', ttl="10m").execute()
    app_config = data[1][0]
    app_config.pop('onerow_id')     #esta coluna apenas força o trigger de unicidade de uma linha
    
    return app_config

def update_config(conn: SupabaseConnection, app_config: Dict) -> None:
    """
    Atualiza as configurações do aplicativo armazenadas no banco de dados.

    Parameters
    ----------
    conn : SupabaseConnection
        Conexão ao banco de dados.
    app_config : Dict
        Dicionário com as novas configurações do app..
    """

    _, _ = (conn.table('config')
              .update(app_config)
              .eq('onerow_id', True)
              .execute()
         )
  
def list_para_df(data_dict: List) -> pd.DataFrame:
    """
    Faz a conversão de uma lista de dicionários para um data frame do pandas.
    
    Parameters
    ----------
    data_dict : List
        Lista de dicionários.

    Returns
    -------
    df : pd.DataFrame
    
        Dataframe obtido a partir do dict.
    """

    df = pd.DataFrame.from_dict(data_dict)
    
    return df

def insert_pergunta(conn: SupabaseConnection, n_pergunta: int, nome_pergunta: str) -> None:
    """
    Insere uma nova pergunta no banco de dados.

    Parameters
    ----------
    conn : SupabaseConnection
        Conexão ao banco de dados.
    n_pergunta : int
        Número da pergunta a inserir.
    nome_pergunta : str
        Nome da pergunta a inserir.
    """
  
    _, _ = (conn.table('perguntas')
               .insert({"pergunta_id": n_pergunta, 
                 "pergunta_texto": nome_pergunta})
              .execute()
           )

def delete_pergunta(conn: SupabaseConnection, n_pergunta: int) -> None:
    """
    Remove uma pergunta do banco de dados.

    Parameters
    ----------
    conn : SupabaseConnection
        Conexão ao banco de dados.
    n_pergunta : int
        Número da pergunta a ser removida.
    """
    
    _, _ = (conn.table('perguntas')
            .delete()
            .eq('pergunta_id', n_pergunta)
            .execute()
           )

def delete_perguntas_acima_limite(conn: SupabaseConnection, app_config: dict) -> None:
    """
    Remove todas perguntas acima do limite atual de perguntas nas configurações
    do aplicativo.
    
    Por exemplo, o app está configurado para 5 perguntas, e há 8 perguntas no
    banco. As perguntas 6, 7 e 8 serão eliminadas.

    Parameters
    ----------
    conn : SupabaseConnection
        Conexão ao banco de dados.
    app_config : dict
        Dicionário com as configurações do aplicativo.
    """
    
    _, _ = (conn.table('perguntas')
          .delete()
          .gt('pergunta_id', app_config['numero_perguntas'])
          .execute()
         )

def delete_todas_perguntas(conn: SupabaseConnection) -> None:
    """
    Remove todas perguntas do banco de dados

    Parameters
    ----------
    conn : SupabaseConnection
        Conexão ao banco de dados.
    """
    
    _, _ = (conn.table('perguntas')
          .delete()
          .gt('pergunta_id', 0)       #a API do Supabase exige alguma condição no delete; esta condição é sempre atendida (as perguntas sempre tem id > 0)
          .execute()
         )
  
def localiza_pergunta(conn: SupabaseConnection, pergunta_id: int) -> Dict:
    """
    

    Parameters
    ----------
    conn : SupabaseConnection
        Conexão ao banco de dados.
    pergunta_id : int
        Número da pergunta.

    Returns
    -------
    pergunta: Dict
        Um dict com os dados da pergunta localizada.
    """
    
    data, _ = (conn
               .table('perguntas')
               .select("*")
               .eq('pergunta_id', pergunta_id)
               .execute()
               )
   	
    pergunta = data[1][0]
	
    return pergunta
  
def localiza_votante(conn: SupabaseConnection, email: str) -> Tuple[Dict, bool]:
    """
    Localiza o votante com email dado.

    Parameters
    ----------
    conn : SupabaseConnection
        Conexão ao banco de dados.
    email : str
        E-mail de cadastro do votante.

    Returns
    -------
    votante, localizado: Tuple[Dict, bool]
        votante é um dicionário com os dados do votante (None se o votante não
                                                         foi localizado);
        localizado é um booleano que indica se o votante foi ou não localizado
        (True se sim, False se não).
    """

    data, _ = (conn
               .table('votantes')
               .select("*")
               .eq('email', email)
               .execute()
              )
      
    if data[1] != []:
        votante = data[1][0]
        localizado = True
    else:
        votante = None
        localizado = False
    
    return votante, localizado
  
def insert_votante(conn: SupabaseConnection, nome: str, email: str, grupo: int, token: str) -> None: 
    """
    Insere um votante no banco de dados.

    Parameters
    ----------
    conn : SupabaseConnection
        Conexão ao banco de dados.
    nome : str
        Nome do votante.
    email : str
        E-mail do votante (chave primária de identificação)
    grupo : int
        Grupo do votante.
    token: str
        Token de autenticação do votante.
    """
    
    _, _ = (conn.table('votantes')
               .upsert({"nome": nome, 
                 "email": email,
                 "grupo": grupo,
                 "token": token,
                 "votou": False})
              .execute()
           )

def delete_votante(conn: SupabaseConnection, email: str) -> None:
    """
    Remove o votante do banco de dados.

    Parameters
    ----------
    conn : SupabaseConnection
        Conexão ao banco de dados.
    email : str
        E-mail a ser removido do banco.
    """

    _, _ = (conn.table('votantes')
            .delete()
            .eq('email', email)
            .execute()
           )
	
def delete_votantes_acima_grupo_limite(conn: SupabaseConnection, app_config: dict) -> None:
    """
    Remove todos votantes acima do grupo máximo nas configurações do app.
    
    Exemplo: o app está configurado para 4 grupos, mas há votantes nos grupos
    1,2, 4, 5, 8
    
    Os votantes dos grupos 5 e 8 serão eliminados.

    Parameters
    ----------
    conn : SupabaseConnection
        Conexão ao banco de dados.
    app_config : dict
        Dicionário com as configurações atuais do app.
    """
    _, _ = (conn.table('votantes')
          .delete()
          .gt('grupo', app_config['numero_grupos'])
          .execute()
         )

def delete_todos_votantes(conn: SupabaseConnection) -> None:
    """
    Remove todos votantes do banco de dados.

    Parameters
    ----------
    conn : SupabaseConnection
        Conexão ao banco de dados.
    """
  
    _, _ = (conn.table('votantes')
          .delete()
          .neq('token', '')       #o supabase não permite, via API, queries sem condições.
          .execute()
         )
	
def atualiza_votante(conn: SupabaseConnection, votante: dict) -> None:
    """
    Atualiza o votante no banco de dados.

    Parameters
    ----------
    conn : SupabaseConnection
        Conexão ao banco de dados.
    votante : dict
        Dicionário com os dados do votante a serem atualizados.
    """

    email = votante['email']
    
    _, _ = (conn.table('votantes')
            .update(votante)
            .eq('email', email)
            .execute()
       )

def insert_voto(conn:SupabaseConnection, voto: str, pergunta_id: int) -> None: 
    """
    Insere um voto no banco de dados.

    Parameters
    ----------
    conn : SupabaseConnection
        Conexão ao banco de dados.
    voto : str
        String com o conteúdo do voto.
    pergunta_id : int
        Número da pergunta que está sendo votada.
    """
  
    _, _ = (conn.table('votos')
               .insert({"voto": voto, 
                 "pergunta_id": pergunta_id})
              .execute()
           )

def deletar_votos(conn: SupabaseConnection, pergunta_id: int = None) -> None: 
    """
    Remove todos votos da urna. Se o número da pergunta (pergunta_id)
    for informado, deleta apenas os votos de pergunta_id. Caso contrário,
    remove todos votos (limpa a urna)

    Parameters
    ----------
    conn : SupabaseConnection
        Conexão ao banco de dados.
    pergunta_id : int, optional
        Identificação da pergunta. Se não houver, deleta votos de todas
        perguntas (limpa a urna)
    """

    if pergunta_id:
        _, _ = (conn.table('votos')
            .delete()
			.eq('pergunta_id', pergunta_id)
			.execute()
		 )
    else:
        _, _ = (conn.table('votos')
			.delete()
			.gt('voto_id', 0)
			.execute()
		 )
	
def reinicia_votantes(conn: SupabaseConnection) -> None:
    """
    Reinicia todos votantes atuais.

    Parameters
    ----------
    conn : SupabaseConnection
        Conexão ao banco de dados.
    """
    
    update_list = []
    votantes_list = get_list_table(conn, table='votantes')
	
    #é feita por requisição a requisição na , o que é lento
    #isto poderia ser agilizado escrevendo uma função em PL/pgSQL
    #diretamente no banco de dados em Supabase, e usando
    #uma conexão direta a essa função.
    for votante in votantes_list:
        email_atual = votante['email']
        update_list.append({'email': email_atual, 'votou': False})
	
        _, _ = (conn.table('votantes')
				.upsert(update_list)
				.execute()
				)
