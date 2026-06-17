# SABE - Sistema de Auditoria Baseado em Evidências

![logo]([https://drive.google.com/file/d/1CQr_v1SPwSG49IQODXhbdFFRDEMETW-b/view?usp=sharing](https://lh3.googleusercontent.com/rd-d/ALs6j_FmzsHq-_GgG3-F-KnXmHyTmWhr-pKSUFpQv53J3pRaLMS1t5YwPLsC0TjCKHPdZPQRW3HDD8gR3iC-bE3Og_sZwGq0IDcPrdBy2JxFGititBcJW5_8xlIlj5H8xWXVzs0vLSVZ1N07Zo3f6rDSooSaMxVYVbNepT7AMjHatiEHt_6shxPSYtM6Y2yt2DHVjSxMbE_TYTtsRTy67WKjc73AuA_oIl1aMULANNXfAIfG3RBcPXugVuX1_Ux-g3waY2wtjNDOZ5In-spClFMfK-70kN2z9bTuSzjagU5drjpjBVyaaFJYWlHOtG1J88nxLCIt4RkE_wllgjc9i0uEKYpPXN6_A7_o_0j8p6A9MDQznvv4ixwYWSFrZdM0mTYyH2KeInqWyAGHgjer5lZ5m1ZKiOKe2nUafO9HP2zTu9TebiBXcfHiLABYPNJBp5pMtHwAWpz-t9MKw9Hpw8OOIKF9NMlIuj3Wbg-obBGyiQ0TjWDDR4Jpx7Z0EG2hZBu7LVDHVlWpFbikTVFfpxzq_slpyaTEmmGn6dWgVfoFfKAHe8ECx1RjJI5HZutUV80FnqLs89Yia-d8orILDi864n8o9GskIZMEfH_Bq6d505UUgS7nLWTUGS4TT90ablTJCZ9e4d-fwU8N-06yagq4ufkWIFvkwAZ4LMGSrzZXHlZCBYtdudRFHfTD1QE3Ghlh4ZrlgtslJFYrn19eHpPiJImwDxO1-2HtZKgGJDoR-2Mc9UhjjYfDp-OJPKsu8-mlVNlldHJjno1JUzBKsHszra4ajHbZgk-DPWJ-B5LKGJDMXB4tKn9gTNdrmKHFjrZc6czYMk6QhrHIOMHofcQwhv6ge_2d8xM6cCCXTzJCnCZmOHJJ6tOyljwpk7DF_CFl8ojhADUlrs3KsEGdnEFOoQ7Nxt7Ntu-F8IytCAWfhUHSTQQiyE8iRZoEKIrOpsaVquu35U_w2OKQYo-fEEf26YiiIR-OhO9A4yy3pfpD2FEif5bvhspEI7Y4Z9aTHA4c3Oo5RxukHfH8SmSs2iJBlCYvqAkXc5_Veo_8IEvV4Ec_QynwPvfA5lI1wskxT8WFMBCGYZj_8KRr3DU8Y9ktzMOxmChGgQGCq5x6DfM5MYRUiHYkeKu79WxfZBUBP112K43CmRetfH8X27vHnUQxrWwtuDlSrkIxTWfT_SYJ0gX0V_-ILyDYKCcwcKZz4fKRZ_SgbGvwR5rIMVL5-KzFVpyQtklEftJXlkIvOBOPcw=w1919-h944?auditContext=forDisplay))

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
