import streamlit as st

n_grupos = 7

#para testes, obviamente
DICT_VOTANTES = {'ABCDEF': 1, 
                  'BACBAC': 2,
                 }

if not em_votacao in st.session_state:
    st.session_state['em_votacao'] = False
    
st.title('Sistema de votação')

if not st.session_state['em_votacao']: 
    votante_atual = st.text_input('Coloque seu token de votação')
    
    if votante_atual in lista_votantes:
        st.session_state['em_votacao'] = False
        st.session_state['grupo_votante'] = DICT_VOTANTES[votante_atual]

else:
    #em votação

    grupos_a_votar = list(range(1,8))
    grupos_a_votar.remove(st.session_state['grupo_votante'])
    
    grupo_escolhido = st.selectbox('Escolha o seu grupo', grupos_a_votar)

    if grupo_escolhido:
        st.write('Você escolheu o grupo ' + str(grupo_escolhido))
    
