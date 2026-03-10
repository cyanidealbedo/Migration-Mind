# django_app/apps/core/views/api.py

import logging
import uuid
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.core.models import Assessment
from apps.core.services.enqueue import enqueue_assessment_job

logger = logging.getLogger(__name__)

class AssessmentListCreateAPI(APIView):
    def post(self, request):
        is_demo = request.data.get('is_demo', False)
        
        new_id = f"asm-{uuid.uuid4().hex[:8]}"
        assessment_name = "Demo Retail Application Stack" if is_demo else "Uploaded Assessment"
        
        assessment = Assessment.objects.create(
            id=new_id,
            name=assessment_name,
            status=Assessment.StatusChoices.PROCESSING
        )
        
        logger.info(f"[Assessment API] Created new assessment {assessment.id} (Demo: {is_demo})")

        enqueued = enqueue_assessment_job(assessment.id, is_demo=is_demo)
        
        if not enqueued:
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
            assessment = Assessment.objects.get(id=assessment_id)
            
            # 1. Put the assessment back into "processing" state
            assessment.status = Assessment.StatusChoices.PROCESSING
            assessment.save()
            
            logger.info(f"[Wave API] Wave {wave_number} marked complete. Re-triggering AI pipeline for {assessment_id}.")
            
            # 2. Drop a new message in the Service Bus! 
            # The AI will wake up and generate Version 2 of the Playbook.
            enqueue_assessment_job(assessment.id, is_demo=True)
            
            return Response({"message": f"Wave {wave_number} complete. Recalculating playbook..."}, status=status.HTTP_200_OK)
            
        except Assessment.DoesNotExist:
            return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)

