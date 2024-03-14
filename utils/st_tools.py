import streamlit as st

def remove_bar():
  
    hide_decoration_bar_style = """
        <style>
            header {visibility: hidden;}
        </style>
        """
    
    st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)
