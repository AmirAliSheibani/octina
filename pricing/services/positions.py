from django.utils import timezone

def deactivate_position(position, reason=""):
    position.is_active = False
    position.deactivation_reason = reason
    position.deactivated_at = timezone.now()
    position.save()