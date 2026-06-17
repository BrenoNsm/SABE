# Guia de Deploy - SABE

## Ambiente de Produção

Este guia descreve o processo de implantação do SABE em ambiente de produção on-premises.

## Pré-requisitos de Produção

- Servidor Linux (Ubuntu 22.04 LTS ou superior recomendado)
- Python 3.12+
- PostgreSQL 15+
- Nginx (como proxy reverso)
- Tesseract OCR com idioma português
- Supervisor (para gerenciamento de processos)

## Configuração do Servidor

### 1. Instalar Dependências do Sistema

```bash
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev
sudo apt install -y postgresql postgresql-client
sudo apt install -y nginx supervisor
sudo apt install -y tesseract-ocr tesseract-ocr-por
sudo apt install -y libpango-1.0-0 libpangoft2-1.0-0 libpangocairo-1.0-0
```

### 2. Criar Usuário do Sistema

```bash
sudo useradd -m -s /bin/bash sabe
sudo usermod -aG www-data sabe
```

### 3. Configurar PostgreSQL

```bash
sudo -u postgres psql -c "CREATE USER sabe_user WITH PASSWORD 'senha_segura';"
sudo -u postgres psql -c "CREATE DATABASE sabe_db OWNER sabe_user;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE sabe_db TO sabe_user;"
```

### 4. Instalar a Aplicação

```bash
sudo mkdir -p /opt/sabe
sudo chown sabe:sabe /opt/sabe
sudo -u sabe git clone <repo-url> /opt/sabe
cd /opt/sabe
sudo -u sabe python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 5. Configurar Ambiente

```bash
sudo -u sabe cp .env.example .env
# Editar .env para produção:
# DEBUG=False
# SECRET_KEY=<gerar chave segura>
# ALLOWED_HOSTS=sabe.tce.rr.gov.br,localhost
# DB_PASSWORD=<senha configurada>
# DJANGO_SETTINGS_MODULE=config.settings.production
```

### 6. Configurar Nginx

```nginx
# /etc/nginx/sites-available/sabe
server {
    listen 80;
    server_name sabe.tce.rr.gov.br;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name sabe.tce.rr.gov.br;

    ssl_certificate /etc/ssl/certs/tce-rr.crt;
    ssl_certificate_key /etc/ssl/private/tce-rr.key;

    client_max_body_size 50M;

    location /static/ {
        alias /opt/sabe/staticfiles/;
    }

    location /media/ {
        alias /opt/sabe/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 7. Configurar Supervisor

```ini
[program:sabe]
command=/opt/sabe/.venv/bin/gunicorn sabe.config.wsgi:application -w 4 -b 127.0.0.1:8000
directory=/opt/sabe
user=sabe
autostart=true
autorestart=true
stderr_logfile=/var/log/sabe/err.log
stdout_logfile=/var/log/sabe/out.log
environment=DJANGO_SETTINGS_MODULE="sabe.config.settings.production"
```

### 8. Finalizar

```bash
# Coletar estáticos
cd /opt/sabe
source .venv/bin/activate
python manage.py collectstatic --noinput

# Migrar
python manage.py migrate

# Iniciar serviços
sudo systemctl enable supervisor
sudo systemctl restart supervisor
sudo systemctl enable nginx
sudo systemctl restart nginx
```

## Manutenção

### Backups

```bash
# Backup do banco
pg_dump -U sabe_user sabe_db > /backup/sabe_$(date +%Y%m%d).sql

# Backup dos arquivos
tar -czf /backup/sabe_media_$(date +%Y%m%d).tar.gz /opt/sabe/media/
```

### Logs

```bash
# Logs da aplicação
tail -f /var/log/sabe/out.log
tail -f /var/log/sabe/err.log

# Logs do Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Atualização

```bash
cd /opt/sabe
git pull
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo supervisorctl restart sabe
```
