from django.contrib import admin
from .models import (
    Assessment, Asset, Dependency, MigrationWave, 
    CostModel, RiskCard, PlaybookVersion, AgentRun
)

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('id', 'name')

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('asset_id', 'name', 'asset_type', 'assessment')
    list_filter = ('asset_type',)
    search_fields = ('name', 'asset_id')

@admin.register(MigrationWave)
class MigrationWaveAdmin(admin.ModelAdmin):
    list_display = ('wave_number', 'name', 'assessment', 'status', 'duration_days')
    list_filter = ('status',)
    
@admin.register(RiskCard)
class RiskCardAdmin(admin.ModelAdmin):
    list_display = ('risk_type', 'wave', 'is_blocking', 'signed_off_by')
    list_filter = ('is_blocking', 'risk_type')

admin.site.register(Dependency)
admin.site.register(CostModel)
admin.site.register(PlaybookVersion)
admin.site.register(AgentRun)
