# django_app/apps/core/views/pages.py

import logging
from django.shortcuts import render, get_object_or_404
from apps.core.models import Assessment

logger = logging.getLogger(__name__)

def home_upload_view(request):
    """
    Renders the upload page where users drop their JSON/CSV or click 'Load Demo'.
    """
    logger.info("Rendering Home/Upload view.")
    return render(request, 'core/home_upload.html')

def assessments_list_view(request):
    assessments = Assessment.objects.all().order_by('-created_at')
    return render(request, 'core/assessments_list.html', {'assessments': assessments})

def playbook_detail_view(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id)
    return render(request, 'core/playbook_detail.html', {'assessment': assessment})

def playbook_history_view(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id)
    return render(request, 'core/playbook_history.html', {'assessment': assessment})

def governance_view(request):
    return render(request, 'core/governance.html')
