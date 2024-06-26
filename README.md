# Sistema de votação

## Introdução

Repositório para um sistema de votação simples em Streamlit para atividades estilo workshop/seminários, preparado para deploy rápido no Streamlit Cloud, com conexão persistente a um banco de dados em Supabase.

O objetivo é ter um aplicativo de rápida implementação e baixa complexidade, deploy quase instantâneo, com ótima usabilidade, responsivo (para poder ser utilizado em celulares), fácil manutenção e customização, com ferramentas simples de controle e visualização dos resultados por um administrador, com baixíssimo custo, com viabilidade para grupos pequenos de jogadores.

O caso de uso típico são em situações de jogos corporativos, em que os participantes devem votar ou responder algumas questões pré-formuladas.

No caso de uso específico para que o aplicativo foi desenhado, a votação é para o seguinte jogo: um conjunto de $N$ grupos, com vários participantes em cada um, votam para eleger um grupo em cada rodada, em várias rodadas de perguntas, com a restrição de que cada participante não pode votar no próprio grupo em que pertence. Em cada rodada, os grupos são ranqueados em ordem de número de votos, sendo que o grupo com mais votos recebe $N+1$ pontos, o segundo grupo mais votado recebe $N$ pontos, e assim por diante, até o último grupo, que recebe 1 ponto. No fim de todas rodadas, ganha o grupo com mais pontos.

Da forma que é implementado, o custo é zero: o Streamlit Cloud e o Supabase disponibilizam soluções sem custo, com limites razoáveis (dados de mar/2024).

O gargalo na implementação são os recursos do Streamlit Cloud em seu free tier (em mar/2024, são estes os [limites de recursos do Streamlit Cloud](https://docs.streamlit.io/streamlit-community-cloud/manage-your-app)). Contudo, por ser um aplicativo muito simples, deve suportar algumas dezenas de usuários simultâneos, o que é adequado para o uso de caso projetado.

Não é implementado nenhum sistema de hashing, autenticação ou autorização no app. O aplicativo, da forma que será disponibilizado, é viável apenas para casos em que não há preocupação com segurança dos dados ou resultados da votação.

## Instruções de deploy

### Fork no github

Faça um fork deste projeto para sua conta do github. Mantenha o projeto público (necessário para disponibilização no Streamlit Cloud e acesso público dos votantes).

### Criando o banco de dados

Crie uma conta no [Supabase](https://supabase.com/) e abra um banco de dados pessoal.

Na pasta supabase_db do projeto o arquivo create_db.sql possui os comandos de PostgreSQL necessários para criar o schema de tabelas utilizado no back-end.

A maior parte das rotinas de acesso ao back-end estão concentradas em ./utils/db_utils.py, caso queira utilizar outro banco de dados ou utilizar seu ORM preferido.

### Streamlit Cloud

As instruções de deploy no Streamlit Cloud são descritas [aqui](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app).

### Secrets

Para deploy, é necessário fornecer o arquivo secrets.toml para o Streamlit (mais informações [aqui](https://docs.streamlit.io/library/advanced-features/secrets-management)).

No caso deste app, ele tem o formato:

#### ./.streamlit/secrets.toml
```TOML
[admin_config]
ADMIN_PASSWORD = "SENHA DO USUARIO ADMINISTRADOR DO APP"

[connections.supabase]
SUPABASE_URL = "URL DO DB DO SUPABASE"
SUPABASE_KEY = "CHAVE DO URL DO SUPABASE"
```

Para deploy no Streamlit Cloud, você deve atualizar os secrets conforme [as instruções do Streamlit](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management).

## Limitações

Limitações já identificadas:

1. Limite de usuários simultâneos. O banco de dados do Supabase, mesmo na versão gratuíta, é muito robusto e com limites bem generosos. Contudo, os [limites de recursos do Streamlit Cloud](https://docs.streamlit.io/streamlit-community-cloud/manage-your-app) são modestos, embora suficientes para grupos pequenos. O aplicativo foi testado com sucesso com ~40-50 usuários simultâneos, o que é mais que suficiente para o uso de caso planejado. Acredito que ele deve suportar um número moderado de usuários simultâneos ainda no Streamlit Cloud (talvez 100-200 usuários simultâneos sem afetar a experiência do usuário final). Caso seja necessário maior número de usuários, é necessário fazer o deploy do app do Streamlit em outra plataforma.

2. O módulo de administração é no mesmo webapp que o o módulo de votação. Caso necessário, isso é simples de ser resolvido: basta usar dois projetos, um apenas com o módulo de administração e o outro apenas com o módulo de votação, e criar dois apps no Streamlit Cloud.
