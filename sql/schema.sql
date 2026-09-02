CREATE DATABASE IF NOT EXISTS estudo_prog
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE estudo_prog;

CREATE TABLE IF NOT EXISTS temas (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  nome        VARCHAR(100) NOT NULL UNIQUE,
  descricao   TEXT,
  criado_em   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS topicos (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  tema_id       INT NOT NULL,
  titulo        VARCHAR(200) NOT NULL,
  anotacoes     TEXT,
  status        ENUM('pendente', 'estudando', 'revisar', 'dominado')
                NOT NULL DEFAULT 'pendente',
  criado_em     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT fk_topico_tema FOREIGN KEY (tema_id)
    REFERENCES temas(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS revisoes (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  topico_id   INT NOT NULL,
  revisado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  comentario  TEXT,
  CONSTRAINT fk_revisao_topico FOREIGN KEY (topico_id)
    REFERENCES topicos(id) ON DELETE CASCADE
);

INSERT IGNORE INTO temas (nome, descricao) VALUES
  ('Python', 'Linguagem Python e sua biblioteca padrao'),
  ('SQL', 'Bancos de dados relacionais e MariaDB'),
  ('Algoritmos', 'Estruturas de dados e algoritmos');
