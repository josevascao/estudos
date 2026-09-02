#!/usr/bin/env bash
# Instala o MariaDB (se necessario), cria o banco, as tabelas e o usuario da aplicacao.
# Uso: ./setup_db.sh   (pede senha de sudo)
set -e
cd "$(dirname "$0")"

DB_USER="${DB_USER:-estudo}"
DB_PASS="${DB_PASS:-estudo123}"

if ! command -v mariadb >/dev/null 2>&1; then
  echo ">> Instalando MariaDB..."
  sudo apt-get update -q
  sudo apt-get install -y mariadb-server
fi

sudo systemctl enable --now mariadb

echo ">> Criando banco e tabelas..."
sudo mariadb < sql/schema.sql

echo ">> Criando usuario '$DB_USER'..."
sudo mariadb <<SQL
CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASS';
GRANT ALL PRIVILEGES ON estudo_prog.* TO '$DB_USER'@'localhost';
FLUSH PRIVILEGES;
SQL

echo ">> Instalando dependencias Python..."
pip3 install -q -r requirements.txt

echo ">> Pronto! Execute: python3 -m estudo"
