#apps/core/models.py
import logging
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.db import models

logger = logging.getLogger(__name__)

class Assessment(models.Model):
    class StatusChoices(models.TextChoices):
        UPLOADED = 'uploaded', _('Uploaded')
        PROCESSING = 'processing', _('Processing (Agents Running)')
        PLAYBOOK_READY = 'playbook_ready', _('Playbook Ready')
        FAILED = 'failed', _('Failed')

    id = models.CharField(max_length=50, primary_key=True, help_text="Unique assessment ID")
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.UPLOADED)
    raw_file_url = models.URLField(blank=True, null=True, help_text="Blob URL of the uploaded assessment JSON/CSV")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.status})"


class Asset(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='assets')
    asset_id = models.CharField(max_length=100, help_text="Original ID from Azure Migrate")
    name = models.CharField(max_length=255)
    asset_type = models.CharField(max_length=50, help_text="e.g., VM, Database, WebApp")
    properties = models.JSONField(default=dict, help_text="OS, cores, memory, tags, etc.")

    def __str__(self):
        return f"{self.name} [{self.asset_type}]"


class Dependency(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='dependencies')
    source_asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='outgoing_dependencies')
    target_asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='incoming_dependencies')
    dependency_type = models.CharField(max_length=50, default="network")

    def __str__(self):
        return f"{self.source_asset.name} -> {self.target_asset.name}"


class MigrationWave(models.Model):
    class StatusChoices(models.TextChoices):
        PLANNED = 'planned', _('Planned')
        IN_PROGRESS = 'in_progress', _('In Progress')
        COMPLETED = 'completed', _('Completed')

    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='waves')
    wave_number = models.IntegerField()
    name = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PLANNED)
    duration_days = models.IntegerField(default=0)
    assets = models.ManyToManyField(Asset, related_name='waves')
    reasoning = models.TextField(blank=True, help_text="LLM reasoning for this wave sequence")

    class Meta:
        ordering = ['wave_number']

    def __str__(self):
        return f"Wave {self.wave_number}: {self.name}"


class CostModel(models.Model):
    wave = models.OneToOneField(MigrationWave, on_delete=models.CASCADE, related_name='cost_model')
    current_monthly_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    projected_monthly_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    estimated_savings = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    pricing_source = models.CharField(max_length=255, default="Azure Retail Prices API")
    calculation_details = models.JSONField(default=dict, help_text="Breakdown of costs by asset")

    def __str__(self):
        return f"Costs for Wave {self.wave.wave_number}"


class RiskCard(models.Model):
    wave = models.ForeignKey(MigrationWave, on_delete=models.CASCADE, related_name='risk_cards')
    risk_type = models.CharField(max_length=100, help_text="e.g., GDPR, SOX, Downtime")
    description = models.TextField()
    is_blocking = models.BooleanField(default=False)
    remediation_plan = models.TextField(blank=True)
    signed_off_by = models.CharField(max_length=100, blank=True, null=True)
    signed_off_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.risk_type} - Wave {self.wave.wave_number} (Blocking: {self.is_blocking})"


class PlaybookVersion(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='playbook_versions')
    version_number = models.IntegerField()
    payload = models.JSONField(help_text="Full snapshot of the playbook at this version")
    diff_summary = models.TextField(blank=True, help_text="What changed from the previous version")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-version_number']

    def __str__(self):
        return f"{self.assessment.name} - v{self.version_number}"


class AgentRun(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='agent_runs')
    agent_name = models.CharField(max_length=50, help_text="Surveyor, Architect, Accountant, Risk Officer")
    tokens_in = models.IntegerField(default=0)
    tokens_out = models.IntegerField(default=0)
    duration_ms = models.IntegerField(default=0)
    model_used = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=50, default="success")
    logs = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.agent_name} run for {self.assessment.id} [{self.status}]"



class UserProfile(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio        = models.TextField(blank=True, default='')
    avatar_data = models.TextField(blank=True, default='')   # base64 data URI
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile({self.user.username})"


class Notification(models.Model):
    class Level(models.TextChoices):
        INFO    = 'info',    'Info'
        SUCCESS = 'success', 'Success'
        WARNING = 'warning', 'Warning'
        ERROR   = 'error',   'Error'

    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title      = models.CharField(max_length=200)
    body       = models.TextField(blank=True, default='')
    level      = models.CharField(max_length=10, choices=Level.choices, default=Level.INFO)
    is_read    = models.BooleanField(default=False)
    link       = models.CharField(max_length=300, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.level}] {self.title} → {self.user.username}"


# ── HELPER: call this from function_app.py / api.py to fire notifications ──
def notify(user, title, body='', level='info', link=''):
    """Create a Notification for a user. Safe to call from anywhere."""
    if user is None:
        return
    Notification.objects.create(user=user, title=title, body=body, level=level, link=link)


