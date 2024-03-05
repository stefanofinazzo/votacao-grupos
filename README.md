# Sistema de votação

Repositório para um sistema de votação simples em Streamlit para atividades estilo workshop/seminários, preparado para deploy rápido no Streamlit Cloud, com conexão persistente a um banco de dados em Supabase.

O objetivo é ter um aplicativo de rápida implementação e baixa complexidade, deploy quase instantâneo, com ótima usabilidade, responsivo (para poder ser utilizado em celulares), fácil manutenção e customização, com ferramentas simples de controle e visualização dos resultados por um administrador, com baixíssimo custo, com viabilidade para grupos pequenos de jogadores.

O uso de caso típico são em situações de jogos corporativos, em que os participantes devem votar ou responder algumas questões pré-formuladas.

Da forma que é implementado, o custo é zero: o Streamlit Cloud e o Supabase disponibilizam soluções sem custo, com limites razoáveis (dados de mar/2024).

O gargalo na implementação são os recursos do Streamlit Cloud em seu free tier (em mar/2024, são estes os [limites de recursos do Streamlit Cloud](https://docs.streamlit.io/streamlit-community-cloud/manage-your-app)). Contudo, por ser um aplicativo muito simples, deve suportar algumas dezenas de usuários simultâneos, o que é adequado para o uso de caso típico.

Não é implementado nenhum sistema de hashing, autenticação ou autorização no app. O aplicativo, da forma que será disponibilizado, é viável apenas para casos em que não há preocupação com segurança dos dados ou resultados da votação.

## Secrets

Para deploy, é necessário fornecer o arquivo .secrets.toml.

No caso deste app, ele tem o formato:

```TOML
[admin_password]
ADMIN_PASSWORD = "SENHA DO USUARIO ADMINISTRADOR DO APP"

[connections.supabase]
SUPABASE_URL = "URL DO DB DO SUPABASE"
SUPABASE_KEY = "CHAVE DE ACESSO AO DB"
```

Para deploy no Streamlit Cloud, você deve atualizar os secrets conforme [as instruções do Streamlit](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management).
