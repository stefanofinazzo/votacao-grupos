CREATE TABLE votantes (
    email varchar(200) PRIMARY KEY,
    nome varchar(200),
    grupo integer,
    token varchar(80),
    votou boolean
);
