from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth import user_logged_in, user_logged_out
from django.contrib.postgres.search import SearchVector

from sabe.apps.audit.models import Audit
from sabe.apps.documents.models import Document
from sabe.apps.documents.services import update_search_vector as update_doc_search_vector
from sabe.apps.findings.models import Finding, Evidence
from sabe.apps.findings.services import update_finding_search_vector
from sabe.apps.legal.models import LegalFramework
from sabe.apps.legal.services import update_legal_search_vector
from sabe.apps.audit_log.services import log_action


@receiver(post_save, sender=Audit)
def audit_post_save(sender, instance, created, **kwargs):
    from sabe.apps.audit.services import update_audit_search_vector
    if not instance.search_vector:
        update_audit_search_vector(instance)


@receiver(post_save, sender=Document)
def document_post_save(sender, instance, created, **kwargs):
    if instance.extracted_text and not instance.search_vector:
        update_doc_search_vector(instance)


@receiver(post_save, sender=Finding)
def finding_post_save(sender, instance, created, **kwargs):
    if created:
        update_finding_search_vector(instance)


@receiver(post_save, sender=Evidence)
def evidence_post_save(sender, instance, created, **kwargs):
    if created:
        update_finding_search_vector(instance.finding)


@receiver(post_save, sender=LegalFramework)
def legal_post_save(sender, instance, created, **kwargs):
    update_legal_search_vector(instance)


@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    log_action(user, 'login', request=request, details=f'Usuário {user.username} realizou login')


@receiver(user_logged_out)
def user_logged_out_handler(sender, request, user, **kwargs):
    if user:
        log_action(user, 'logout', request=request, details=f'Usuário {user.username} realizou logout')


@receiver(post_save, sender=Finding)
def finding_audit_log(sender, instance, created, **kwargs):
    action = 'create' if created else 'update'
    log_action(
        instance.created_by if created else instance.updated_by,
        action,
        model_name='Finding',
        object_id=instance.id,
        details=f'Achado: {instance.title}'
    )


@receiver(post_delete, sender=Finding)
def finding_delete_audit_log(sender, instance, **kwargs):
    log_action(
        None,
        'delete',
        model_name='Finding',
        object_id=instance.id,
        details=f'Achado excluído: {instance.title}'
    )
