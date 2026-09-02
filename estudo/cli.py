"""Interface de linha de comando interativa."""
import sys

import pymysql

from . import db

CORES = {
    "pendente": "\033[90m",
    "estudando": "\033[93m",
    "revisar": "\033[91m",
    "dominado": "\033[92m",
}
RESET = "\033[0m"


def cor(status):
    return f"{CORES.get(status, '')}{status}{RESET}"


def perguntar(msg, obrigatorio=True, padrao=None):
    while True:
        sufixo = f" [{padrao}]" if padrao is not None else ""
        valor = input(f"{msg}{sufixo}: ").strip()
        if valor:
            return valor
        if padrao is not None:
            return padrao
        if not obrigatorio:
            return None
        print("  Campo obrigatorio.")


def perguntar_int(msg):
    while True:
        valor = input(f"{msg}: ").strip()
        if valor.isdigit():
            return int(valor)
        if valor == "":
            return None
        print("  Digite um numero.")


def escolher_status(padrao="pendente"):
    opcoes = " / ".join(f"{i+1}={s}" for i, s in enumerate(db.STATUS))
    while True:
        valor = input(f"Status ({opcoes}) [{padrao}]: ").strip()
        if valor == "":
            return padrao
        if valor.isdigit() and 1 <= int(valor) <= len(db.STATUS):
            return db.STATUS[int(valor) - 1]
        if valor in db.STATUS:
            return valor
        print("  Status invalido.")


def confirmar(msg):
    return input(f"{msg} (s/N): ").strip().lower() == "s"


# ---------- Telas ----------
def tela_temas():
    temas = db.listar_temas()
    print("\n=== TEMAS ===")
    if not temas:
        print("  (nenhum tema cadastrado)")
    for t in temas:
        print(f"  [{t['id']}] {t['nome']} ({t['total_topicos']} topicos) - {t['descricao'] or ''}")
    return temas


def novo_tema():
    nome = perguntar("Nome do tema")
    desc = perguntar("Descricao", obrigatorio=False)
    tid = db.criar_tema(nome, desc)
    print(f"  Tema criado com id {tid}.")


def editar_tema():
    tela_temas()
    tid = perguntar_int("Id do tema a editar")
    if tid is None:
        return
    atual = next((t for t in db.listar_temas() if t["id"] == tid), None)
    if not atual:
        print("  Tema nao encontrado.")
        return
    nome = perguntar("Nome", padrao=atual["nome"])
    desc = perguntar("Descricao", padrao=atual["descricao"] or "")
    db.atualizar_tema(tid, nome, desc)
    print("  Tema atualizado.")


def excluir_tema():
    tela_temas()
    tid = perguntar_int("Id do tema a excluir (apaga todos os topicos dele!)")
    if tid is not None and confirmar("Tem certeza?"):
        n = db.excluir_tema(tid)
        print("  Tema excluido." if n else "  Tema nao encontrado.")


def tela_topicos(tema_id=None, status=None):
    topicos = db.listar_topicos(tema_id, status)
    print("\n=== TOPICOS DE ESTUDO ===")
    if not topicos:
        print("  (nenhum topico)")
    for p in topicos:
        print(f"  [{p['id']}] {p['tema']:<12} {p['titulo']:<40} {cor(p['status'])}")
    return topicos


def listar_topicos_filtrado():
    print("\nFiltrar por: 1=tema  2=status  Enter=todos")
    op = input("> ").strip()
    if op == "1":
        tela_temas()
        tela_topicos(tema_id=perguntar_int("Id do tema"))
    elif op == "2":
        tela_topicos(status=escolher_status())
    else:
        tela_topicos()


def ver_topico():
    tela_topicos()
    pid = perguntar_int("Id do topico")
    if pid is None:
        return
    p = db.obter_topico(pid)
    if not p:
        print("  Topico nao encontrado.")
        return
    print(f"\n--- [{p['id']}] {p['titulo']} ---")
    print(f"Tema:       {p['tema']}")
    print(f"Status:     {cor(p['status'])}")
    print(f"Atualizado: {p['atualizado_em']}")
    print(f"Anotacoes:\n{p['anotacoes'] or '  (vazio)'}")
    revs = db.listar_revisoes(pid)
    if revs:
        print("Revisoes:")
        for r in revs:
            print(f"  - {r['revisado_em']}: {r['comentario'] or ''}")


def novo_topico():
    temas = tela_temas()
    if not temas:
        print("  Crie um tema primeiro.")
        return
    tema_id = perguntar_int("Id do tema")
    if tema_id is None:
        return
    titulo = perguntar("Titulo do topico")
    print("Anotacoes (linha vazia para terminar):")
    linhas = []
    while (linha := input("  ")) != "":
        linhas.append(linha)
    status = escolher_status()
    pid = db.criar_topico(tema_id, titulo, "\n".join(linhas) or None, status)
    print(f"  Topico criado com id {pid}.")


def editar_topico():
    tela_topicos()
    pid = perguntar_int("Id do topico a editar")
    if pid is None:
        return
    p = db.obter_topico(pid)
    if not p:
        print("  Topico nao encontrado.")
        return
    titulo = perguntar("Titulo", padrao=p["titulo"])
    print(f"Anotacoes atuais:\n{p['anotacoes'] or '  (vazio)'}")
    print("Novas anotacoes (linha vazia para manter as atuais):")
    linhas = []
    while (linha := input("  ")) != "":
        linhas.append(linha)
    anot = "\n".join(linhas) if linhas else None
    status = escolher_status(padrao=p["status"])
    db.atualizar_topico(pid, titulo=titulo, anotacoes=anot, status=status)
    print("  Topico atualizado.")


def excluir_topico():
    tela_topicos()
    pid = perguntar_int("Id do topico a excluir")
    if pid is not None and confirmar("Tem certeza?"):
        n = db.excluir_topico(pid)
        print("  Topico excluido." if n else "  Topico nao encontrado.")


def revisar_topico():
    tela_topicos()
    pid = perguntar_int("Id do topico revisado")
    if pid is None or not db.obter_topico(pid):
        print("  Topico nao encontrado.")
        return
    comentario = perguntar("Comentario da revisao", obrigatorio=False)
    status = escolher_status(padrao="revisar")
    db.registrar_revisao(pid, comentario, status)
    print("  Revisao registrada.")


def resumo():
    print("\n=== RESUMO ===")
    for r in db.resumo_por_status():
        print(f"  {cor(r['status']):<20} {r['total']}")


MENU = [
    ("Listar temas", tela_temas),
    ("Novo tema", novo_tema),
    ("Editar tema", editar_tema),
    ("Excluir tema", excluir_tema),
    ("Listar topicos (com filtro)", listar_topicos_filtrado),
    ("Ver topico (anotacoes e revisoes)", ver_topico),
    ("Novo topico", novo_topico),
    ("Editar topico", editar_topico),
    ("Excluir topico", excluir_topico),
    ("Registrar revisao", revisar_topico),
    ("Resumo por status", resumo),
]


def main():
    print("Auxilio de Estudo de Programacao - MariaDB")
    try:
        db.listar_temas()
    except pymysql.MySQLError as e:
        print(f"Erro ao conectar no MariaDB: {e}\nExecute ./setup_db.sh primeiro.")
        sys.exit(1)

    while True:
        print("\n" + "-" * 40)
        for i, (nome, _) in enumerate(MENU, 1):
            print(f" {i:>2}. {nome}")
        print("  0. Sair")
        op = input("> ").strip()
        if op == "0":
            print("Ate logo!")
            break
        if op.isdigit() and 1 <= int(op) <= len(MENU):
            try:
                MENU[int(op) - 1][1]()
            except pymysql.MySQLError as e:
                print(f"  Erro no banco: {e.args[1] if len(e.args) > 1 else e}")
        else:
            print("  Opcao invalida.")


if __name__ == "__main__":
    main()
