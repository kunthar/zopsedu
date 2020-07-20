"""
    Datatable sorgularinina karsilik uygun paginated datayi dondurebilen classi iceren modul
"""
from flask.json import loads
from sqlalchemy import asc, desc, or_, String, and_


class DataTableServer:
    """
        Datatable sorgularinina karsilik uygun paginated datayi dondurebilen class
    """
    ORDERING = {'asc': asc, 'desc': desc}

    def __init__(self, columns, qry):
        """
        Datatable da gosterilen colonlarin modeldeki fieldlari ve
        Datatable da gosterilecek modelin sorgusu ile objeyi initialize eder.
        :param columns: index to datatable field mapping. dict {'0':Person.name, '1':Person.surname}
        :param qry: sqlalchemy base query object
        :return
        """
        self.columns = columns
        self.qry = qry

    def query(self, request):
        """
        Sadece 'String' fieldlarda arama ozelligi calisir yapilabilir
        Datatable sorgusundan gelen argumanlari alir ve bunlardan bir result objesi dondurur.
        Datatable uyumlulugu icin filtre uygulanmadan once tabloda bulunun
        row sayisi result.filtered_from degerinde dondurulur.

        :param request: flask request object
        :return Paginate object:
        """
        qry = self.qry
        args = loads(request.values.get("args"))
        order_field = self.columns[args["order"][0]["column"]]
        order_field_dir = self.ORDERING[args["order"][0]["dir"]]
        search_value = args["search"]["value"]
        start = args["start"]
        length = args["length"]

        global_search_list = []
        column_search_list = []
        if search_value:
            for column_index in self.columns.keys():
                column_field = self.columns[column_index]
                column_type = column_field.property.columns[0].type
                if isinstance(column_type, String):
                    global_search_list.append(
                        self.columns[column_index].ilike("%{}%".format(search_value)))
        for column_index in self.columns.keys():
            column = args["columns"][column_index]
            if column["search"]["value"]:
                column_field = self.columns[column_index]
                column_type = column_field.property.columns[0].type
                if isinstance(column_type, String):
                    column_search_list.append(
                        self.columns[column_index].ilike("%{}%".format(column["search"]["value"]))
                    )

        qry = qry.filter(or_(*global_search_list), and_(*column_search_list))
        qry = qry.order_by(order_field_dir(order_field))
        result = qry.paginate(page=int(start/length)+1, per_page=length, error_out=False)
        result.filtered_from = self.qry.count()
        return result
