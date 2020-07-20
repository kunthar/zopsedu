

def list_to_form(form_list):
    form_dict = {}
    for form in form_list:
        form_dict.update({
            form['name']: form['value']
        })
    return form_dict