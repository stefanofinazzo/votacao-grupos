CREATE TABLE votantes (
    email varchar(200) PRIMARY KEY,
    nome varchar(200),
    grupo integer,
    token varchar(80),
    votou boolean
);

CREATE TABLE votos (
    voto_id SERIAL PRIMARY KEY,
    pergunta_id INTEGER,
    voto varchar(200),
    
    FOREIGN KEY(pergunta_id) REFERENCES perguntas(pergunta_id)
);

CREATE TABLE perguntas (
   pergunta_id INTEGER PRIMARY KEY,
   pergunta_texto text
);

CREATE TABLE config (
   onerow_id bool PRIMARY KEY DEFAULT true,
   numero_grupos INTEGER DEFAULT 7,
   numero_perguntas INTEGER DEFAULT 10,
   pergunta_liberada INTEGER DEFAULT 1,
   votacao_ativa boolean DEFAULT false
    
   CONSTRAINT onerow_uni CHECK (onerow_id)
);

-- View para contagem de votos --

CREATE VIEW contagem_votos as
  (SELECT COUNT(votos.voto) AS n_votos, 
    votos.voto as voto,
    votos.pergunta_id AS pergunta_id,
    perguntas.pergunta_texto AS pergunta_texto
  FROM votos
  INNER JOIN perguntas ON perguntas.pergunta_id = votos.pergunta_id
  GROUP BY votos.voto, votos.pergunta_id, perguntas.pergunta_texto
  ORDER BY pergunta_id
  );

-- Configuração padrão

INSERT INTO config VALUES (true, 7, 10, 1, false);
