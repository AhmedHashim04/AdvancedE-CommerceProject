from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notifications'


#WSGI : Web Server Gateway Interface (One way communication) client cannot send data to server
#ASGI : Asynchronous Server Gateway Interface (Two way communication) client can send data to server and server can send data to client

# Sockets Limits :
    # - Connection leaks
    # - Too many idle sockets : make ram lake 
    # - Broadcast inefficiency : if many users are online, sending to all is inefficient
    # - load balancing : distribute connections across multiple servers

# SSE : Server Still Sent Events but (One way communication) client cannot send data to server
# WebSockets : (Two way communication) client can send data to server and server can send data to client
# Push Notifications : (Mobile and web) requires user permission. uses (FCM[Google Cloud Messaging], APNs[Apple Push Notification Service])


# Third-party =   First-party(Django / programmer who implements the feature) 
#               + Second-party(Client)
#               + Third-party (Another service provider that enhances the feature )

# Third-party Limits :
    # - Dependency : if third-party service goes down, your feature goes down
    # - Cost : many third-party services charge based on usage
    # - Privacy : user data may be shared with third-party service
    # - Customization : limited to what the third-party service offers
    # - Integration : may require additional work to integrate with your existing system

    # Examples :
            # - django-notifications-hq
            # - django-activity-stream

    # Customization ability :
        # - customize templates style 
        # - customize delivery methods (email, SMS, push notifications)
        # - Filtering options (only certain types of users)
        # - Real-time / Batch

    # Customization challenges :
        # - FCM, APNS (Mobile Push Notifications)
        # - Dashboard customization (adapting the notification dashboard to specific needs)
        # - SMS / Email Options (integrating with services like Twilio, SendGrid)
        # - Large-scale handling (efficiently managing notifications for a large user base)