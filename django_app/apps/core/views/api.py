# django_app/apps/core/views/api.py

import logging
import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.core.models import Assessment, MigrationWave
from apps.core.services.enqueue import enqueue_assessment_job

logger = logging.getLogger(__name__)

class AssessmentListCreateAPI(APIView):
    def post(self, request):
        is_demo = request.data.get('is_demo', False)
        
        # 1. Create a unique Assessment record
        new_id = f"asm-{uuid.uuid4().hex[:8]}"
        assessment_name = "Demo Retail Application Stack" if is_demo else "Uploaded Assessment"
        
        assessment = Assessment.objects.create(
            id=new_id,
            name=assessment_name,
            status=Assessment.StatusChoices.PROCESSING # Set to processing immediately
        )
        
        logger.info(f"[Assessment API] Created new assessment {assessment.id} (Demo: {is_demo})")

        # 2. Enqueue the job to Azure Service Bus
        enqueued = enqueue_assessment_job(assessment.id, is_demo=is_demo)
        
        if not enqueued:
            # If Service Bus isn't configured yet (local dev), we'll fake the completion for UI testing
            logger.info("[Assessment API] Simulating agent pipeline completion for UI testing.")
            assessment.status = Assessment.StatusChoices.PLAYBOOK_READY
            assessment.save()

        return Response({
            "message": "Assessment created and job enqueued.",
            "assessment_id": assessment.id,
            "status": assessment.status
        }, status=status.HTTP_201_CREATED)


class AssessmentStatusAPI(APIView):
    def get(self, request, assessment_id):
        try:
            assessment = Assessment.objects.get(id=assessment_id)
            return Response({
                "assessment_id": assessment.id,
                "status": assessment.status
            }, status=status.HTTP_200_OK)
        except Assessment.DoesNotExist:
            return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)


class WaveCompleteAPI(APIView):
    def patch(self, request, assessment_id, wave_number):
        try:
            wave = MigrationWave.objects.get(assessment_id=assessment_id, wave_number=wave_number)
            wave.status = MigrationWave.StatusChoices.COMPLETED
            wave.save()
            logger.info(f"[Wave API] Marked Wave {wave_number} for Assessment {assessment_id} as COMPLETED.")
            
            # Here we would normally enqueue another job to recalculate the playbook
            # enqueue_recalculation_job(assessment_id)
            
            return Response({"message": f"Wave {wave_number} marked complete"}, status=status.HTTP_200_OK)
        except MigrationWave.DoesNotExist:
            return Response({"error": "Wave not found"}, status=status.HTTP_404_NOT_FOUND)
