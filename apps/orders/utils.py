from io import BytesIO
from django.template.loader import get_template
from weasyprint import HTML, CSS
from django.utils import translation
from django.conf import settings
import os
from django.templatetags.static import static
from django.utils import timezone

def generate_invoice_pdf(request, order, lang_code='en'):
    translation.activate(lang_code)
    logo_url = request.build_absolute_uri(static('images/modyex-logo.png'))
    template = get_template('order/invoice_template.html')
    context = {
        'order': order,
        'user': order.user,
        'items': order.items.all(),
        'logo_url': logo_url,
    }
    html_string = template.render(context)

    translation.deactivate()


    cairo_font_path = os.path.join(settings.BASE_DIR, 'static/fonts/Cairo-Regular.ttf')

    css = CSS(string=f"""
        @font-face {{
            font-family: 'Cairo';
            src: url('file://{cairo_font_path}');
        }}
        body {{
            font-family: 'Cairo', sans-serif;
        }}
    """)

    pdf_file = BytesIO()
    HTML(string=html_string, base_url=settings.BASE_DIR).write_pdf(pdf_file, stylesheets=[css])
    pdf_file.seek(0)

    return pdf_file.getvalue()
