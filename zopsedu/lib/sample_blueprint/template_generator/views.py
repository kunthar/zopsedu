from flask import render_template, request, url_for, redirect, Blueprint, flash, send_file

from sqlalchemy.orm.exc import NoResultFound
from zopsedu.lib.renders import TRenderer
from zopsedu.models.sablon import Sablon
from zopsedu.models import File
from zopsedu.lib.db import DB
from io import BytesIO

template_generator_blueprint = Blueprint(
    'template_generator',
    __name__,
    template_folder='templates',
)


@template_generator_blueprint.route("/download/", methods=["GET", "POST"])
def bring_template():
    """Databaseten okunan sablonun işlenip, işlenen dökümanın indirilmesini sağlar"""
    try:
        template = DB.session.query(Sablon).filter_by(id=10).one()
    except NoResultFound:
        flash("HATA!!! Istenilen sablon bulunamadi.")
        return redirect(url_for("template_generator.upload"))  # Importante
    context = {"name": "Sample Name"}

    renderer = TRenderer(template=template.file.file_object, context=context)
    rendered_document = renderer.render_document()

    if request.method == "POST":
        return send_file(
            BytesIO(rendered_document),
            as_attachment=True,
            attachment_filename=template.file.content.file.filename,
            mimetype='application/vnd.oasis.opendocument.text'
        )
    return render_template("template_generator/table.html", person=context)  # Importante


@template_generator_blueprint.route('/upload/', methods=["GET", "POST"])
def upload():
    """Sablon yukleme ve sablonun database kayit edilmesi icin kullanilir."""
    uploaded_file = request.files.get('sablon', None)
    if uploaded_file:
        yeni_sablon_file = File(content=uploaded_file)
        DB.session.add(yeni_sablon_file)
        DB.session.flush()
        yeni_sablon = Sablon(file=yeni_sablon_file.id)
        DB.session.add(yeni_sablon)
        DB.session.commit()
    return render_template("template_generator/upload.html")


@template_generator_blueprint.route('/ping/')
def ping():
    return render_template("template_generator/ping.html")
