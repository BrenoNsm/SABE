import os
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.conf import settings
from django.db import transaction

from sabe.apps.audit.models import Audit
from sabe.apps.documents.models import Document
from sabe.apps.findings.models import Finding, Evidence
from sabe.apps.legal.models import LegalFramework, FindingLegalFramework
from sabe.apps.audit_log.models import AuditLog


class Command(BaseCommand):
    help = 'Cria dados de homologação para o SABE'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando seed de dados...')

        self._create_users()
        self._create_legal_frameworks()
        self._create_audits()
        self._create_documents()
        self._create_findings_and_evidences()
        self._link_legal_frameworks()

        self.stdout.write(self.style.SUCCESS('Seed concluída com sucesso!'))

    def _create_users(self):
        users_data = [
            {'username': 'auditor01', 'password': 'auditor01@tce', 'first_name': 'Carlos', 'last_name': 'Silva'},
            {'username': 'auditor02', 'password': 'auditor02@tce', 'first_name': 'Ana', 'last_name': 'Oliveira'},
            {'username': 'auditor03', 'password': 'auditor03@tce', 'first_name': 'Pedro', 'last_name': 'Santos'},
        ]
        created = 0
        for data in users_data:
            if not User.objects.filter(username=data['username']).exists():
                user = User.objects.create_user(
                    username=data['username'],
                    password=data['password'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                )
                user.save()
                created += 1
                self.stdout.write(f'  Usuário criado: {data["username"]}')
            else:
                self.stdout.write(f'  Usuário já existe: {data["username"]}')
        self.stdout.write(f'  Total de usuários criados: {created}')

    def _create_legal_frameworks(self):
        frameworks = [
            {'tipo': 'CF', 'numero': 'CF/1988', 'ementa': 'Constituição da República Federativa do Brasil de 1988', 'texto': 'Constituição da República Federativa do Brasil de 1988. Art. 70 a 75 - Fiscalização contábil, financeira e orçamentária.'},
            {'tipo': 'lei', 'numero': '14.133/2021', 'ementa': 'Lei de Licitações e Contratos Administrativos', 'texto': 'Lei nº 14.133, de 1º de abril de 2021. Lei de Licitações e Contratos Administrativos.'},
            {'tipo': 'lei', 'numero': 'LC 101/2000', 'ementa': 'Lei de Responsabilidade Fiscal', 'texto': 'Lei Complementar nº 101, de 4 de maio de 2000. Estabelece normas de finanças públicas voltadas para a responsabilidade na gestão fiscal.'},
            {'tipo': 'lei', 'numero': '8.429/1992', 'ementa': 'Lei de Improbidade Administrativa', 'texto': 'Lei nº 8.429, de 2 de junho de 1992. Dispõe sobre as sanções aplicáveis em virtude da prática de atos de improbidade administrativa.'},
            {'tipo': 'lei', 'numero': '4.320/1964', 'ementa': 'Normas Gerais de Direito Financeiro', 'texto': 'Lei nº 4.320, de 17 de março de 1964. Estatui Normas Gerais de Direito Financeiro para elaboração e controle dos orçamentos e balanços da União, dos Estados, dos Municípios e do Distrito Federal.'},
            {'tipo': 'resolucao', 'numero': '001/2020-TCE-RR', 'ementa': 'Regimento Interno do Tribunal de Contas do Estado de Roraima', 'texto': 'Resolução nº 001/2020. Aprova o Regimento Interno do Tribunal de Contas do Estado de Roraima.'},
            {'tipo': 'in', 'numero': '001/2021-TCE-RR', 'ementa': 'Instrução Normativa sobre fiscalização de obras públicas', 'texto': 'Instrução Normativa nº 001/2021. Estabelece procedimentos para fiscalização de obras públicas no âmbito do TCE-RR.'},
            {'tipo': 'acordao', 'numero': '123/2022-TCE-RR', 'ementa': 'Acórdão sobre prestação de contas de recursos da saúde', 'texto': 'Acórdão nº 123/2022-TCE-RR. Julga irregular a prestação de contas de recursos da saúde.'},
        ]
        created = 0
        for data in frameworks:
            obj, is_new = LegalFramework.objects.get_or_create(
                tipo=data['tipo'],
                numero=data['numero'],
                defaults={'ementa': data['ementa'], 'texto': data['texto']}
            )
            if is_new:
                created += 1
                self.stdout.write(f'  Fundamentação criada: {obj}')
            else:
                self.stdout.write(f'  Fundamentação já existe: {obj}')
        self.stdout.write(f'  Total de fundamentações criadas: {created}')

    def _create_audits(self):
        if not User.objects.exists():
            self.stdout.write(self.style.WARNING('  Nenhum usuário disponível. Pulando criação de auditorias.'))
            return

        auditor01 = User.objects.get(username='auditor01')
        auditor02 = User.objects.get(username='auditor02')

        audits_data = [
            {
                'numero': '001/2026',
                'exercicio': 2026,
                'processo': '001.001/2026',
                'unidade_jurisdicionada': 'Prefeitura Municipal de Boa Vista',
                'responsavel': 'Prefeito Municipal',
                'objeto': 'Auditoria de conformidade na execução de obras públicas de pavimentação asfáltica no município de Boa Vista, exercício 2025.',
                'data_inicio': date(2026, 1, 15),
                'data_encerramento': date(2026, 4, 30),
                'observacoes': 'Auditoria realizada com base na IN 001/2021-TCE-RR.',
                'created_by': auditor01,
            },
            {
                'numero': '002/2026',
                'exercicio': 2026,
                'processo': '002.001/2026',
                'unidade_jurisdicionada': 'Secretaria Estadual de Saúde',
                'responsavel': 'Secretário Estadual de Saúde',
                'objeto': 'Auditoria operacional na gestão dos contratos de fornecimento de medicamentos da Secretaria Estadual de Saúde.',
                'data_inicio': date(2026, 2, 1),
                'data_encerramento': date(2026, 5, 15),
                'observacoes': '',
                'created_by': auditor02,
            },
            {
                'numero': '003/2026',
                'exercicio': 2026,
                'processo': '003.001/2026',
                'unidade_jurisdicionada': 'Câmara Municipal de Boa Vista',
                'responsavel': 'Presidente da Câmara',
                'objeto': 'Auditoria de regularidade na gestão de diárias e passagens da Câmara Municipal de Boa Vista.',
                'data_inicio': date(2026, 3, 1),
                'data_encerramento': None,
                'observacoes': 'Auditoria em andamento.',
                'created_by': auditor01,
            },
        ]

        created = 0
        for data in audits_data:
            if not Audit.objects.filter(numero=data['numero']).exists():
                audit = Audit.objects.create(**data)
                created += 1
                self.stdout.write(f'  Auditoria criada: {audit}')
            else:
                self.stdout.write(f'  Auditoria já existe: {data["numero"]}')
        self.stdout.write(f'  Total de auditorias criadas: {created}')

    def _create_documents(self):
        if not Audit.objects.exists():
            return

        auditor01 = User.objects.get(username='auditor01')
        audit_obras = Audit.objects.get(numero='001/2026')

        # Criar um PDF de exemplo mínimo
        pdf_content = self._generate_sample_pdf('Relatório de Execução de Obras - Janeiro/2026')
        doc = Document.objects.create(
            audit=audit_obras,
            filename='relatorio_obras_jan2026.pdf',
            original_filename='relatorio_obras_jan2026.pdf',
            file_size=len(pdf_content),
            mime_type='application/pdf',
            sha256_hash='a"*"placeholder"*"hash_001',
            page_count=1,
            ocr_status='completed',
            extracted_text=(
                'RELATÓRIO DE EXECUÇÃO DE OBRAS - JANEIRO/2026\n\n'
                'Prefeitura Municipal de Boa Vista\n'
                'Secretaria Municipal de Infraestrutura\n\n'
                'Obra: Pavimentação Asfáltica da Avenida Principal\n'
                'Contrato: 045/2025\n'
                'Empresa: Construtora Roraima Ltda\n'
                'Valor: R$ 2.500.000,00\n\n'
                'Medição do mês de janeiro de 2026:\n'
                '- Serviço de terraplanagem: 85% concluído\n'
                '- Serviço de drenagem: 60% concluído\n'
                '- Pavimentação: 30% concluído\n\n'
                'Prazo contratual: 12 meses\n'
                'Início: 01/01/2026\n'
                'Término previsto: 31/12/2026\n\n'
                'Responsável técnico: Eng. Roberto Almeida - CREA 12345\n'
                'Fiscal do contrato: João Batista - Matrícula 6789'
            ),
            uploaded_by=auditor01,
        )
        self.stdout.write(f'  Documento criado: {doc.original_filename}')
        self.stdout.write(f'  Total de documentos criados: 1')

        # Salva o PDF de exemplo no disco
        media_dir = settings.MEDIA_ROOT / 'documents' / '2026' / '06'
        os.makedirs(media_dir, exist_ok=True)
        filepath = os.path.join(media_dir, 'relatorio_obras_jan2026.pdf')
        with open(filepath, 'wb') as f:
            f.write(pdf_content)
        doc.file.name = f'documents/2026/06/relatorio_obras_jan2026.pdf'
        doc.save(update_fields=['file'])

    def _create_findings_and_evidences(self):
        if not Audit.objects.exists() or not Document.objects.exists():
            return

        auditor01 = User.objects.get(username='auditor01')
        audit_obras = Audit.objects.get(numero='001/2026')
        doc = Document.objects.filter(audit=audit_obras).first()
        audit_saude = Audit.objects.get(numero='002/2026')

        findings_data = [
            {
                'audit': audit_obras,
                'title': 'Atraso na execução do cronograma físico',
                'description': 'Foi constatado que a execução física da obra de pavimentação asfáltica apresenta atraso de 15% em relação ao cronograma previsto no contrato 045/2025. A medição de janeiro indica apenas 30% de pavimentação concluída quando o previsto era 45%.',
                'criterio': 'Art. 66 da Lei 14.133/2021 - O contrato deve ser executado fielmente pelas partes.',
                'condicao': 'A execução física encontra-se em desconformidade com o cronograma contratual.',
                'causa': 'Deficiência no planejamento da contratada e falta de fiscalização efetiva.',
                'efeito': 'Possível comprometimento do prazo final de conclusão e majoração de custos.',
                'recomendacao': 'Notificar a contratada para apresentar novo cronograma recuperativo e intensificar a fiscalização.',
                'classificacao': 'high',
                'created_by': auditor01,
            },
            {
                'audit': audit_obras,
                'title': 'Ausência de Anotação de Responsabilidade Técnica',
                'description': 'Não foi localizada a Anotação de Responsabilidade Técnica (ART) do responsável pela execução da obra, conforme exige a Lei 6.496/1977.',
                'criterio': 'Art. 1º da Lei 6.496/1977 - Todo contrato de execução de obra deve ter ART.',
                'condicao': 'ART do responsável técnico não apresentada.',
                'causa': 'Desorganização documental da contratada.',
                'efeito': 'Irregularidade na documentação técnica da obra.',
                'recomendacao': 'Solicitar a regularização da ART no prazo de 15 dias.',
                'classificacao': 'medium',
                'created_by': auditor01,
            },
            {
                'audit': audit_saude,
                'title': 'Fragilidade no controle de estoque de medicamentos',
                'description': 'Foram identificadas inconsistências no controle de estoque de medicamentos de alto custo, com divergências entre o registro no sistema e o inventário físico.',
                'criterio': 'Art. 94 da Lei 4.320/1964 - O controle da execução orçamentária compreenderá o registro dos atos de gestão.',
                'condicao': 'Divergência entre estoque registrado e estoque físico.',
                'causa': 'Falta de procedimentos padronizados de inventário e controle.',
                'efeito': 'Risco de desabastecimento e possível dano ao erário.',
                'recomendacao': 'Implementar controle periódico de inventário e treinar os servidores responsáveis.',
                'classificacao': 'critical',
                'created_by': auditor01,
            },
        ]

        for data in findings_data:
            finding = Finding.objects.create(**data)
            self.stdout.write(f'  Achado criado: {finding.title}')

            if doc and finding.audit == audit_obras:
                evidence = Evidence.objects.create(
                    document=doc,
                    finding=finding,
                    page_number=1,
                    captured_text=f'Medição do mês de janeiro de 2026: Serviço de pavimentação: 30% concluído. Prazo contratual: 12 meses. Relacionado ao achado: {finding.title}',
                    coordinates={'x': 50, 'y': 200, 'width': 500, 'height': 100, 'page': 1},
                    hash='placeholder_hash_evidence_001',
                    created_by=auditor01,
                )
                self.stdout.write(f'    Evidência criada para: {finding.title}')

    def _link_legal_frameworks(self):
        if not Finding.objects.exists() or not LegalFramework.objects.exists():
            return

        lei_licitacoes = LegalFramework.objects.get(numero='14.133/2021')
        lei_rf = LegalFramework.objects.get(numero='LC 101/2000')
        lei_improbidade = LegalFramework.objects.get(numero='8.429/1992')
        lei_financas = LegalFramework.objects.get(numero='4.320/1964')

        finding_atraso = Finding.objects.filter(title__icontains='Atraso').first()
        finding_controle = Finding.objects.filter(title__icontains='Fragilidade').first()
        finding_art = Finding.objects.filter(title__icontains='Responsabilidade Técnica').first()

        links = [
            (finding_atraso, lei_licitacoes),
            (finding_art, lei_licitacoes),
            (finding_controle, lei_financas),
            (finding_controle, lei_rf),
            (finding_atraso, lei_improbidade),
        ]

        for finding, framework in links:
            if finding and framework:
                obj, created = FindingLegalFramework.objects.get_or_create(
                    finding=finding,
                    legal_framework=framework,
                )
                if created:
                    self.stdout.write(f'  Vinculação criada: {finding.title} -> {framework}')

    def _generate_sample_pdf(self, title):
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4
            from io import BytesIO

            buffer = BytesIO()
            p = canvas.Canvas(buffer, pagesize=A4)
            p.setTitle(title)
            p.drawString(50, 750, title)
            p.drawString(50, 700, 'Prefeitura Municipal de Boa Vista')
            p.drawString(50, 680, 'RELATÓRIO DE EXECUÇÃO DE OBRAS')
            p.drawString(50, 650, 'Obra: Pavimentação Asfáltica da Avenida Principal')
            p.drawString(50, 630, 'Contrato: 045/2025')
            p.drawString(50, 610, 'Empresa: Construtora Roraima Ltda')
            p.drawString(50, 590, 'Valor: R$ 2.500.000,00')
            p.drawString(50, 560, 'Medição do mês de janeiro de 2026:')
            p.drawString(70, 540, '- Serviço de terraplanagem: 85% concluído')
            p.drawString(70, 520, '- Serviço de drenagem: 60% concluído')
            p.drawString(70, 500, '- Pavimentação: 30% concluído')
            p.drawString(50, 470, 'Prazo contratual: 12 meses')
            p.drawString(50, 450, 'Início: 01/01/2026')
            p.drawString(50, 430, 'Término previsto: 31/12/2026')
            p.drawString(50, 400, 'Responsável técnico: Eng. Roberto Almeida - CREA 12345')
            p.drawString(50, 380, 'Fiscal do contrato: João Batista - Matrícula 6789')
            p.save()
            pdf_bytes = buffer.getvalue()
            buffer.close()
            return pdf_bytes
        except ImportError:
            # Fallback: minimal PDF stub
            return self._generate_minimal_pdf(title)

    def _generate_minimal_pdf(self, title):
        import hashlib
        # Criar um PDF mínimo válido
        content = f'{title}\n\nRelatório de execução de obras\nPrefeitura Municipal de Boa Vista\nJaneiro/2026'.encode('utf-8')
        # PDF minimal header + content (not a proper PDF but enough for testing)
        pdf = b'%PDF-1.4\n'
        pdf += b'1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n'
        pdf += b'2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n'
        pdf += b'3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] >>\nendobj\n'
        pdf += b'xref\n0 4\n'
        pdf += b'0000000000 65535 f \n'
        pdf += b'0000000009 00000 n \n'
        pdf += b'0000000058 00000 n \n'
        pdf += b'0000000115 00000 n \n'
        pdf += b'trailer\n<< /Size 4 /Root 1 0 R >>\n'
        pdf += b'startxref\n190\n%%EOF'
        return pdf
