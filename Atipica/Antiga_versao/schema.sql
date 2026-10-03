-- ============================================================
-- ATÍPICA — Schema MySQL
-- Substitui o armazenamento em tpac_users.json
-- ============================================================

CREATE DATABASE IF NOT EXISTS atipica
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE atipica;

-- ── Usuários (era o "nó raiz" de cada perfil no JSON) ─────────
CREATE TABLE usuarios (
    email                    VARCHAR(255) PRIMARY KEY,
    nome                     VARCHAR(255) NOT NULL,
    senha                    VARCHAR(255) NOT NULL,
    tentativas_login         INT NOT NULL DEFAULT 0,
    bloqueado                BOOLEAN NOT NULL DEFAULT FALSE,
    codigo_desbloqueio       VARCHAR(20) NULL,
    estilo_instrucao         VARCHAR(20) NOT NULL DEFAULT 'direto',
    preferencias_sensoriais  VARCHAR(20) NOT NULL DEFAULT 'visual',
    tipo_alerta              VARCHAR(20) NOT NULL DEFAULT 'visual',
    lembretes_ativos         BOOLEAN NOT NULL DEFAULT TRUE,
    pontuacao                INT NOT NULL DEFAULT 0
) ENGINE=InnoDB;

-- ── Tarefas (cobre tarefas_diarias e tarefas_educacionais) ────
CREATE TABLE tarefas (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    usuario_email    VARCHAR(255) NOT NULL,
    tipo             ENUM('tarefas_diarias', 'tarefas_educacionais') NOT NULL,
    titulo           VARCHAR(255) NOT NULL,
    horario          VARCHAR(10)  NOT NULL DEFAULT '',
    data             VARCHAR(20)  NOT NULL DEFAULT '',
    concluida        BOOLEAN NOT NULL DEFAULT FALSE,
    tempo_limite_min INT NOT NULL DEFAULT 0,
    ordem            INT NOT NULL DEFAULT 0,
    FOREIGN KEY (usuario_email) REFERENCES usuarios(email) ON DELETE CASCADE,
    INDEX idx_tarefas_usuario (usuario_email, tipo)
) ENGINE=InnoDB;

-- ── Passos de cada tarefa (checklist da IA) ────────────────────
CREATE TABLE passos (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    tarefa_id   INT NOT NULL,
    texto       VARCHAR(255) NOT NULL,
    concluido   BOOLEAN NOT NULL DEFAULT FALSE,
    ordem       INT NOT NULL DEFAULT 0,
    FOREIGN KEY (tarefa_id) REFERENCES tarefas(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ── Estudos ─────────────────────────────────────────────────────
CREATE TABLE estudos (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    usuario_email   VARCHAR(255) NOT NULL,
    materia         VARCHAR(255) NOT NULL,
    objetivo        VARCHAR(255) NOT NULL DEFAULT '',
    tempo_estimado  INT NOT NULL,
    tempo_estudado  INT NOT NULL DEFAULT 0,
    prioridade      VARCHAR(20) NOT NULL,
    concluido       BOOLEAN NOT NULL DEFAULT FALSE,
    ordem           INT NOT NULL DEFAULT 0,
    FOREIGN KEY (usuario_email) REFERENCES usuarios(email) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ── Lembretes ───────────────────────────────────────────────────
CREATE TABLE lembretes (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    usuario_email   VARCHAR(255) NOT NULL,
    mensagem        VARCHAR(255) NOT NULL,
    horario         VARCHAR(10) NOT NULL DEFAULT '',
    tipo_alerta     VARCHAR(20) NOT NULL,
    ativo           BOOLEAN NOT NULL DEFAULT TRUE,
    ordem           INT NOT NULL DEFAULT 0,
    FOREIGN KEY (usuario_email) REFERENCES usuarios(email) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ── Histórico ───────────────────────────────────────────────────
CREATE TABLE historico (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    usuario_email   VARCHAR(255) NOT NULL,
    atividade       VARCHAR(255) NOT NULL,
    categoria       VARCHAR(50) NOT NULL,
    data            VARCHAR(20) NOT NULL,
    hora            VARCHAR(10) NOT NULL,
    status          VARCHAR(20) NOT NULL,
    ordem           INT NOT NULL DEFAULT 0,
    FOREIGN KEY (usuario_email) REFERENCES usuarios(email) ON DELETE CASCADE
) ENGINE=InnoDB;
