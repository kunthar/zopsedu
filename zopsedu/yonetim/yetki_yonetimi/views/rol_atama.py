""" Rol Atama Modülü """
from flask_allows import Or
from sqlalchemy.orm import joinedload

from flask import render_template, request, redirect, url_for, jsonify, render_template_string
from flask_babel import gettext as _
from flask_classful import FlaskView, route
from flask_login import login_required, current_user

from zopsedu.auth.models.auth import UserRole, User
from zopsedu.auth.permissions import permission_dict
from zopsedu.lib.db import DB
from zopsedu.models import Person, Role as RoleModel
from zopsedu.auth.lib import auth, Permission, Role
from zopsedu.personel.models.personel import Personel
from zopsedu.personel.models.unvan import HitapUnvan
from zopsedu.yonetim.yetki_yonetimi.forms import RolAtamaForm, KisiSearchForm


class RolAtamaView(FlaskView):
    """Kullaniciya rol atama ekrani"""

    excluded_methods = [
        "qry",
        "user_id"
    ]

    def process_data(self, result, form_data, total_record):
        data = [[
            index + 1,
            r.unvan_ad,
            "{} {}".format(r.ad, r.soyad),
            render_template_string(
                """<ul>
                    {% if item.roles %}
                        {% for r in item.roles %}
                            <li>{{ r.name }}</li> 
                        {% endfor %}
                        {% else %}
                        {{ _('Henüz bu kullanıcıya ait bir rol bulunmamaktadır.') }}

                    {% endif %}
                    </ul>
                """,
                item=r.User),
            render_template_string("""
             <button class="btn btn-success"
                     data-toggle="modal"
                     onclick="rol_atama_{{id}}()">
                     Rol Ata
            </button>
               <script>
                    function rol_atama_{{ id }}() {
                     $('#rolAtaModal').modal('show');
                     $('#ata').attr("formaction", "{{ url_for('yetki_yonetimi.kisi_rol_ata', u_id=id) }}");
                    }
                </script>
            """, id=r.User.id)
        ] for index, r in enumerate(result)]

        return jsonify({"data": data,
                        "draw": form_data['draw'],
                        "recordsFiltered": total_record,
                        "recordsTotal": total_record}
                       )

    @property
    def qry(self):
        """AkademikPersonel BaseQuery"""
        return DB.session.query(User).options(joinedload(User.roles)). \
            join(Person, Person.user_id == User.id). \
            join(Personel, Personel.person_id == Person.id). \
            join(HitapUnvan, Personel.unvan == HitapUnvan.id).add_columns(
            Person.ad.label("ad"),
            Person.soyad.label("soyad"),
            HitapUnvan.ad.label("unvan_ad")
        )

    @property
    def user_id(self):
        """Kullanici idsi dondurur"""
        return current_user.id

    @login_required
    @auth.requires(Or(Permission(*permission_dict["yonetim"]["yetki_yonetimi"]["rol_atama"]),
                      Role("BAP Admin")),
                   menu_registry={'path': '.yonetim.yetki_yonetimi.rol_atama',
                                  'title': _("Rol Atama")
                                  })
    @route("/", methods=['GET'])
    def kisi_listesi(self):
        """Kisi Listesi Ekrani"""
        roller = [(r.id, r.name) for r in DB.session.query(RoleModel).all() if r.name != "anonymous"]
        rol_atama_form = RolAtamaForm()
        rol_atama_form.roller.choices = roller
        rol_atama_form.process()
        kisi_search_form = KisiSearchForm()

        return render_template("kullanici_rolleri.html",
                               rol_atama_form=rol_atama_form,
                               form=kisi_search_form)

    @login_required
    @auth.requires(Or(Permission(*permission_dict["yonetim"]["yetki_yonetimi"]["rol_atama"]),
                      Role("BAP Admin")))
    @route("/<int:u_id>", methods=["POST"], endpoint="kisi_rol_ata")
    def kisi_rol_ata(self, u_id):
        """Kisi Listesi Ekrani"""

        form = RolAtamaForm(request.form)
        for r in form.roller.data:
            yeni_rol = UserRole(user_id=u_id, role_id=r)
            DB.session.add(yeni_rol)
            DB.session.commit()

        return redirect(url_for('yetki_yonetimi.RolAtamaView:kisi_listesi'))

    @login_required
    @auth.requires(Or(Permission(*permission_dict["yonetim"]["yetki_yonetimi"]["rol_atama"]),
                      Role("BAP Admin")))
    @route('/data', methods=["POST"], endpoint="kisi_rol_search")
    def kisi_arama(self):  # pylint: disable=too-many-branches
        """
        Bap kişilerinde POST ile gelen parametrelere gore arama yapip, sonuclari dondurur.

        Returns:
            http response
        """

        qry = self.qry
        total_record = qry.count()
        form_data = request.form.to_dict()
        search_form = KisiSearchForm(**form_data)

        if not search_form.validate():
            result = qry.offset(form_data['start']).limit(
                form_data['length']).all()
            total_record = qry.count()
            return self.process_data(result, form_data, total_record)

        kisi_ad = search_form.kisi_ad.data
        kisi_soyad = search_form.kisi_soyad.data

        if kisi_ad:
            qry = qry.filter(Person.ad.ilike('%' + kisi_ad + '%'))

        if kisi_soyad:
            qry = qry.filter(Person.soyad.ilike('%' + kisi_soyad + '%'))

        result = qry.offset(form_data['start']).limit(form_data['length']).all()

        return self.process_data(result, form_data, total_record)
