# from celery import shared_task
# from django.core.mail import EmailMessage
# from django.conf import settings
# from django.template.loader import render_to_string
# from .utils import generate_invoice_pdf
# from django.core.files.base import ContentFile


# @shared_task
# def send_order_emails_task(order_id):
#    from .models import Order  # import inside task
#    order = Order.objects.get(id=order_id)

#    context = {
#        'order': order,
#        'user': order.user,
#        'shipping_address': order.address,
#        'shipping_cost': order.shipping_option,
#        'total': order.total_price,
#    }

#    subject_customer = f"Thanks for your order #{order.id}"
#    message_customer = render_to_string("order/order_customer.html", context)
#    email_customer = EmailMessage(
#        subject_customer,
#        message_customer,
#        settings.DEFAULT_FROM_EMAIL,
#        [order.user.email],
#    )
#    if order.invoice_pdf:
#        email_customer.attach_file(order.invoice_pdf.path)
#    email_customer.content_subtype = "html"
#    email_customer.send()

#    subject_owner = f"New Order #{order.id} placed"
#    message_owner = render_to_string("order/order_store_owner.html", context)
#    email_owner = EmailMessage(
#        subject_owner,
#        message_owner,
#        settings.DEFAULT_FROM_EMAIL,
#        [settings.STORE_OWNER_EMAIL],
#    )
#    if order.invoice_pdf:
#        email_owner.attach_file(order.invoice_pdf.path)
#    email_owner.content_subtype = "html"
#    email_owner.send()


# @shared_task
# def generate_invoice_task(order_id):
#    from .models import Order  # استوردها هنا لو حصل مشاكل
#    try:
#        order = Order.objects.get(id=order_id)
#        pdf_content = generate_invoice_pdf(order)
#        if pdf_content:
#            order.invoice_pdf.save(f"invoice_{order.id}.pdf", ContentFile(pdf_content))
#            order.save()
           
#            # لو عايز تبعت الإيميل بعد التوليد
#         #    send_order_emails_task.delay(order.id)
#    except Order.DoesNotExist:
#        pass  # أو سجّل الخطأ



