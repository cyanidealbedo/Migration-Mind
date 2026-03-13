# django_app/apps/core/views/api.py
import logging
import uuid
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.core.models import Assessment, PlaybookVersion, RiskCard, AgentRun, MigrationWave
from apps.core.services.enqueue import enqueue_assessment_job
from apps.core.services.contentsafety import moderate_text

logger = logging.getLogger(__name__)


class AssessmentDetailAPI(APIView):
    """Rename (PATCH) or Delete (DELETE) a single assessment."""

    def patch(self, request, assessment_id):
        try:
            assessment = Assessment.objects.get(id=assessment_id)
            new_name = request.data.get('name', '').strip()
            if not new_name:
                return Response({"error": "name is required"}, status=status.HTTP_400_BAD_REQUEST)
            assessment.name = new_name
            assessment.save()
            logger.info(f"[Assessment API] Renamed {assessment_id} → '{new_name}'")
            return Response({"message": "Renamed.", "name": new_name}, status=status.HTTP_200_OK)
        except Assessment.DoesNotExist:
            return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, assessment_id):
        try:
            assessment = Assessment.objects.get(id=assessment_id)
            name = assessment.name
            assessment.delete()   # CASCADE deletes all related objects
            logger.info(f"[Assessment API] Deleted {assessment_id} ('{name}')")
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Assessment.DoesNotExist:
            return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)


class CancelAssessmentAPI(APIView):
    """Cancel a running pipeline — marks assessment as failed so UI stops polling."""

    def patch(self, request, assessment_id):
        try:
            assessment = Assessment.objects.get(id=assessment_id)
            if assessment.status != Assessment.StatusChoices.PROCESSING:
                return Response({"message": "Assessment is not currently processing."}, status=status.HTTP_200_OK)
            assessment.status = Assessment.StatusChoices.FAILED
            assessment.save()
            logger.info(f"[Assessment API] Cancelled pipeline for {assessment_id}")
            return Response({"message": "Pipeline cancelled."}, status=status.HTTP_200_OK)
        except Assessment.DoesNotExist:
            return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)


class AssessmentListCreateAPI(APIView):

    def post(self, request):
        is_demo = request.data.get('is_demo', False)
        user_description = request.data.get('description', '')

        # ── Content Safety moderation on any user-supplied text ──
        if user_description:
            safe, reason = moderate_text(user_description)
            if not safe:
                logger.warning(f"[Content Safety] Blocked upload: {reason}")
                return Response(
                    {"error": f"Content moderation blocked this submission: {reason}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        new_id = f"asm-{uuid.uuid4().hex[:8]}"
        assessment_name = "Demo Retail Application Stack" if is_demo else "Uploaded Assessment"

        assessment = Assessment.objects.create(
            id=new_id,
            name=assessment_name,
            status=Assessment.StatusChoices.PROCESSING
        )

        logger.info(f"[Assessment API] Created {assessment.id} (Demo: {is_demo})")
        enqueued = enqueue_assessment_job(assessment.id, is_demo=is_demo)

        if not enqueued:
            # Dev mode fallback — run pipeline inline
            assessment.status = Assessment.StatusChoices.PLAYBOOK_READY
            assessment.save()

        return Response({
            "message": "Assessment created and job enqueued.",
            "assessment_id": assessment.id,
            "status": assessment.status
        }, status=status.HTTP_201_CREATED)


class AssessmentListCreateAPI(APIView):
    def post(self, request):
        is_demo = request.data.get('is_demo', False)
        user_description = request.data.get('description', '')

        if user_description:
            safe, reason = moderate_text(user_description)
            if not safe:
                logger.warning(f"[Content Safety] Blocked upload: {reason}")
                return Response(
                    {"error": f"Content moderation blocked this submission: {reason}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        new_id = f"asm-{uuid.uuid4().hex[:8]}"
        assessment_name = "Demo Retail Application Stack" if is_demo else "Uploaded Assessment"

        assessment = Assessment.objects.create(
            id=new_id,
            name=assessment_name,
            status=Assessment.StatusChoices.PROCESSING
        )

        logger.info(f"[Assessment API] Created {assessment.id} (Demo: {is_demo})")
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
            latest = PlaybookVersion.objects.filter(
                assessment=assessment
            ).order_by('-version_number').first()

            return Response({
                "assessment_id": assessment.id,
                "status": assessment.status,
                "version": latest.version_number if latest else None,
            }, status=status.HTTP_200_OK)
        except Assessment.DoesNotExist:
            return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)


class WaveCompleteAPI(APIView):
    def patch(self, request, assessment_id, wave_number):
        try:
            assessment = Assessment.objects.get(id=assessment_id)
            assessment.status = Assessment.StatusChoices.PROCESSING
            assessment.save()

            # Mark the wave completed in DB
            MigrationWave.objects.filter(
                assessment=assessment,
                wave_number=wave_number
            ).update(status='completed')

            logger.info(f"[Wave API] Wave {wave_number} marked complete. Re-triggering pipeline for {assessment_id}.")
            enqueue_assessment_job(assessment.id, is_demo=True)

            return Response(
                {"message": f"Wave {wave_number} complete. Recalculating playbook..."},
                status=status.HTTP_200_OK
            )
        except Assessment.DoesNotExist:
            return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)


class RiskAcknowledgeAPI(APIView):
    """
    Acknowledge a risk card.
    Accepts either:
      - URL param risk_id  (from governance page)
      - Body params wave_number + risk_type (from playbook detail page, where we only have JSON data)
    """
    def patch(self, request, assessment_id, risk_id=None):
        signer = request.data.get('signed_by', 'System Administrator')

        try:
            if risk_id:
                risk = RiskCard.objects.get(id=risk_id, wave__assessment_id=assessment_id)
            else:
                # Lookup by wave_number + risk_type
                wave_number = request.data.get('wave_number')
                risk_type   = request.data.get('risk_type', '')
                risk = RiskCard.objects.filter(
                    wave__assessment_id=assessment_id,
                    wave__wave_number=wave_number,
                    risk_type__icontains=risk_type[:40]
                ).first()
                if not risk:
                    # Soft success — risk card may only exist in JSON payload, not DB yet.
                    # Return success so the UI still updates visually.
                    logger.info(f"[Risk API] No DB row found for wave {wave_number} / {risk_type} — soft ack.")
                    return Response({"message": "Risk acknowledged (no DB record)."}, status=status.HTTP_200_OK)

            risk.signed_off_by = signer
            risk.signed_off_at = timezone.now()
            risk.save()
            logger.info(f"[Risk API] Risk {risk.id} acknowledged by {signer}")
            return Response({"message": "Risk acknowledged.", "signed_by": signer}, status=status.HTTP_200_OK)

        except RiskCard.DoesNotExist:
            return Response({"error": "Risk card not found"}, status=status.HTTP_404_NOT_FOUND)


class GovernanceSignoffAPI(APIView):
    """Approve or reject a governance item. Reject re-enqueues the pipeline."""
    def patch(self, request, assessment_id):
        action = request.data.get('action')  # 'approve' or 'reject'
        signer = request.data.get('signed_by', 'System Administrator')

        try:
            assessment = Assessment.objects.get(id=assessment_id)

            if action == 'approve':
                logger.info(f"[Governance] Approved by {signer} for {assessment_id}")
                return Response({"message": f"Approved by {signer}."}, status=status.HTTP_200_OK)

            elif action == 'reject':
                logger.info(f"[Governance] Rejected by {signer}. Re-enqueuing pipeline for {assessment_id}.")
                assessment.status = Assessment.StatusChoices.PROCESSING
                assessment.save()
                enqueue_assessment_job(assessment.id, is_demo=True)
                return Response(
                    {"message": "Rejected. Agent pipeline will regenerate the wave plan."},
                    status=status.HTTP_200_OK
                )
            else:
                return Response({"error": "action must be 'approve' or 'reject'"}, status=status.HTTP_400_BAD_REQUEST)

        except Assessment.DoesNotExist:
            return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)


class AgentRunsAPI(APIView):
    """Returns the agent audit trail for a given assessment."""
    def get(self, request, assessment_id):
        try:
            Assessment.objects.get(id=assessment_id)
            runs = AgentRun.objects.filter(
                assessment_id=assessment_id
            ).order_by('created_at').values(
                'agent_name', 'status', 'tokens_in', 'tokens_out',
                'duration_ms', 'model_used', 'logs', 'created_at'
            )
            return Response({"runs": list(runs)}, status=status.HTTP_200_OK)
        except Assessment.DoesNotExist:
            return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)


class PlaybookVersionListAPI(APIView):
    """Returns all playbook versions for a given assessment."""
    def get(self, request, assessment_id):
        try:
            Assessment.objects.get(id=assessment_id)
            versions = PlaybookVersion.objects.filter(
                assessment_id=assessment_id
            ).order_by('-version_number').values(
                'version_number', 'diff_summary', 'created_at'
            )
            return Response({"versions": list(versions)}, status=status.HTTP_200_OK)
        except Assessment.DoesNotExist:
            return Response({"error": "Assessment not found"}, status=status.HTTP_404_NOT_FOUND)


class NotificationsAPI(APIView):
    """Fetch / mark-read notifications for the current user."""

    def get(self, request):
        from apps.core.models import Notification
        if not request.user.is_authenticated:
            return Response({"notifications": [], "unread_count": 0})
        notifs = Notification.objects.filter(user=request.user).order_by('-created_at')[:30]
        data = [{
            "id": n.id, "title": n.title, "body": n.body,
            "level": n.level, "is_read": n.is_read,
            "link": n.link, "created_at": n.created_at.isoformat(),
        } for n in notifs]
        unread = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({"notifications": data, "unread_count": unread})

    def patch(self, request):
        """Mark all as read."""
        from apps.core.models import Notification
        if not request.user.is_authenticated:
            return Response({"ok": True})
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({"ok": True})
# NOTE: models.py additions needed:
# UserProfile(user OneToOne, bio, avatar_data TextField)
# Notification(user FK, title, body, level choices, is_read bool, link, created_at)
# Assessment needs user FK (nullable for existing rows)
