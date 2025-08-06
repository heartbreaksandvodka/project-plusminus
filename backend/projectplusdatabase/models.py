import uuid
from django.db import models
from authentication.models import User
from mt5_integration.models import MT5Account


class EATemplate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    config_schema = models.JSONField()  # JSON schema for EA config
    tier_access = models.JSONField()    # JSON for tiered access
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ea_templates'
        verbose_name = 'EA Template'
        verbose_name_plural = 'EA Templates'
        indexes = [
            models.Index(fields=["name"]),
        ]

    def __str__(self):
        return self.name

class UserEAInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ea_template = models.ForeignKey(EATemplate, on_delete=models.CASCADE)
    mt5_account = models.ForeignKey(MT5Account, on_delete=models.CASCADE)
    config = models.JSONField()  # User's config for this EA
    mt5_login = models.CharField(max_length=255)
    mt5_password_encrypted = models.BinaryField()  # Store encrypted, use KMS
    mt5_server = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_ea_instances'
        verbose_name = 'User EA Instance'
        verbose_name_plural = 'User EA Instances'
        unique_together = ("user", "ea_template", "mt5_account")
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["ea_template"]),
            models.Index(fields=["mt5_account"]),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.ea_template.name}"

class EAPerformance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_ea_instance = models.ForeignKey(UserEAInstance, on_delete=models.CASCADE)
    stats = models.JSONField()  # Flexible stats storage
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ea_performance'
        verbose_name = 'EA Performance'
        verbose_name_plural = 'EA Performance'
        indexes = [
            models.Index(fields=["user_ea_instance"]),
        ]

    def __str__(self):
        return f"Performance for {self.user_ea_instance}"
