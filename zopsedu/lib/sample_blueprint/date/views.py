from flask import render_template, request, url_for, redirect, Blueprint
from flask_login import login_required
from zopsedu.lib.form import forms

date_blueprint = Blueprint(
    'date',
    __name__,
    template_folder='templates',
)


@date_blueprint.route("/index", methods=["GET", "POST"])
@login_required
def date():
    """Date form sample view"""
    form = forms.GenderAndALanguageForm(request.form, d2=2)
    # print(request.form.get(form.file.id))  # we can reach the input value like this to get file ids
    if request.method == 'POST' and form.validate():
            return redirect(url_for('date.ping'))

    return render_template("date/date.html", form=form)
