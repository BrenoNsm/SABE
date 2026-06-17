# Fluxo de Trabalho - SABE

## Visão Geral

O **SABE** (Sistema de Auditoria Baseado em Evidências) gerencia auditorias desde a criação até a geração de relatórios. Abaixo está o fluxo completo de uso.

## 1. Autenticação

- Acesse `/accounts/login/` para fazer login
- Para criar novos usuários, acesse o admin em `/admin/` (usuário staff)

## 2. Auditorias (Módulo principal)

### Criar
- `/audit/create/` — formulário com número, exercício, responsável, objeto, etc.

### Listar
- `/audit/` — tabela com todas as auditorias, ações de editar/duplicar/excluir

### Detalhar
- `/audit/<pk>/` — visão geral com abas:
  - **Documentos**: upload e processamento
  - **Achados**: cadastro de evidências
  - **Fundamentação Legal**: vinculação de normas
  - **Relatórios**: geração DOCX/PDF

### Editar
- `/audit/<pk>/edit/`

### Fechar
- `/audit/<pk>/close/` — encerra a auditoria

### Duplicar
- `/audit/<pk>/duplicate/` — copia dados para nova auditoria

## 3. Documentos

### Upload
- `/documents/upload/<audit_id>/` — envio de PDFs, imagens, etc.

### Processamento OCR
- Na tela de detalhe do documento (`/documents/<pk>/`), clique em "Processar"
- O sistema extrai texto via OCR (idioma configurado em `OCR_LANGUAGE`)

### Visualizador de PDF
- `/documents/<pk>/viewer/` — visualização inline com seleção de texto para criar evidências

## 4. Achados e Evidências

### Criar achado
- Dentro da auditoria, seção "Achados", clique em "Adicionar Achado"
- Preencha: título, classificação, descrição, critério, condição, causa, efeito, recomendação

### Criar evidência
- No visualizador de PDF, selecione texto e clique em "Criar Evidência"
- Ou em `/findings/evidence/create/` manualmente

## 5. Fundamentação Legal

- `/legal/` — CRUD de normas jurídicas
- Dentro de cada achado, é possível vincular fundamentos legais

## 6. Relatórios

### Gerar
- Na tela de detalhe da auditoria, clique em "Gerar Relatório"
- Opções: **DOCX** (via python-docx) ou **PDF** (via WeasyPrint)

### Download/Exclusão
- Relatórios gerados ficam listados na auditoria para download ou exclusão

## 7. Pesquisa

- `/search/` — busca textual em todos os achados, documentos e auditorias

## 8. Logs de Auditoria

- `/logs/` — registro de todas as ações (login, upload, criação, etc.)

## 9. Admin

- `/admin/` — interface Django Admin para gerenciamento avançado de usuários, grupos e dados

---

## Resumo do Ciclo de Vida

```
Criar Auditoria
  → Upload de Documentos
    → Processar OCR
      → Identificar Achados
        → Criar Evidências (texto selecionado)
          → Vincular Fundamentação Legal
            → Gerar Relatório (DOCX/PDF)
              → Fechar Auditoria
```
