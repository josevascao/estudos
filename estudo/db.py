"""Conexao e operacoes CRUD no MariaDB."""
import os
from contextlib import contextmanager

import pymysql
from pymysql.cursors import DictCursor

CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "estudo"),
    "password": os.getenv("DB_PASS", "estudo123"),
    "database": os.getenv("DB_NAME", "estudo_prog"),
    "charset": "utf8mb4",
    "cursorclass": DictCursor,
}

STATUS = ("pendente", "estudando", "revisar", "dominado")


@contextmanager
def conectar():
    conn = pymysql.connect(**CONFIG)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _exec(sql, params=(), fetch=None):
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            if fetch == "one":
                return cur.fetchone()
            if fetch == "all":
                return cur.fetchall()
            return cur.lastrowid or cur.rowcount


# ---------- Temas ----------
def listar_temas():
    return _exec(
        """SELECT t.id, t.nome, t.descricao, COUNT(p.id) AS total_topicos
           FROM temas t LEFT JOIN topicos p ON p.tema_id = t.id
           GROUP BY t.id ORDER BY t.nome""",
        fetch="all",
    )


def criar_tema(nome, descricao=None):
    return _exec("INSERT INTO temas (nome, descricao) VALUES (%s, %s)", (nome, descricao))


def atualizar_tema(tema_id, nome, descricao):
    return _exec("UPDATE temas SET nome=%s, descricao=%s WHERE id=%s", (nome, descricao, tema_id))


def excluir_tema(tema_id):
    return _exec("DELETE FROM temas WHERE id=%s", (tema_id,))


# ---------- Topicos ----------
def listar_topicos(tema_id=None, status=None):
    sql = """SELECT p.id, p.titulo, p.status, p.anotacoes, p.atualizado_em,
                    t.nome AS tema
             FROM topicos p JOIN temas t ON t.id = p.tema_id WHERE 1=1"""
    params = []
    if tema_id:
        sql += " AND p.tema_id=%s"
        params.append(tema_id)
    if status:
        sql += " AND p.status=%s"
        params.append(status)
    sql += " ORDER BY t.nome, p.id"
    return _exec(sql, params, fetch="all")


def obter_topico(topico_id):
    return _exec(
        """SELECT p.*, t.nome AS tema FROM topicos p
           JOIN temas t ON t.id = p.tema_id WHERE p.id=%s""",
        (topico_id,),
        fetch="one",
    )


def criar_topico(tema_id, titulo, anotacoes=None, status="pendente"):
    return _exec(
        "INSERT INTO topicos (tema_id, titulo, anotacoes, status) VALUES (%s, %s, %s, %s)",
        (tema_id, titulo, anotacoes, status),
    )


def atualizar_topico(topico_id, titulo=None, anotacoes=None, status=None):
    campos, params = [], []
    for col, val in (("titulo", titulo), ("anotacoes", anotacoes), ("status", status)):
        if val is not None:
            campos.append(f"{col}=%s")
            params.append(val)
    if not campos:
        return 0
    params.append(topico_id)
    return _exec(f"UPDATE topicos SET {', '.join(campos)} WHERE id=%s", params)


def excluir_topico(topico_id):
    return _exec("DELETE FROM topicos WHERE id=%s", (topico_id,))


# ---------- Revisoes ----------
def registrar_revisao(topico_id, comentario=None, novo_status=None):
    with conectar() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO revisoes (topico_id, comentario) VALUES (%s, %s)",
                (topico_id, comentario),
            )
            if novo_status:
                cur.execute("UPDATE topicos SET status=%s WHERE id=%s", (novo_status, topico_id))


def listar_revisoes(topico_id):
    return _exec(
        "SELECT id, revisado_em, comentario FROM revisoes WHERE topico_id=%s ORDER BY revisado_em DESC",
        (topico_id,),
        fetch="all",
    )


def resumo_por_status():
    return _exec(
        "SELECT status, COUNT(*) AS total FROM topicos GROUP BY status ORDER BY status",
        fetch="all",
    )
