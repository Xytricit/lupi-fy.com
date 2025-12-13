from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Purchase, Project, CreatorPayout


@receiver(post_save, sender=Purchase)
def purchase_completed(sender, instance, created, **kwargs):
    """Send notifications when purchase is completed"""
    if instance.status == 'completed' and not created:
        # Send email to buyer
        send_mail(
            subject=f'Purchase Confirmed: {instance.project.title}',
            message=f'Thank you for your purchase! You can now download your project at {settings.SITE_URL}/marketplace/{instance.project.slug}/',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.buyer.email],
            fail_silently=True
        )
        
        # Notify creator
        send_mail(
            subject=f'New Sale: {instance.project.title}',
            message=f'Congratulations! You made a sale of ${instance.creator_earnings}. View details at {settings.SITE_URL}/marketplace/creator/',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.project.creator.email],
            fail_silently=True
        )


@receiver(post_save, sender=Project)
def project_approved(sender, instance, created, **kwargs):
    """Notify creator when project is approved"""
    if instance.status == 'approved' and not created:
        send_mail(
            subject=f'Project Approved: {instance.title}',
            message=f'Your project has been approved and is now live on the marketplace! View it at {settings.SITE_URL}/marketplace/{instance.slug}/',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.creator.email],
            fail_silently=True
        )


@receiver(post_save, sender=Project)
def project_rejected(sender, instance, created, **kwargs):
    """Notify creator when project is rejected"""
    if instance.status == 'rejected' and not created:
        send_mail(
            subject=f'Project Rejected: {instance.title}',
            message=f'Your project "{instance.title}" was rejected.\n\nReason: {instance.rejection_reason}\n\nPlease revise and resubmit.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.creator.email],
            fail_silently=True
        )
