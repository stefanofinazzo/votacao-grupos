from time import sleep

import streamlit as st

n_grupos = 7

#para testes, obviamente
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

    if grupo_escolhido:
        st.write('Você escolheu o grupo ' + str(grupo_escolhido))
    
