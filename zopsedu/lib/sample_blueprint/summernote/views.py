from flask import render_template, request, url_for, redirect, Blueprint

from zopsedu.lib.form import forms

summernote_blueprint = Blueprint(
    'summernote',
    __name__,
    template_folder='templates',
    static_folder='static'
)


@summernote_blueprint.route('/summernote', methods=["GET", "POST"])
def summer_note():
    form = forms.SummerNoteForm(request.form)
    if request.method == 'POST' and form.validate():
        return redirect(url_for('ping'))
    return render_template('summernote/summernote.html', form=form)
