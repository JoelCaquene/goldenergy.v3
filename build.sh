#!/usr/bin/env bash
# Encerrar o script se houver erro
set -o errexit

# Instalar as dependências
pip install -r requirements.txt

# Coletar arquivos estáticos e migrar o banco
python manage.py collectstatic --no-input
python manage.py migrate
