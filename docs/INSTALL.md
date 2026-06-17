# Guia de Instalação - SABE

## Pré-requisitos

### 1. Python 3.12+

Verifique a instalação:
```bash
python --version
```

### 2. PostgreSQL 15+

#### Windows
1. Baixe o instalador em https://www.postgresql.org/download/windows/
2. Execute o instalador e anote a senha do usuário `postgres`
3. Durante a instalação, certifique-se de instalar também o pgAdmin

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install postgresql postgresql-client
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### 3. Tesseract OCR

#### Windows
1. Baixe o instalador em https://github.com/UB-Mannheim/tesseract/wiki
2. Execute o instalador e adicione o Tesseract ao PATH do sistema
3. Instale o pacote de idioma português durante a instalação

#### Linux
```bash
sudo apt install tesseract-ocr tesseract-ocr-por
```

## Configuração do Banco de Dados

1. Acesse o PostgreSQL:
```bash
psql -U postgres
```

2. Crie o banco de dados:
```sql
CREATE DATABASE sabe_db;
CREATE DATABASE sabe_test_db;
\q
```

## Configuração do Projeto

```bash
# Clone ou copie os arquivos do projeto
cd sabe

# Crie o ambiente virtual
python -m venv .venv

# Ative o ambiente virtual
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Windows CMD:
.venv\Scripts\activate.bat
# Linux/macOS:
source .venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Configure o arquivo .env
cp .env.example .env
# Edite o .env com as credenciais do PostgreSQL
```

## Execução

```bash
# Execute as migrações
python manage.py migrate

# Carregue os dados de homologação
python manage.py seed_data

# Colete os arquivos estáticos
python manage.py collectstatic --noinput

# Inicie o servidor
python manage.py runserver
```

Acesse: http://localhost:8000

### Usuários da Seed

| Usuário    | Senha          | Nome            |
|------------|----------------|-----------------|
| auditor01  | auditor01@tce  | Carlos Silva    |
| auditor02  | auditor02@tce  | Ana Oliveira    |
| auditor03  | auditor03@tce  | Pedro Santos    |

## Execução dos Testes

```bash
# Executar todos os testes
pytest

# Executar com relatório de cobertura
pytest --cov=sabe --cov-report=html
open htmlcov/index.html
```
