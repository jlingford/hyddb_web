import logging

from celery.signals import task_failure, task_success
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Q
from django.db.models.signals import post_save
from django.template.loader import render_to_string

from browser.models import HydrogenaseSequence, NonHydrogenaseSequence

from .classifier import BLASTClassifier
from .models import ClassificationTask


logger = logging.getLogger(__name__)


######################
# Mail Notifications #
######################

def mail(task_id, template, recipient, subject):
    mail_body = render_to_string(template, {'task_id': task_id})
    send_mail(subject, mail_body, 'noreply@services.birc.au.dk',
              recipient_list=[recipient])


def if_mail_is_available(f):
    """
    Only run decorated function if e-mail was provided for the given task.
    """
    def wrapper(sender, *args, **kwargs):
        task_id = sender.request.id
        recipient = ClassificationTask.objects.get(
            Q(task_id=task_id) | Q(downstream_protein_task_id=task_id)
        ).email_address

        if recipient:
            return f(*args, sender=sender, recipient=recipient, **kwargs)
    return wrapper


@task_success.connect
@if_mail_is_available
def send_task_success_mail(sender=None, recipient=None, *args, **kwargs):
    mail(task_id=sender.request.id,
         template='classifier/mail/success.txt',
         recipient=recipient,
         subject='HydroClf: Job completed ({})'.format(sender.request.id))


@task_failure.connect
@if_mail_is_available
def send_task_failure_mail(sender=None, recipient=None, *args, **kwargs):
    mail(task_id=sender.request.id,
         template='classifier/mail/failure.txt',
         recipient=recipient,
         subject='HydroClf: Job failed ({})'.format(sender.request.id))


#################
# Rebuild BLAST #
#################

def rebuild_blast_database(*args, **kwargs):
    if kwargs.get('raw'):
        logger.debug('rebuild_blast_database() bypassed')
        return

    X = []
    y = []

    for entry in HydrogenaseSequence.objects.all():
        X.append(entry.sequence)

        # [FeFe] Group A subtypes are not considered in the BLAST
        # classification step, so we just group all of the sequences belonging
        # to one of the subtypes into one class.
        if entry.hydrogenase_class.name.startswith('[FeFe] Group A'):
            y.append('[FeFe] Group A')
        else:
            y.append(entry.hydrogenase_class.name)

    for entry in NonHydrogenaseSequence.objects.all():
        X.append(entry.protein_sequence)
        y.append('NONHYDROGENASE')

    BLASTClassifier(db=settings.BLASTDB).fit(X, y)


post_save.connect(rebuild_blast_database, sender=HydrogenaseSequence)
post_save.connect(rebuild_blast_database, sender=NonHydrogenaseSequence)
