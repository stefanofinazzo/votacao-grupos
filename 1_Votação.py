from time import sleep

import streamlit as st

st.set_page_config(page_title='Sistema de Votação', 
                   page_icon=None, 
                   layout="wide", 
                   initial_sidebar_state="collapsed", 
                   menu_items=None)

n_grupos = 7

#para testes, obviamente
#necessário lógica para obter os tokens de um db qualquer aqui
#para os fins do aplicativo (para jogos corporativos simples, não
#é necessário implementar ferramentas de autenticação/autorização/etc.
DICT_VOTANTES = {'ABCDEF': 1, 
                  'BACBAC': 2,
                 }

if not 'em_votacao' in st.session_state:
    st.session_state['em_votacao'] = False
    
st.title('Sistema de votação')

if not st.session_state['em_votacao']: 
    votante_atual = st.text_input('Coloque seu token de votação')
    
    if votante_atual in list(DICT_VOTANTES.keys()):
        st.session_state['em_votacao'] = True
        st.session_state['grupo_votante'] = DICT_VOTANTES[votante_atual]
        st.success('Bem-vindo!')
        sleep(2)
        st.rerun()

    elif votante_atual is not None:
        st.error('Votante não localizado')

else:
    #em votação

    grupos_a_votar = list(range(1,8))
    grupos_a_votar.remove(st.session_state['grupo_votante'])
    
    grupo_escolhido = st.selectbox('Escolha o seu grupo', grupos_a_votar)
    
    if st.button('Votar'):
        st.write('Você escolheu o grupo ' + str(grupo_escolhido))
        #lógica para transferir o voto para db aqui
        #lógica para remover voto da lista aqui
    
