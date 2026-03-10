# django_app/apps/core/urls.py

from django.urls import path
from .views import pages, api

app_name = 'core'

urlpatterns =[
    # ---- Pages (UI) ----
    path('', pages.home_upload_view, name='home_upload'),
    path('assessments/', pages.assessments_list_view, name='assessments_list'),
    path('playbook/<str:assessment_id>/', pages.playbook_detail_view, name='playbook_detail'),
    path('playbook/<str:assessment_id>/history/', pages.playbook_history_view, name='playbook_history'),
    path('governance/', pages.governance_view, name='governance'),

    # ---- API Endpoints (DRF / AJAX) ----
    path('api/assessments/', api.AssessmentListCreateAPI.as_view(), name='api_assessments'),
    path('api/assessments/<str:assessment_id>/status/', api.AssessmentStatusAPI.as_view(), name='api_assessment_status'),
    path('api/assessments/<str:assessment_id>/waves/<int:wave_number>/complete/', api.WaveCompleteAPI.as_view(), name='api_wave_complete'),
]
