# django_app/apps/core/services/enqueue.py

import json
import logging
from django.conf import settings
from azure.servicebus import ServiceBusClient, ServiceBusMessage
from apps.core.models import Assessment

logger = logging.getLogger(__name__)

def enqueue_assessment_job(assessment_id: str, is_demo: bool = False):
    """
    Sends a message to the Azure Service Bus queue to trigger the Agent Framework orchestrator.
    """
    raw_conn_string = getattr(settings, 'SERVICE_BUS_CONNECTION_STRING', None)
    queue_name = getattr(settings, 'SERVICE_BUS_QUEUE_NAME', 'assessment-jobs')
    
    # Clean the string just in case it has quotes
    connection_string = raw_conn_string.strip("'\"") if raw_conn_string else None

    if not connection_string or "your-namespace" in connection_string:
        logger.warning(f"[Service Bus] No valid connection string found. Skipping enqueue for {assessment_id}. (Development Mode)")
        return False

    try:
        # Create the message payload matching the agent contract
        payload = {
            "assessment_id": assessment_id,
            "is_demo": is_demo,
            "requested_run_type": "full_pipeline"
        }
        
        message = ServiceBusMessage(json.dumps(payload))
        
        # Connect and send
        with ServiceBusClient.from_connection_string(connection_string) as client:
            with client.get_queue_sender(queue_name) as sender:
                sender.send_messages(message)
                
        logger.info(f"[Service Bus] Successfully enqueued job for Assessment: {assessment_id}")
        return True
        
    except Exception as e:
        logger.error(f"[Service Bus] Failed to enqueue job for {assessment_id}. Error: {str(e)}")
        Assessment.objects.filter(id=assessment_id).update(status=Assessment.StatusChoices.FAILED)
        return False
