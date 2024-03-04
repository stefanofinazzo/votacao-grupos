CREATE TABLE votantes (
    email varchar(200) PRIMARY KEY,
    nome varchar(200),
    grupo integer,
    token varchar(80),
    votou boolean
);

CREATE TABLE votos (
    voto_id SERIAL PRIMARY KEY
    voto varchar(200)
);
