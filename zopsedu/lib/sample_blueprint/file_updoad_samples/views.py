from flask import render_template, request, url_for, redirect, Blueprint

# from zopsedu.lib.form import forms

file_upload_samples_blueprint = Blueprint(
    'file_updload_samples',
    __name__,
    template_folder='templates',
    static_folder='static'
)


@file_upload_samples_blueprint.route('/file_upload_samples', methods=["GET"])
# @login_required
def file():
    """test page for form elements"""
    # form = forms.InlineLoginForm(request.form)
    # if request.method == 'POST' and form.validate():
    #     return redirect(url_for('ping'))
    return render_template('file_upload_samples/file_upload.html')


# @file_upload_samples_blueprint.route('/file_upload_samples', methods=["POST"])
# # @login_required
# def file_upload():
#     files = request.files
#     return render_template('file_upload.html', files=files)
