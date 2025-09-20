# apps/notifications/tasks.py
from celery import shared_task
from pyfcm import FCMNotification

@shared_task
def send_fcm_push(tokens, title, body, data):
    push_service = FCMNotification(api_key="FCM_SERVER_KEY")
    result = push_service.notify_multiple_devices(registration_ids=tokens, message_title=title, message_body=body, data_message=data)
    return result
