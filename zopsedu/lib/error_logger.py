import json
import traceback

from flask import current_app, request
from flask_login import current_user


class CustomErrorHandler:

    @staticmethod
    def get_request_details():
        """
        request icinden form ve args dictlerini alip serialize edip return eder
        :return: str
        """
        req = request
        # Return the contents as regular dict. If flat is True the returned dict will only have the
        # first item present, if flat is False all values will be returned as lists.
        form_data = {}
        request_args = {}
        if req.form:
            form_data = req.form.to_dict(flat=True)
        if req.args:
            request_args = request.args.to_dict(flat=True)

        return json.dumps({"form_data": form_data,
                           "args": request_args})

    @staticmethod
    def error_handler(hata=None):

        if not hata:
            hata = "{hata}".format(hata=traceback.format_exc())

        current_app.logger.error(hata,
                                 {"url": request.url,
                                  "method": request.method,
                                  "user_id": current_user.id,
                                  "remote_addr": request.remote_addr,
                                  "request_details": CustomErrorHandler.get_request_details()
                                  })
