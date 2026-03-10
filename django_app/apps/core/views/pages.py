# django_app/apps/core/views/pages.py

import logging
from django.shortcuts import render, get_object_or_404
from apps.core.models import Assessment, PlaybookVersion

logger = logging.getLogger(__name__)

def home_upload_view(request):
    logger.info("Rendering Home/Upload view.")
    return render(request, 'core/home_upload.html')

def assessments_list_view(request):
    assessments = Assessment.objects.all().order_by('-created_at')
    return render(request, 'core/assessments_list.html', {'assessments': assessments})

def playbook_detail_view(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id)
    
    # Grab the most recently saved JSON payload from the database
    latest_version = PlaybookVersion.objects.filter(assessment=assessment).order_by('-version_number').first()
    
    playbook_data = {}
    current_version_number = 1
    
    if latest_version and latest_version.payload:
        playbook_data = latest_version.payload
        current_version_number = latest_version.version_number
        logger.info(f"Loaded Playbook v{current_version_number} for {assessment_id}")

    return render(request, 'core/playbook_detail.html', {
        'assessment': assessment,
        'playbook': playbook_data,
        'version': current_version_number
    })

def playbook_history_view(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id)
    return render(request, 'core/playbook_history.html', {'assessment': assessment})

def governance_view(request):
    return render(request, 'core/governance.html')
