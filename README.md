# Auxilio de Estudo de Programacao

CLI em Python + MariaDB para organizar temas, topicos de estudo, anotacoes e revisoes.

## Instalacao (Linux Mint / Ubuntu)

```bash
./setup_db.sh        # instala MariaDB, cria banco `estudo_prog`, tabelas e usuario `estudo`
python3 -m estudo    # abre o menu interativo
```

Credenciais padrao: usuario `estudo`, senha `estudo123` (altere via variaveis
`DB_USER`, `DB_PASS`, `DB_HOST`, `DB_NAME` antes de rodar o setup e a CLI).

## Estrutura

- `sql/schema.sql` – tabelas `temas`, `topicos` (anotacoes + status) e `revisoes`
- `estudo/db.py`   – conexao (PyMySQL) e funcoes CRUD
- `estudo/cli.py`  – menu interativo

Status possiveis: `pendente`, `estudando`, `revisar`, `dominado`.
