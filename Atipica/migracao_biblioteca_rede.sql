USE atipica;

CREATE TABLE IF NOT EXISTS biblioteca (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    titulo      VARCHAR(255) NOT NULL,
    tipo        VARCHAR(50)  NOT NULL,
    categoria   VARCHAR(20)  NOT NULL DEFAULT 'blue',
    ordem       INT NOT NULL DEFAULT 0
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS rede_apoio (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    nome          VARCHAR(255) NOT NULL,
    funcao        VARCHAR(255) NOT NULL,
    distancia_km  DECIMAL(4,1),
    ordem         INT NOT NULL DEFAULT 0
) ENGINE=InnoDB;

INSERT INTO biblioteca (titulo, tipo, categoria, ordem) VALUES
('Rotinas visuais: por onde começar', 'Cartilha', 'blue', 0),
('Entendendo crises sensoriais', 'Artigo', 'coral', 1),
('Comunicação alternativa em casa', 'Guia', 'green', 2),
('Preparando a escola para o Samuel', 'Artigo', 'yellow', 3);

INSERT INTO rede_apoio (nome, funcao, distancia_km, ordem) VALUES
('Dra. Camila Reis', 'Terapeuta Ocupacional', 1.2, 0),
('Grupo Passo a Passo', 'Grupo de apoio a famílias', 3.0, 1);