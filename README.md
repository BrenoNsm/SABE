# SABE - Sistema de Auditoria Baseado em Evidências

![logo](https://drive.google.com/file/d/1CQr_v1SPwSG49IQODXhbdFFRDEMETW-b/view?usp=sharing)

Sistema corporativo destinado ao **Tribunal de Contas do Estado de Roraima (TCE-RR)** para gestão de auditorias, documentos, evidências, achados e produção de relatórios técnicos.

## Requisitos

- Python 3.12+
- PostgreSQL 15+
- Tesseract OCR
- Sistema operacional: Linux (recomendado), Windows ou macOS

## Instalação Rápida

```bash
# Clonar o repositório
git clone <repo-url> sabe
cd sabe

# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente virtual (Windows)
.venv\Scripts\Activate.ps1

# Ativar ambiente virtual (Linux/macOS)
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas credenciais do PostgreSQL

# Executar migrações
python manage.py migrate

# Carregar dados de homologação
python manage.py seed_data

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Iniciar servidor de desenvolvimento
python manage.py runserver
```

## Funcionalidades

- **Auditorias**: CRUD completo, duplicação, encerramento
- **Documentos**: Upload de PDF, OCR automático, extração de texto, hash SHA-256
- **Visualizador PDF**: Interface com PDF.js, zoom, busca textual, seleção de texto
- **Evidências**: Captura de trechos do PDF, hash, coordenadas, cadeia de custódia
- **Achados**: Classificação (Baixa, Média, Alta, Crítica), critério, causa, efeito
- **Fundamentação Legal**: CF, Leis, Decretos, Acórdãos, Súmulas, Jurisprudência
- **Relatórios**: Geração em DOCX e PDF com estrutura completa
- **Pesquisa**: Busca global com PostgreSQL Full Text Search
- **Logs**: Auditoria completa de todas as ações do sistema

## Tecnologias

- Python 3.12+ / Django 5.0 LTS
- PostgreSQL com Full Text Search
- HTMX + Tailwind CSS
- PDF.js para visualização
- OCRmyPDF + Tesseract para OCR
- PyMuPDF + pdfplumber para extração
- python-docx + WeasyPrint para relatórios

## Segurança

- CSRF, CSP, HSTS, XSS Protection
- HttpOnly Cookies, SameSite Strict
- Upload com validação MIME
- Sanitização de entradas
- Logs de auditoria

## Testes

```bash
# Executar testes com cobertura
pytest

# Ver cobertura em HTML
open htmlcov/index.html
```

Meta mínima: 90% de cobertura.
