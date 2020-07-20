"""Auth Lib"""
from functools import wraps

from flask import session, current_app, abort, flash, redirect
from flask import request as current_request

from flask_login import current_user, LoginManager, user_unauthorized, make_next_param, \
    login_url as make_login_url
from flask_login.config import USE_SESSION_FOR_NEXT
from flask_login.utils import expand_login_view
from flask_allows.allows import Allows, _make_callable
from flask_allows import Requirement, ConditionalRequirement
from flask_menu.classy import classy_menu_item

from sqlalchemy.exc import IntegrityError, ProgrammingError
from sqlalchemy.orm import joinedload

from zopsedu.app import app
from zopsedu.auth.models.auth import Permission as PermissionModel
from zopsedu.lib.db import DB

# pylint: disable=invalid-name
cache = app.extensions['redis']


# pylint: enable=invalid-name


class ZopseduLoginManager(LoginManager):
    """
    LoginManager for Zopsedu
    """
    def unauthorized(self):
        """
        This is overwrote for Zopsedu
        """
        user_unauthorized.send(current_app._get_current_object()) # pylint: disable=protected-access

        if current_request.headers.environ.get('HTTP_X_REQUESTED_WITH'):
            abort(401)

        if current_request.blueprint in self.blueprint_login_views:
            login_view = self.blueprint_login_views[current_request.blueprint]
        else:
            login_view = self.login_view

        if not login_view:
            abort(401)

        if self.login_message:
            if self.localize_callback is not None:
                flash(self.localize_callback(self.login_message),  # pylint: disable=not-callable
                      category=self.login_message_category)
            else:
                flash(self.login_message, category=self.login_message_category)

        config = current_app.config
        if config.get('USE_SESSION_FOR_NEXT', USE_SESSION_FOR_NEXT):
            login_url = expand_login_view(login_view)
            session['next'] = make_next_param(login_url, current_request.url)
            redirect_url = make_login_url(login_view)
        else:
            redirect_url = make_login_url(login_view, next_url=current_request.url)

        return redirect(redirect_url)


def build_permission_tree(selected_permissions=None):  # pylint:disable=too-many-branches
    """
    [
        {
            "text": "BAP",
            "children": [
                {
                    "text": "Same but with checkboxes",
                    "children": [
                        {
                            "text": "initially selected",
                            "state": { "selected": true }
                        },
                    ]
                }
            ]
        },

    ]

    Returns:
        list: permission tree

    """
    if not selected_permissions:
        selected_permissions = []
    selected_permissions = [(sel_per.group, sel_per.name) for sel_per in selected_permissions]
    gp_tuple = DB.session.query(PermissionModel.group, PermissionModel.name).distinct().all()
    gp_dict = {}
    for group, permission in gp_tuple:
        if group not in gp_dict:
            gp_dict[group] = []
        gp_dict[group].append(permission)

    module_dict = {}
    for key, _ in gp_dict.items():
        keys = key.split('.')
        if len(keys) > 1:
            if keys[0] not in module_dict:
                module_dict[keys[0]] = {keys[1]: gp_dict[key]}
            else:
                module_dict[keys[0]][keys[1]] = gp_dict[key]
        else:
            module_dict[key] = gp_dict[key]

    data = []
    for key, value in module_dict.items():
        module = {
            "text": key,
            "children": [],
        }
        if isinstance(value, dict):
            for _key, _value in value.items():
                group = {
                    "text": _key,
                    "children": [],
                }

                for perm in _value:
                    permission = {
                        "text": perm,
                        "state": {
                            "selected": (".".join([key, _key]), perm) in selected_permissions},
                    }
                    group['children'].append(permission)
                module['children'].append(group)
            data.append(module)
        elif isinstance(value, list):
            for perm in value:
                permission = {
                    "text": perm,
                    "state": {"selected": (key, perm) in selected_permissions},
                }
                module['children'].append(permission)
            data.append(module)

    return data


def identity_loader():
    """Returns current user"""
    return current_user


class Role(Requirement):
    """Rol icin ozel requirement

    Şu şekilde kullanılabilir:
        `allows.requires(Role("Öğretim Üyesi"))`

    """

    def __init__(self, role: object) -> object:
        super().__init__()
        self.role = role

    def fulfill(self, user, request=None):
        """Session rol ile gerekli rolu karsilastirir."""
        user_role = session.get("current_role_name", None)
        # user_role = user.get_role(session['current_role'])
        if not user_role:
            return self.role == 'anonymous'

        return self.role == user_role


class Permission(Requirement):
    """Kendi route permissionlarımızı belirlemek için yazılan custom permission classı"""

    def __init__(self, permission, group, id):
        super().__init__()
        self.permission = permission
        self.group = group
        self.id = id

    def fulfill(self, user, request=None):
        """
        Permissionları kontrol eden metot
        Cache'de yazılı olan rolun permissionlari icerisinde fullfill edilmek istenen permission
        varmı kontrolu yapar. Eger rolun permissionlari redisten beklenmedik bir sekilde silinmis
        ise DB ye gerekli queryi atıp rolun permissionlari cache yazar
        """
        cache = current_app.extensions['redis']
        role_id = session['current_role']
        role_name = session.get("current_role_name", None)
        role_permission_cache_key = current_app.config['ROLES_PERMISSIONS_CACHE_KEY'].format(
            role_id=role_id)

        if not cache.exists(role_permission_cache_key):
            if role_name == 'anonymous':
                """
                anonymous userin permissioni olmadigi icin ROLES_PERMISSION_CACHE_KEY e bos bi 
                deger eklenir. 
                """
                # todo: zaman olmadigi icin incelenemedi
                cache.sadd(role_permission_cache_key, "")
            else:
                from zopsedu.models import Role as RoleModel
                role = DB.session.query(RoleModel).filter(
                    RoleModel.id == role_id).options(joinedload(RoleModel.permissions)).one()
                cache.sadd(role_permission_cache_key, *[perm.name for perm in role.permissions])

        return cache.sismember(
            role_permission_cache_key,
            self.permission
        )

    def __repr__(self):
        return "{}:{}".format(self.group, self.permission)


class AuthRequires(Allows):
    """Extended Allows"""

    # pylint: disable=inconsistent-return-statements
    def requires(self, *requirements, **opts):
        """
        Decorator to enforce requirements on routes

        :param requirements: Collection of requirements to impose on view
        :param throws: Optional, keyword only. Exception to throw for this
            route, if provided it takes precedence over the exception stored
            on the instance
        :param on_fail: Optional, keyword only. Value or function to use as
            the on_fail for this route, takes precedence over the on_fail
            configured on the instance.
        """

        def raiser():
            """Raiser"""
            raise opts.get('throws', self.throws)

        def fail(*args, **kwargs):
            """Fail"""
            func = _make_callable(opts.get('on_fail', self.on_fail))
            res = func(*args, **kwargs)

            if res is not None:
                return res
            raiser()

        def decorator(func):
            """Decorator"""
            perms_groups = []
            reqs = []
            menu = opts.get('menu_registry', None)
            if menu:
                def visible_when():
                    """visible_when callback for menu items"""
                    return self.fulfill(requirements)

                registrar = classy_menu_item(menu.get('path'), menu.get('title'),
                                             order=menu.get('order', 0),
                                             visible_when=visible_when)
                func = registrar(func)

            def get_perms(req):
                """Recursive permission discovery"""
                if isinstance(req, ConditionalRequirement):
                    for requirement in req.requirements:
                        get_perms(requirement)
                elif isinstance(req, Permission):
                    perms_groups.append((req.permission, req.group, req.id))
                    app.logger.info("Function %s decorated for permission: %s ", func.__qualname__,
                                    req.permission)
                else:
                    app.logger.info("Function %s decorated for custom requirement: %s ",
                                    func.__qualname__,
                                    req)

            for req in requirements:
                get_perms(req)
                reqs.append(req)

            endpoint_name = ':'.join(func.__qualname__.split('.'))
            import_path = "{}.{}".format(func.__module__, func.__qualname__)
            if perms_groups:
                perms, _ , _= zip(*perms_groups)
                cache.sadd(app.config['PERMISSIONS_OF_ENDPOINT_CACHE_KEY'].format(
                    endpoint=endpoint_name), *perms)
                cache.sadd(app.config['ALL_PERMISSIONS_CACHE_KEY'], *perms)
                for perm, group,id in set(perms_groups):
                    DB.session.add(PermissionModel(name=perm,
                                                     group=group,
                                                     id=id,
                                                     endpoint_name=endpoint_name))
                    try:
                        DB.session.commit()
                    except IntegrityError:
                        app.logger.error("Permission:[%s] already in DB", perm)
                        DB.session.rollback()
                        DB.session.execute(
                            """SELECT setval(pg_get_serial_sequence('permissions', 'id'),
                             coalesce(max(id),0) + 1, false) FROM permissions;"""
                        )
                    except ProgrammingError:
                        DB.session.rollback()
                        break

                cache.sadd(app.config['ALL_PERMISSIONS_CACHE_KEY'], *perms)

            cache.hset(app.config['ALL_IMPORT_PATH_OF_ENDPOINTS_CACHE_KEY'], endpoint_name,
                       import_path)

            # pylint: disable=no-else-return
            @wraps(func)
            def allower(*args, **kwargs):
                """allower"""
                if self.fulfill(requirements):
                    return func(*args, **kwargs)
                else:
                    return fail(*args, **kwargs)
                # pylint: enable=no-else-return

            return allower

        return decorator
        # pylint: enable=inconsistent-return-statements


# pylint: disable=invalid-name
auth = AuthRequires(identity_loader=identity_loader)
# pylint: enable=invalid-name
