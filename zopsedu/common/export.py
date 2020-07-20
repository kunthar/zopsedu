from flask_classful import FlaskView, route
from flask_login import login_required
from io import BytesIO

from flask import make_response, request, render_template_string, send_file
from pdfkit import from_string

TEMPLATE_BODY = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <link href="{{ request.url_root }}static/assets/zopsedu/css/zopsedu.css" rel="stylesheet" type="text/css"/>
            <link href="{{ request.url_root }}static/assets/zopsedu/css/zopsedu-sablon.css" rel="stylesheet" type="text/css"/>
            <script src="{{ request.url_root }}static/assets/js/core/libraries/jquery.min.js"></script>    
            <meta charset="UTF-8">
        </head>
        <body>
            {{ content | safe }}
        </body>
        <script>
        $('.no-print').remove();
        </script>
        </html>
    """


class ExportView(FlaskView):

    @login_required
    @route('/export-pdf', methods=["POST"])
    def export_pdf(self):
        """
            returns pdf rendered from form 'template' data.
        :return:
        """
        content = request.form.get('template', '')
        as_attachment = True
        if request.form.get('attachment', '') == 'false':
            as_attachment = False

        template = render_template_string(TEMPLATE_BODY, content=content, request=request)
        output = BytesIO()
        pdf = from_string(template, output_path=False, options={'quiet': ''})
        output.write(pdf)
        output.seek(0)
        return send_file(output,
                         attachment_filename="zopsedu.pdf",
                         as_attachment=as_attachment)

    @login_required
    @route('/export-word', methods=["POST"])
    def export_word(self):
        """
            returns word rendered from form 'template' data.
        :return:
        """
        content = request.form.get('template', '')

        template = render_template_string(TEMPLATE_BODY, content=content, request=request)
        resp = make_response(template)

        resp.headers["Content-Type"] = "application/vnd.ms-word"
        resp.headers["Expires"] = "0"
        resp.headers["Cache-Control"] = "must-revalidate, post-check=0, pre-check=0"
        resp.headers["Content-Disposition"] = "attachment;filename=zopsedu.doc"

        return resp
