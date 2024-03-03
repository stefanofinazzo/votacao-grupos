# Sistema de votação

Repositório para um sistema de votação simples em Streamlit para atividades estilo workshop/seminários, preparado para deploy rápido no Streamlit Cloud, com conexão persistente a um banco de dados em Supabase.

O objetivo é ter um aplicativo de deploy quase instantâneo e fácil manutenção, com ferramentas simples de controle e visualização dos resultados por um administrador, para uso em situações de jogos corporativos, de fácil customização e baixíssimo custo, com viabilidade para grupos pequenos de jogadores.

Da forma que é implementado, o custo é zero: o Streamlit Cloud e o Supabase disponibilizam soluções sem custo, com limites razoáveis (dados de mar/2024).

O gargalo na implementação são os recursos do Streamlit Cloud em seu free tier (em mar/2024, são atualmente este [limites](https://docs.streamlit.io/streamlit-community-cloud/manage-your-app)). Contudo, por ser um aplicativo muito simples, deve suportar algumas dezenas de usuários simultâneos, o que é adequado para o uso de caso típico.

Não é implementado nenhum sistema de hashing, autenticação ou autorização no app. O aplicativo, da forma que será disponibilizado, é viável apenas para casos em que não há preocupação com segurança dos dados ou resultados da votação.
