# Arquitetura do SABE

## Visão Geral

O SABE (Sistema de Auditoria Baseado em Evidências) é uma aplicação web monolitica construída com Django, projetada para operação on-premises no Tribunal de Contas do Estado de Roraima.

## Stack Tecnológica

```
Frontend: Django Templates + HTMX + Tailwind CSS + PDF.js
Backend:  Python 3.12+ / Django 5.0 LTS
Banco:    PostgreSQL 15+ (Full Text Search)
OCR:      OCRmyPDF + Tesseract + PyMuPDF + pdfplumber
Relatórios: python-docx + WeasyPrint
Testes:   Pytest + Factory Boy + Coverage
```

## Estrutura de Diretórios

```
sabe/
├── config/              # Configuração central
│   ├── settings/        # Settings por ambiente
│   ├── urls.py          # URLs raiz
│   └── wsgi.py          # WSGI
├── apps/
│   ├── core/            # Núcleo (middleware, signals, context)
│   ├── accounts/        # Autenticação (login/logout)
│   ├── audit/           # Gestão de auditorias
│   ├── documents/       # Documentos, OCR, extração
│   ├── findings/        # Achados e evidências
│   ├── legal/           # Fundamentação legal
│   ├── reports/         # Geração de relatórios
│   ├── search/          # Busca global
│   └── audit_log/       # Logs de auditoria
├── templates/           # Templates Django
├── static/              # Arquivos estáticos
├── media/               # Uploads
├── reports_output/      # Relatórios gerados
├── tests/               # Testes automatizados
└── management/          # Comandos personalizados
```

## Modelo de Dados

### Entidades Principais

```
Auditoria (Audit)
├── Documentos (Document) [1:N]
│   └── Evidências (Evidence) [1:N]
├── Achados (Finding) [1:N]
│   ├── Evidências (Evidence) [1:N]
│   └── Fundamentação Legal (FindingLegalFramework) [N:N]
│       └── Fundamentos Legais (LegalFramework)
└── Relatórios (Report) [1:N]

AuditLog: Log centralizado de auditoria
```

## Fluxo de Processamento de Documentos

1. Upload do PDF → Armazenamento + SHA-256
2. Tentativa de extração de texto com PyMuPDF
3. Se texto insuficiente → OCR com OCRmyPDF
4. Extração de texto do PDF  OCRizado
5. Indexação no PostgreSQL Full Text Search (search_vector)

## Fluxo de Relatórios

1. Coleta de dados da auditoria
2. Para DOCX: geração com python-docx (estrutura programática)
3. Para PDF: renderização HTML → WeasyPrint
4. Armazenamento do arquivo gerado

## Segurança

- Settings modulares por ambiente (dev/hml/prod)
- CSP configurado por ambiente
- Headers de segurança via middleware
- Proteção CSRF nativa do Django
- Cookies HttpOnly + SameSite Strict
- Upload com validação MIME
- Sanitização de entradas (ORM do Django)
- Logs de auditoria para todas as ações críticas

## Estratégia de Testes

- Testes unitários: models, services, utilitários
- Testes de integração: fluxos completos
- Testes funcionais: views e navegação
- Fixtures com Factory Boy
- Meta: 90%+ de cobertura

## Ambientes

| Ambiente   | Settings Module                     | DEBUG | Banco        |
|------------|-------------------------------------|-------|--------------|
| Dev        | config.settings.development         | True  | PostgreSQL   |
| Homologação| config.settings.homologation        | False | PostgreSQL   |
| Produção   | config.settings.production          | False | PostgreSQL   |
