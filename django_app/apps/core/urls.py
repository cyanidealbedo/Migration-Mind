# django_app/apps/core/urls.py
from django.urls import path
from .views import pages, api

app_name = 'core'

urlpatterns = [
    # ── Pages (UI) ──
    path('', pages.home_upload_view, name='home_upload'),
    path('assessments/', pages.assessments_list_view, name='assessments_list'),
    path('playbook/<str:assessment_id>/', pages.playbook_detail_view, name='playbook_detail'),
    path('playbook/<str:assessment_id>/history/', pages.playbook_history_view, name='playbook_history'),
    path('governance/', pages.governance_view, name='governance'),

    # ── API: Assessments ──
    path('api/assessments/', api.AssessmentListCreateAPI.as_view(), name='api_assessments'),
    path('api/assessments/<str:assessment_id>/', api.AssessmentDetailAPI.as_view(), name='api_assessment_detail'),
    path('api/assessments/<str:assessment_id>/status/', api.AssessmentStatusAPI.as_view(), name='api_assessment_status'),
    path('api/assessments/<str:assessment_id>/cancel/', api.CancelAssessmentAPI.as_view(), name='api_assessment_cancel'),
    path('api/assessments/<str:assessment_id>/versions/', api.PlaybookVersionListAPI.as_view(), name='api_versions'),
    path('api/assessments/<str:assessment_id>/agent-runs/', api.AgentRunsAPI.as_view(), name='api_agent_runs'),

    # ── API: Waves ──
    path('api/assessments/<str:assessment_id>/waves/<int:wave_number>/complete/', api.WaveCompleteAPI.as_view(), name='api_wave_complete'),

    # ── API: Risks ──
    path('api/assessments/<str:assessment_id>/risks/acknowledge/', api.RiskAcknowledgeAPI.as_view(), name='api_risk_acknowledge_body'),
    path('api/assessments/<str:assessment_id>/risks/<int:risk_id>/acknowledge/', api.RiskAcknowledgeAPI.as_view(), name='api_risk_acknowledge'),

    # ── API: Governance ──
    path('api/assessments/<str:assessment_id>/governance/signoff/', api.GovernanceSignoffAPI.as_view(), name='api_governance_signoff'),
]
