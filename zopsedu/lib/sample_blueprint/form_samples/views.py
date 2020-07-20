from flask import render_template, request, url_for, redirect, Blueprint, jsonify
from flask_login import login_required

from zopsedu.lib.form import forms

form_samples_blueprint = Blueprint(
    'form_samples',
    __name__,
    template_folder='templates',
    static_folder='static'
)


@form_samples_blueprint.route('/form-elements', methods=["GET", "POST"])
# @login_required
def form_elements():
    """test page for form elements"""
    form = forms.LoginForm(request.form)
    city_list = forms.SelectBoxForm(request.form)

    if request.method == 'POST' and form.validate():
        return redirect(url_for('ping'))
    return render_template(
        'form_samples/form_elements.html',
        select_url="/form_samples/select-random", form=form, city_list=city_list
    )


@form_samples_blueprint.route('/select-random', methods=["POST"])
def sample_selectbox_response():
    form = request.form
    q = form.get('q')
    initial_val = form.get('initial_val')
    if not q or len(q) < 3:
        return jsonify({"items": [],
                        "total_count": 0})


    from faker import Faker
    import random
    fake = Faker('tr_TR')
    number_of_results = random.choice([0, 0, 1, 2, 0, 3, 5, 6, 7, 0, 8, 13, 30])
    if not number_of_results:
        return jsonify({"items": [],
                        "total_count": 0})


    results = []
    for i in range(number_of_results):
        word = fake.word()
        break_index = random.choice(range(len(word)))
        results.append({"id": i, "text": "{}{}{}".format(word[0:break_index], q, word[break_index:])})

    return jsonify({"total_count": len(results), "items": results})
