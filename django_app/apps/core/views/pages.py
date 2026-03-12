# django_app/apps/core/views/pages.py
import logging
from django.shortcuts import render, get_object_or_404
from apps.core.models import Assessment, PlaybookVersion, AgentRun, RiskCard

logger = logging.getLogger(__name__)


def home_upload_view(request):
    return render(request, 'core/home_upload.html')


def assessments_list_view(request):
    assessments = Assessment.objects.all().order_by('-created_at')
    ready_count = assessments.filter(status='playbook_ready').count()
    processing_count = assessments.filter(status='processing').count()
    return render(request, 'core/assessments_list.html', {
        'assessments': assessments,
        'ready_count': ready_count,
        'processing_count': processing_count,
    })


def playbook_detail_view(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id)
    latest_version = PlaybookVersion.objects.filter(
        assessment=assessment
    ).order_by('-version_number').first()

    playbook_data = {}
    current_version_number = 1
    prev_version = None
    diff_summary = None

    if latest_version and latest_version.payload:
        playbook_data = latest_version.payload
        current_version_number = latest_version.version_number
        diff_summary = latest_version.diff_summary
        logger.info(f"Loaded Playbook v{current_version_number} for {assessment_id}")

        # Get previous version for the "updated" banner
        if current_version_number > 1:
            prev_version = PlaybookVersion.objects.filter(
                assessment=assessment,
                version_number=current_version_number - 1
            ).first()

    # Compliance score: % of waves with zero blocking risks
    risk_cards = []
    total_blocking = 0
    total_warnings = 0
    if playbook_data.get('risk'):
        risk_cards = playbook_data['risk'].get('wave_risk_cards', [])
        total_blocking = sum(1 for r in risk_cards if r.get('is_blocking'))
        total_warnings = sum(1 for r in risk_cards if not r.get('is_blocking'))

    total_waves = len(playbook_data.get('architect', {}).get('waves', []))
    waves_with_blocking = len(set(r['wave_number'] for r in risk_cards if r.get('is_blocking')))
    compliance_score = 0
    if total_waves > 0:
        compliance_score = round(((total_waves - waves_with_blocking) / total_waves) * 100)

    # Agent runs for the thought stream panel
    agent_runs = AgentRun.objects.filter(
        assessment=assessment
    ).order_by('created_at')

    return render(request, 'core/playbook_detail.html', {
        'assessment': assessment,
        'playbook': playbook_data,
        'version': current_version_number,
        'diff_summary': diff_summary,
        'prev_version': prev_version,
        'compliance_score': compliance_score,
        'total_blocking': total_blocking,
        'total_warnings': total_warnings,
        'agent_runs': agent_runs,
        'show_update_banner': current_version_number > 1,
    })


def playbook_history_view(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id)
    versions = PlaybookVersion.objects.filter(
        assessment=assessment
    ).order_by('-version_number')

    # Build enriched version list with asset/wave counts
    enriched_versions = []
    for v in versions:
        payload = v.payload or {}
        waves = payload.get('architect', {}).get('waves', [])
        total_assets = sum(len(w.get('assets', [])) for w in waves)
        total_savings = 0
        per_wave = payload.get('accountant', {}).get('per_wave_costs', [])
        for pw in per_wave:
            total_savings += pw.get('estimated_savings', 0)

        enriched_versions.append({
            'version': v,
            'total_waves': len(waves),
            'total_assets': total_assets,
            'total_savings': round(total_savings, 2),
        })

    return render(request, 'core/playbook_history.html', {
        'assessment': assessment,
        'enriched_versions': enriched_versions,
        'latest_version': versions.first(),
    })


def governance_view(request):
    # Get all assessments with blocking risk cards that haven't been signed off
    pending_risks = RiskCard.objects.filter(
        is_blocking=True,
        signed_off_at__isnull=True
    ).select_related('wave', 'wave__assessment').order_by('-wave__assessment__created_at')

    signed_risks = RiskCard.objects.filter(
        signed_off_at__isnull=False
    ).select_related('wave', 'wave__assessment').order_by('-signed_off_at')[:10]

    # Recent agent run audit trail
    recent_runs = AgentRun.objects.all().select_related(
        'assessment'
    ).order_by('-created_at')[:20]

    return render(request, 'core/governance.html', {
        'pending_risks': pending_risks,
        'signed_risks': signed_risks,
        'recent_runs': recent_runs,
        'pending_count': pending_risks.count(),
        'signed_count': signed_risks.count(),
    })
