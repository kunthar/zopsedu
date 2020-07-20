from flask import render_template, request, url_for, redirect, Blueprint, jsonify
from flask.json import dumps

table_blueprint = Blueprint(
    'table',
    __name__,
    template_folder='templates',
    static_folder='static',
)


@table_blueprint.route('/table')
# @login_required
def table_with_buttons():
    """Table example"""
    return render_template('table/table_manage_buttons.html')


@table_blueprint.route('/parent_child_table')
def table_with_parent_child():
    """Table example"""
    data = [
        [1, 2, "Hayat", 4, 5, '<i class="fa fa-plus-square fa-2x" aria-hidden="true"></i>',
         ["A", "B", "C", "D"], [[1, 2, 3, 4], [2, 3, 4, 5], [3, 4, 5, 6]]],
        [1, 2, "W*ndoz", 4, 5, '<i class="fa fa-plus-square fa-2x" aria-hidden="true"></i>',
         ["A", "B", "C", "D"], [[1, 2, 3, 4], [2, 3, 4, 5], [3, 4, 5, 6]]],
        [1, 2, "ile", 4, 5, '<i class="fa fa-plus-square fa-2x" aria-hidden="true"></i>',
         ["A", "B", "C", "D"], [[1, 2, 3, 4], [2, 3, 4, 5], [3, 4, 5, 6]]],
        [1, 2, "daha", 4, 5, '<i class="fa fa-plus-square fa-2x" aria-hidden="true"></i>',
         ["A", "B", "C", "D"], [[1, 2, 3, 4], [2, 3, 4, 5], [3, 4, 5, 6]]],
        [1, 2, "guzel", 4, 5, '<i class="fa fa-plus-square fa-2x" aria-hidden="true"></i>',
         ["A", "B", "C", "D"], [[1, 2, 3, 4], [2, 3, 4, 5], [3, 4, 5, 6]]],
        [1, 2, "Yasasin", 4, 5, '<i class="fa fa-plus-square fa-2x" aria-hidden="true"></i>',
         ["A", "B", "C", "D"], [[1, 2, 3, 4], [2, 3, 4, 5], [3, 4, 5, 6]]],
        [1, 2, "W*ndoz !!!", 4, 5, '<i class="fa fa-plus-square fa-2x" aria-hidden="true"></i>',
         ["A", "B", "C", "D"], []],
    ]

    return render_template('table/table_parent_child.html', data=dumps(data))


@table_blueprint.route('/parent_child_table/data', methods=['DELETE', 'PUT'])
def table_with_parent_child_data():
    if request.method == 'DELETE':
        # verinin validasyonu ve silinip silinemiyecegi kontrol edilir.
        # ardindan uygun status code geri dondurulur. Ornekte her zaman 200 donuyor.
        json = request.json
        if 'parentData' in json.keys():
            # parentData eger var ise silme islemi bir row un child i icindedir.

            json['parentData'][-1].remove(json['targetData'])
            return jsonify([])
        else:
            return jsonify([])
    if request.method == 'PUT':
        json = request.json
        json['parentData'][-1].append(json['newData'])
        return jsonify(json['parentData'])
