# -*- coding: utf-8 -*-

############# PACOTES ##################

import string
import secrets
from time import sleep

from typing import List, Dict, Union

import pandas as pd
import plotly.express as px

import streamlit as st

from st_supabase_connection import SupabaseConnection
from streamlit.delta_generator import DeltaGenerator

from . import db_utils


############### VARIÁVEIS GLOBAIS ########

ALPHABET = string.ascii_letters

############# FUNÇÕES AUXILIARES #########

def create_token(digits: int = 4) -> str:
    """
    Cria um token aleatório, com apenas letras do alfabeto maiúsculas.

    Parameters
    ----------
    digits : int, optional
        Número de caráteres no token. The default is 4.

    Returns
    -------
    token : str
        Token gerado.

    """
  
    token = ''.join(secrets.choice(ALPHABET) for i in range(digits)).upper()
     
    return token

def lista_perguntas_no_banco(perguntas_df: pd.DataFrame) -> List:
    """
    Obtém a lista de números das perguntas no banco de dados.

    Parameters
    ----------
    perguntas_df : pd.DataFrame
        Dataframe com as perguntas.

    Returns
    -------
    lista_perguntas: List
        Lista de números das perguntas.
    """

    if not perguntas_df.empty:
           lista_perguntas = perguntas_df['pergunta_id'].unique().tolist()
    else:
           lista_perguntas = None
            
    return lista_perguntas

def votos_bar_plot(votos_pergunta_df: pd.DataFrame) -> None:
    """
    Prepara o gráfico (em plotly) com os votos na pergunta por grupo.
    
    Parameters
    ----------
    votos_pergunta_df : pd.DataFrame
        Dataframe com os votos em uma pergunta.
    """

    fig = px.bar(votos_pergunta_df,
                   y='voto',
                   x='n_votos',
                   labels={
                     "voto": "Grupo",
                     "n_votos": "Votos",
                       },
                  )
      
    fig.update_layout(
                yaxis = dict(
                    tickmode = 'linear',
                    tick0 = 1,
                    dtick = 1,
                    autorange='reversed'
                ),
                xaxis = dict(
                    tickmode = 'linear',
                    tick0 = 0,
                    dtick = 1
                )
            )
      
    st.plotly_chart(fig, use_container_width=True)

def ranking_bar_plot(pontuacao_final_df: pd.DataFrame, 
                     container: Union[None, DeltaGenerator] = None) -> None:
    """
    Prepara o gráfico (em plotly) com a pontuação dos grupos.

    Parameters
    ----------
    pontuacao_final_df : pd.DataFrame
        Data frame com a pontuação final dos grupos.
    container : Union[None, DeltaGenerator], optional
        Container do streamlit, para permitir a execução fora de ordem
        na página. Se não for fornecido um container (gerado pela função
        st.container) o gráfico é gerado no ponto do código onde
        for inserida a função.
    """
    
    fig = px.bar(pontuacao_final_df,
                   y='grupo',
                   x='pontuacao',
                   labels={
                     "grupo": "Grupo",
                     "pontuacao": "Pontuação",
                       },
                  )

    fig.update_layout(
                yaxis = dict(
                    tickmode = 'linear',
                    tick0 = 1,
                    dtick = 1,
                    autorange='reversed'  
                ),
                xaxis = dict(
                    tickmode = 'linear',
                    tick0 = 0,
                    tickformat = ',d'
                )
            )
      
    if container:
        container.plotly_chart(fig, use_container_width=True)
    else:
        st.plotly_chart(fig, use_container_width=True)
      

def calcula_votos_para_pergunta(votos_df: pd.DataFrame, 
                                pergunta_id: int, 
                                numero_grupos: int) -> pd.DataFrame:
    """
    Filtra o dataframe de resultado da votação para filtrar apenas a uma única pergunta.
    
    O processamento inclui os grupos sem votos.

    Parameters
    ----------
    votos_df : pd.DataFrame
        Dataframe com os votos.
    pergunta_id : int
        Número da pergunta a ser filtrada.
    numero_grupos : int
        Número de grupos total.

    Returns
    -------
    votos_pergunta_df : TYPE
        Votos apenas da pergunta filtrada, com grupos sem votos inclusos.
    """
      
    filtro_pergunta = votos_df['pergunta_id'] == pergunta_id
    votos_pergunta_df = votos_df[filtro_pergunta]
    votos_pergunta_df = votos_pergunta_df.reset_index(drop=True)
    votos_pergunta_df = votos_pergunta_df[['voto', 'n_votos']]
    votos_pergunta_df = inclui_votos_zerados(votos_pergunta_df, numero_grupos) #para incluir os grupos sem votos

    return votos_pergunta_df

def inclui_votos_zerados(votos_pergunta_df: pd.DataFrame, total_grupos: int) -> pd.DataFrame:
    """
    Recebe um dataframe com o resultado da votação em apenas uma pergunta,
    e inclui os grupos sem votos (com número de votos = 0).

    Parameters
    ----------
    votos_pergunta_df : pd.DataFrame
        Dataframe com os resultados da votação para a pergunta filtrada.
    total_grupos : int
        Total de grupos na votação.

    Returns
    -------
    votos_perguntas_com_zeros_df : pd.DataFrame
        Votos apenas da pergunta filtrada, com grupos sem votos inclusos..
    """
      
    votos_perguntas_com_zeros_df = votos_pergunta_df.copy()
    
    for grupo_atual in range(1, total_grupos+1):
        filtro_grupo_atual = votos_pergunta_df['voto'] == str(grupo_atual)   #o grupo recebeu algum voto?
        votos_grupo_atual_df = votos_pergunta_df[filtro_grupo_atual]
        
        if votos_grupo_atual_df.empty:
            new_row = pd.DataFrame({'n_votos': [0], 
                                    'voto': [str(grupo_atual)],
                                   })
            votos_perguntas_com_zeros_df = pd.concat([votos_perguntas_com_zeros_df, new_row])

    return votos_perguntas_com_zeros_df
      
def calcula_pontuacao_pergunta(votos_pergunta_df: pd.DataFrame, total_grupos: int) -> pd.DataFrame:
    """
    Recebe o dataframe com o resultado da votação para uma pergunta, e calcula a pontuação
    por grupo naquela pergunta, de acordo com o número de votos recebidos.
    
    No app em tela, a pontuação segue o algoritmo (com N grupos ao todo):
        
        1 Lugar - N + 1 pontos
        2 Lugar - N pontos
        3 Lugar - N - 1 pontos
        ...
        N Lugar - 1 ponto
    
    Desempates são resolvidos atribuindo o mesmo ranking R para todos n grupos empatados,
    com a mesma pontuação. O grupo com menor número de votos subsequente
    recebe o ranking R + n + 1.
    
    Parameters
    ----------
    votos_pergunta_df : pd.DataFrame
        Dataframe com o resultado da votação para uma pergunta.
    total_grupos : int
        Total de grupos no jogo.

    Returns
    -------
    ranking_pergunta_df : TYPE
        Dataframe com os rankings e pontuações de cada grupo, na pergunta atual.
    """

    ranking_pergunta_df = votos_pergunta_df.copy()
    ranking_pergunta_df['ranking'] = ranking_pergunta_df['n_votos'].rank(method='min', ascending=False)
    ranking_pergunta_df['pontuacao'] = total_grupos + 1 - ranking_pergunta_df['ranking'] 
    ranking_pergunta_df = ranking_pergunta_df .sort_values(by='ranking', ascending=True)
    ranking_pergunta_df = ranking_pergunta_df.rename(columns={'voto': 'grupo'})

    return ranking_pergunta_df

def pontuacao_final(pontuacao_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula o dataframe com a pontuação final, agregando os resultados de pontuação por questão

    Parameters
    ----------
    pontuacao_df : pd.DataFrame
        Dataframe com os resultados e pontuação da votação por questão.

    Returns
    -------
    pontuacao_final_df : TYPE
        Dataframe com os resultados agregados.
    """

    pontuacao_final_df = (pontuacao_df
                          .groupby('grupo')
                          .agg({'pontuacao': 'sum'})
                          .reset_index()
                         )

    pontuacao_final_df['ranking'] = pontuacao_final_df['pontuacao'].rank(method='min', ascending=False)
    pontuacao_final_df = pontuacao_final_df.sort_values(by='pontuacao', ascending=False)
    
    return pontuacao_final_df
      
############# WIDGETS ##################

def widget_incluir_pergunta(conn: SupabaseConnection, 
                            app_config: Dict, 
                            perguntas_df: pd.DataFrame) -> None:
    """
    Widget para inclusão de perguntas no banco de dados.

    Parameters
    ----------
    conn : SupabaseConnection
        Conexão ao banco de dados.
    app_config : Dict
        Configuração do app.
    perguntas_df : pd.DataFrame
        Dataframe com os dados das perguntas.
    """
   
    with st.form("incluir_pergunta"):
       
        st.markdown("Inclusão de perguntas")
        
        if not perguntas_df.empty:
            lista_perguntas_atuais = lista_perguntas_no_banco(perguntas_df)
            lista_perguntas_total = list(range(1, app_config['numero_perguntas'] + 1))
            lista_perguntas_ausentes = [pergunta_id for pergunta_id in lista_perguntas_total if pergunta_id not in lista_perguntas_atuais]
        else:
            lista_perguntas_atuais = None
            lista_perguntas_ausentes = list(range(1, app_config['numero_perguntas']  + 1))
        
        if not app_config['votacao_ativa']:
            if (not lista_perguntas_atuais) or (len(lista_perguntas_atuais) < app_config['numero_perguntas']):
                n_pergunta = st.selectbox('Número da pergunta', lista_perguntas_ausentes)
                nome_pergunta = st.text_input('Nome da pergunta')
                submitted = st.form_submit_button("Cadastrar pergunta", type="primary", disabled=False)

            else:
                st.markdown('#### Todas perguntas já cadastradas!')
                submitted = st.form_submit_button("Cadastrar pergunta", type="primary", disabled=True)
             
        elif app_config['votacao_ativa']:
            st.info('Votação liberada. Inserção de perguntas possível apenas com votação interrompida')
            st.selectbox('Número da pergunta', lista_perguntas_ausentes, disabled=True)
            st.text_input('Nome da pergunta', disabled=True)
            submitted = st.form_submit_button("Cadastrar pergunta", type="primary", disabled=True)

        if submitted:
            db_utils.insert_pergunta(conn, n_pergunta, nome_pergunta)
            st.success('Pergunta incluída com sucesso!')
            sleep(1)
            st.rerun()
    

def widget_excluir_pergunta(conn: SupabaseConnection, 
                            app_config: Dict,
                            perguntas_df: pd.DataFrame) -> None:
    """
    Widget para realizar a exclusão de uma pergunta do banco de dados.

    Parameters
    ----------
    conn : SupabaseConnection
        Conexão ao banco de dados.
    app_config : Dict
        Configuração do aplicativo.
    perguntas_df : pd.DataFrame
        Dataframe com os dados das perguntas.
    """
      
    if not perguntas_df.empty:
       
        with st.form("excluir_pergunta"):
            st.write("Exclusão de pergunta")
            lista_perguntas_atuais = lista_perguntas_no_banco(perguntas_df)
            
            if not app_config['votacao_ativa']:
                n_pergunta = st.selectbox('Número da pergunta', lista_perguntas_atuais)
                submitted = st.form_submit_button("Excluir Pergunta", type="primary")
            elif app_config['votacao_ativa']:
                st.info('Votação liberada. Exclusão de perguntas possível apenas com votação interrompida')
                n_pergunta = st.selectbox('Número da pergunta', lista_perguntas_atuais, disabled=True)
                submitted = st.form_submit_button("Excluir Pergunta", type="primary", disabled=True)
                
            if submitted:
                db_utils.deletar_votos(conn, n_pergunta)
                db_utils.delete_pergunta(conn, n_pergunta)
                st.success('Pergunta excluída com sucesso!')
                sleep(1)
                st.rerun()
                        
    else:
        st.markdown('#### Sem perguntas cadastradas no momento!')
            
def widget_lista_perguntas(conn: SupabaseConnection) -> pd.DataFrame:
    """
    Widget que exibe a lista de perguntas no banco de dados

    Parameters
    ----------
    conn : SupabaseConnection
        Conexão ao banco de dados.
        
    Returns
    ---------
    perguntas_df: pd.DataFrame
    
    dataframe com os dados das perguntas.
    """
      
    perguntas_list = db_utils.get_list_table(conn, table='perguntas')
    perguntas_df = db_utils.list_para_df(perguntas_list)
       
    if not perguntas_df.empty:
        perguntas_df = perguntas_df.sort_values(by='pergunta_id')
        st.dataframe(perguntas_df,
                       hide_index=True,
                       use_container_width=True,
                       column_config={
                         "pergunta_id":  st.column_config.NumberColumn("Número"),
                         "pergunta_texto": st.column_config.TextColumn("Pergunta")
                     },
                    )
     
    else:
        st.markdown('#### Sem perguntas cadastradas no momento!')
        
    return perguntas_df
      
def widget_incluir_votante(conn: SupabaseConnection,
                           app_config: Dict) -> None:
    """
    Widget para inclusão de votantes no banco de dados.

    Parameters
    ----------
    conn : SupabaseConnection
        Conexão ao banco de dados.
    app_config : Dict
        Configurações do aplicativo.
    """
   
    with st.form("incluir_votante"):
        st.write("Inclusão de novos votantes")
        if not app_config['votacao_ativa']:
              nome = st.text_input('Nome')
              email = st.text_input('E-mail')
              grupo = st.slider('Grupo', 1, 1, app_config['numero_grupos'])
              token_manual = st.text_input('Token', 
                                               value=None,
                                               max_chars=4,
                                               placeholder='Token a inserir manualmente. Se mantido em branco, um token será gerado automaticamente.',
                                               )
              
              submitted = st.form_submit_button("Cadastrar ou alterar votante", type="primary")
              
        elif app_config['votacao_ativa']:
              st.info('Votação liberada. Inclusão de votantes possível apenas com votação interrompida')
              nome = st.text_input('Nome', disabled=True)
              email = st.text_input('E-mail', disabled=True)
              grupo = st.slider('Grupo', 1, 1, app_config['numero_grupos'], disabled=True)
              token_manual = st.text_input('Token', 
                                               value=None,
                                               max_chars=4,
                                               placeholder='Token a inserir manualmente. Se mantido em branco, um token será gerado automaticamente.',
                                               )
              
              submitted = st.form_submit_button("Cadastrar ou alterar votante", type="primary",disabled=True)
              
    
        if submitted:
              if token_manual == None or token_manual == '':
                  token = create_token(digits=4)
              else:
                  token = token_manual
              db_utils.insert_votante(conn, nome, email, grupo, token)
              st.success('Votante incluído com sucesso!')
              sleep(1)
              st.rerun()

def widget_excluir_votante(conn: SupabaseConnection,
                           app_config: Dict) -> None:
    """
    Widget para exclusão de um votante.

    Parameters
    ----------
    conn : SupabaseConnection
        Conexão ao banco de dados.
    app_config : Dict
        Configurações do aplicativo.
    """
   
    with st.form("excluir_votante"):
        st.write("Exclusão de votante")
        
        if not app_config['votacao_ativa']:
            email = st.text_input('E-mail')
            submitted = st.form_submit_button("Excluir votante", type="primary")
              
        elif app_config['votacao_ativa']:
            st.info('Votação liberada. Inclusão de votantes possível apenas com votação interrompida')
            email = st.text_input('E-mail', disabled=True)
            submitted = st.form_submit_button("Excluir votante", type="primary", disabled=True)
        
        if submitted:
            db_utils.delete_votante(conn, email)
            st.success('Votante excluído com sucesso!')
            sleep(1)
            st.rerun()    

def widget_lista_votantes(conn: SupabaseConnection) -> None:
    """
    Widget para exibir a lista atual de vontates.

    Parameters
    ----------
    conn : SupabaseConnection
        Conexão ao banco de dados.
    """
      
    votantes_list = db_utils.get_list_table(conn, table='votantes')
    
    if votantes_list:
          
        votantes_df = db_utils.list_para_df(votantes_list)
        votantes_df = votantes_df.sort_values(by='nome')
        st.dataframe(votantes_df,
                    hide_index=True,
                    use_container_width=True,
                    column_config={
                      "nome":  st.column_config.TextColumn("Nome"),
                      "email": st.column_config.TextColumn("Email"),
                      "grupo": st.column_config.TextColumn("Grupo"),
                      "token": st.column_config.TextColumn("Token"),
                      "votou": st.column_config.CheckboxColumn("Já votou?")   
                      },
                    )
    else:
        st.info('Sem votantes cadastrados!')
   
def widget_resultados(conn: SupabaseConnection,
                      app_config: Dict) -> None:
    """
    Widget para exibição dos resultados da votação.

    Parameters
    ----------
    conn : SupabaseConnection
        Conexão ao banco de dados.
    app_config : Dict
        Configuração do aplicativo.
    """
    
    st.markdown('## Resultados')

    if app_config['votacao_ativa']:
        st.markdown('### A votação está ativa! Encerre a votação para visualizar os resultados.')
    else:
        votos_list = db_utils.get_list_table(conn, table='contagem_votos')
        votos_df = db_utils.list_para_df(votos_list)
        numero_grupos = app_config['numero_grupos']
      
        if not votos_df.empty:
    
            st.markdown('### Resultado Final')
            
            #os resultados são exibidos na ordem: resultados finais, resultados por questão
            #contudo, os resultados finais são calculados apenas no final do widget
            #assim, para fazer a exibição fora de ordem, preparamos
            #os containers com os gráficos finais, para inclusão
            #da tabela e resultado no final do widget
            colunas_resultado_final = st.columns(2)
            with colunas_resultado_final[0]:
                  container_pontuacao_final = st.container(border=False)
  
            with colunas_resultado_final[1]:
                  container_pontuacao_final_fig = st.container(border=False)
            
            colunas_resultados = st.columns(2)
            
            perguntas_com_votos = votos_df['pergunta_id'].unique().tolist()
            pontuacao_df = pd.DataFrame()
  
            st.markdown('### Resultado por pergunta')
            for pergunta_id in perguntas_com_votos:
  
                st.markdown('##### Pergunta ' + str(pergunta_id))
                
                colunas_resultados = st.columns(2)
                
                votos_pergunta_df = calcula_votos_para_pergunta(votos_df, 
                                                                pergunta_id, 
                                                                numero_grupos)
                
                with colunas_resultados[0]:
                      ranking_pergunta_df = calcula_pontuacao_pergunta(votos_pergunta_df, numero_grupos)
                      st.dataframe(ranking_pergunta_df,
                                   hide_index=True,
                                   use_container_width=True,
                                   column_config={
                                          "ranking":  st.column_config.NumberColumn("Ranking"),
                                          "grupo": st.column_config.NumberColumn("Grupo"),
                                          "n_votos": st.column_config.TextColumn("Votos"),
                                          "pontuacao": st.column_config.TextColumn("Pontuação"),
                                          },
                                        )
                      
                with colunas_resultados[1]:
                      votos_bar_plot(votos_pergunta_df)
  
                if pontuacao_df.empty:
                      pontuacao_df = ranking_pergunta_df
                else:
                      pontuacao_df = pd.concat([pontuacao_df, ranking_pergunta_df])
  
            pontuacao_final_df = pontuacao_final(pontuacao_df)
                  
            #incluindo os resultados finais no container
            container_pontuacao_final.dataframe(pontuacao_final_df,
                  hide_index=True,
                  use_container_width=True,
                  column_order=['ranking', 'grupo', 'pontuacao'],
                  column_config={
                          "ranking":  st.column_config.NumberColumn("Ranking"),
                          "grupo": st.column_config.NumberColumn("Grupo"),
                          "pontuacao": st.column_config.TextColumn("Pontuação")
                          },
                        )
                  
            ranking_bar_plot(pontuacao_final_df, container_pontuacao_final_fig) 
                          
        else:
            st.markdown('#### Urna vazia!')
      
def display_metrics(app_config: Dict) -> None:
    """
    Mostra as métricas da configuração atual.

    Parameters
    ----------
    app_config : Dict
        Configuração do app.
    """

    metrics = st.columns(4)
    
    with metrics[0]:
        st.metric('Número de grupos', app_config['numero_grupos'])
    with metrics[1]:
        st.metric('Número de perguntas', app_config['numero_perguntas'])
    with metrics[2]:
        if app_config['votacao_ativa']:
            st.metric('Votação', 'ATIVA')
        else:
            st.metric('Votação', 'FECHADA')
    with metrics[3]:
        st.metric('Pergunta em votação', app_config['pergunta_liberada'])
                        
def widget_set_grupos(conn: SupabaseConnection,
                      app_config: Dict) -> None: 
    """
    Widget para configuração do número de grupos.

    Parameters
    ----------
    conn : SupabaseConnection
        DESCRIPTION.
    app_config : Dict
        DESCRIPTION.
    """
    
    st.markdown('#### Configuração de grupos')
    
    with st.form("numero_grupos"):

        st.warning('Atenção: os votantes com grupo já cadastradas acima do limite de grupos selecionado serão removidos!',  icon="⚠️")
        
        if not app_config['votacao_ativa']:
            numero_grupos = st.slider('Número de grupos', 1, 10, app_config['numero_grupos'])
            submitted_grupos = st.form_submit_button("Configurar", type="primary")
        else:
            numero_grupos = st.slider('Número de grupos', 1, 10, app_config['numero_grupos'], disabled=True)
            submitted_grupos = st.form_submit_button("Configurar", type="primary", disabled=True)
            
        if submitted_grupos:
            app_config['numero_grupos'] = numero_grupos
            db_utils.update_config(conn, app_config)
            db_utils.delete_votantes_acima_grupo_limite(conn, app_config) 
            st.success('Configuração atualizada com sucesso!')
            sleep(2)
            st.rerun()

def widget_set_perguntas(conn: SupabaseConnection, 
                         app_config: Dict) -> None:
    """
    Configura o número de perguntas na votação.

    Parameters
    ----------
    conn : SupabaseConnection
        Conexão ao banco de dados.
    app_config : Dict
        Configuração do app.
    """    

    st.markdown('#### Configuração de perguntas')
    
    with st.form("numero_perguntas"):
    
        st.warning('Atenção: as perguntas já cadastradas acima do limite serão eliminadas!',  icon="⚠️")
  
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
            sleep(2)
            st.rerun()

def widget_liberar_votacao(conn: SupabaseConnection,
                           app_config: Dict) -> None:
    """
    Widget para liberar a votação no aplicativo.

    Parameters
    ----------
    conn : SupabaseConnection
        Conexão ao banco de dados.
    app_config : Dict
        Configurações do aplicativo.
    """

    st.markdown('#### Liberar votação')
    
    perguntas_list = db_utils.get_list_table(conn, table='perguntas')
    perguntas_df = db_utils.list_para_df(perguntas_list)
    lista_perguntas_atuais = lista_perguntas_no_banco(perguntas_df) 
    
    if lista_perguntas_atuais:
        lista_perguntas_atuais.sort()
        
        with st.form("liberar_votacao"):
              
            if not app_config['votacao_ativa']:
                numero_pergunta_a_liberar = st.selectbox('Pergunta a liberar', 
                                                      lista_perguntas_atuais, 
                                                      disabled=False)
                submitted_liberar_votacao = st.form_submit_button("Liberar votação", type="primary")
            else:
                numero_pergunta_a_liberar = st.selectbox('Pergunta a liberar', 
                                                      lista_perguntas_atuais,
                                                      disabled=True)
                submitted_liberar_votacao = st.form_submit_button("Liberar votação", type="primary", disabled=True)
          
            if submitted_liberar_votacao:
                  
                pergunta_valida = True if (numero_pergunta_a_liberar in lista_perguntas_atuais) else False
                      
                if pergunta_valida:
                    app_config['votacao_ativa'] = True
                    app_config['pergunta_liberada'] = numero_pergunta_a_liberar
                    
                    db_utils.update_config(conn, app_config)
                    st.success('Votação liberada com sucesso!')
                    sleep(2)
                    st.rerun()
                      
                else:
                    st.error('Pergunta ' + str(numero_pergunta_a_liberar) + ' não cadastrada!')
                    
    if not lista_perguntas_atuais:
          st.error('Sem perguntas cadastradas!')

def widget_fechar_votacao(conn: SupabaseConnection,
                          app_config: Dict) -> None:
    """
    Widget para fechar a votação no aplicativo.

    Parameters
    ----------
    conn : SupabaseConnection
        Conexão ao banco de dados.
    app_config : Dict
        Configuração do aplicativo.
    """
    
    st.markdown('#### Fechar votação')
    
    with st.form("fechar_votacao"):

        if app_config['votacao_ativa']:
            st.info('Votação ativa')
            submitted_fechar_votacao = st.form_submit_button("Fechar votação", type="primary")
        else:
            st.info('Votação fechada')
            submitted_fechar_votacao = st.form_submit_button("Fechar votação", type="primary", disabled=True)
                        
        if submitted_fechar_votacao:
            app_config['votacao_ativa'] = False
            db_utils.update_config(conn, app_config)
            st.success('Votação fechada com sucesso!')
            sleep(2)
            st.rerun()

def widget_reinicializar_votantes(conn, app_config: Dict):
    """
    Widget para reinicializar o status dos votantes para "não votou".

    Parameters
    ----------
    conn : TYPE
        Conexão ao banco de dados.
    app_config : Dict
        Configuração do app.
    """

    st.markdown('#### Reinicializar votantes')

    with st.form("reinicializar_votantes"):
        st.info('Utilize esta opção para liberar o voto de todos votantes')
        
        if app_config['votacao_ativa']:
            submitted_reinicializar_votantes = st.form_submit_button("Reinicializar votantes", type="primary", disabled=True)
        else:
            submitted_reinicializar_votantes = st.form_submit_button("Reinicializar votantes", type="primary", disabled=False)
                        
        if submitted_reinicializar_votantes:
            db_utils.reinicia_votantes(conn)
            st.success('Votantes liberados para votação!')
            sleep(2)
            st.rerun()

def widget_limpar_urna(conn: SupabaseConnection,
                       app_config: Dict,
                       lista_perguntas_atuais: List) -> None:
    """
    Widget para limpar (remover) votos da urna, caso necessário.
    
    Permite tanto a limpeza de toda a urna (elimina todas perguntas),
    ou de uma pergunta específica.

    Parameters
    ----------
    conn : SupabaseConnection
        Conexão ao banco de dados.
    app_config : Dict
        Configuração do app.
    lista_perguntas_atuais : List
        Lista com os ids das perguntas atualmente no banco de dados.
    """
    
    st.markdown('#### Limpar urna')
    
    with st.container(border=True):
          
        st.warning('Esta função permite limpa os votos da urna (de uma pergunta específica ou de todas perguntas). Para ser utilizado se for necessário reiniciar o voto de uma pergunta ou de todas perguntas, por razões técnicas.')

        if lista_perguntas_atuais:
            lista_perguntas_atuais.append('Todas')
      
            if not app_config['votacao_ativa']:
                  
                pergunta_a_limpar = st.selectbox('Pergunta com votos a serem removidos', lista_perguntas_atuais)
                
                confirma_limpa_urna = st.button("Limpar urna", type="primary")

                if confirma_limpa_urna:

                    if pergunta_a_limpar != 'Todas':
                        db_utils.deletar_votos(conn, pergunta_id=pergunta_a_limpar)
                        st.success('Votos da pergunta ' + str(pergunta_a_limpar) + ' removidos com sucesso!')
                    else:
                        db_utils.deletar_votos(conn)
                        st.success('Todos votos da urna limpos com sucesso!')
                          
                    sleep(2)
                    st.rerun()
                      
                  
            else:
                st.button("Limpar urna", type="primary", disabled=True)
                st.selectbox('Pergunta com votos a serem removidos', lista_perguntas_atuais, disabled=True)
                  
        else:
            st.error('Sem perguntas cadastradas!')
                                            


def widget_exclusao_dados(conn: SupabaseConnection,
                          app_config: Dict) -> None:
    """
    Widget para excluir TODOS dados de votantes e/ou perguntas
    do banco de dados.

    Parameters
    ----------
    conn : SupabaseConnection
        Conexão ao banco de dados.
    app_config : Dict
        Configuração do aplicativo.
    """

    st.markdown('#### Excluir votantes e perguntas')

    st.error('Atenção, estas configurações EXCLUEM todos votantes ou perguntas. Excluir todas perguntas irá esvaziar a urna!')
    
    if not app_config['votacao_ativa']:
        
        confirma_exclusao = st.checkbox('Confirmar exclusão')
        colunas_botoes_exclusao = st.columns(2)
        
        with colunas_botoes_exclusao[0]:
            if st.button('Excluir perguntas'):
                if confirma_exclusao:
                    db_utils.delete_todas_perguntas(conn)
                    db_utils.deletar_votos(conn)
                    st.success('Todas perguntas excluídas com sucesso')
                    st.success('Todos votos excluídos com sucesso!')
                    sleep(2)
                    st.rerun()
                else:
                    st.error('Confirme a exclusão primeiro')
      
        with colunas_botoes_exclusao[1]: 
            if st.button('Excluir votantes'):
                if confirma_exclusao:
                    db_utils.delete_todos_votantes(conn)
                    st.success('Todos votantes excluídos com sucesso')
                    sleep(2)
                    st.rerun()
                else:
                    st.error('Confirme a exclusão primeiro')
    else:
        confirma_exclusao = st.checkbox('Confirmar exclusão', disabled=True)
        colunas_botoes_exclusao = st.columns(2)
        with colunas_botoes_exclusao[0]: 
            st.button('Excluir perguntas', disabled=True)
        with colunas_botoes_exclusao[1]:
            st.button('Excluir votantes', disabled=True)

def widget_status_config(conn: SupabaseConnection,
                         app_config: Dict, 
                         lista_perguntas_atuais: List) -> None:
    """
    Widget para monitoramento do status da configuração da votação

    Parameters
    ----------
    conn : SupabaseConnection
        Conexão ao banco de dados.
    app_config : Dict
        Configuração do app.
    lista_perguntas_atuais : List
        Lista com os ids das perguntas atualmente cadastradas.

    """
    st.markdown('#### Status da configuração')
    
    with st.container(border=True):
        if lista_perguntas_atuais:
            lista_perguntas_total = list(range(1, app_config['numero_perguntas'] + 1))
            lista_perguntas_ausentes = [pergunta_id for pergunta_id in lista_perguntas_total if pergunta_id not in lista_perguntas_atuais]
        else:
            lista_perguntas_ausentes = list(range(1, app_config['numero_perguntas'] + 1))

        if lista_perguntas_ausentes:
            string_perguntas_ausentes = [str(pergunta) for pergunta in lista_perguntas_ausentes]
            mensagem_perguntas_ausentes = '**:red[Perguntas não cadastradas: ' + ', '.join(string_perguntas_ausentes) + ']**'
            st.markdown(mensagem_perguntas_ausentes)
        else:
            st.success('Todas perguntas cadastradas!')
        
      
def widget_configurar_votacao(conn: SupabaseConnection,
                              app_config: Dict) -> None:
    """
    Widget que agrega todos recursos de configuração da votação.

    Parameters
    ----------
    conn : SupabaseConnection
        Conexão ao banco de dados.
    app_config : Dict
        Configuração do app.
    """

    perguntas_list = db_utils.get_list_table(conn, table='perguntas')
    perguntas_df = db_utils.list_para_df(perguntas_list)
    if not perguntas_df.empty:
        lista_perguntas_atuais = lista_perguntas_no_banco(perguntas_df)
        lista_perguntas_atuais.sort()
    else:
        lista_perguntas_atuais = None
    
    display_metrics(app_config)

    colunas_config = st.columns(2)

    with colunas_config[0]:
        widget_status_config(conn, app_config, lista_perguntas_atuais)
        widget_set_grupos(conn, app_config)
        widget_set_perguntas(conn, app_config)
        widget_exclusao_dados(conn, app_config)

    with colunas_config[1]:
        widget_liberar_votacao(conn, app_config)
        widget_fechar_votacao(conn, app_config)
        widget_reinicializar_votantes(conn, app_config)
        widget_limpar_urna(conn, app_config, lista_perguntas_atuais)
