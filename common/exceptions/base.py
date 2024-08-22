from rest_framework.exceptions import APIException


class CustomAPIException(APIException):
    status_code = 500
    default_detail = ""
    error_code = ""
    detail_format_dic = {
        'status': 500,
        'error_code': '',
        'detail': ''
    }

    def __init__(self, detail=None, error_code=None, status_code=None):
        if not status_code:
            self.detail_format_dic['status'] = self.status_code
        else:
            self.detail_format_dic['status'] = self.status_code = status_code

        if not error_code:
            self.detail_format_dic['error_code'] = self.error_code
        else:
            self.detail_format_dic['error_code'] = error_code

        if not detail:
            self.detail_format_dic['detail'] = self.default_detail
        else:
            self.detail_format_dic['detail'] = detail
        self.detail = self.detail_format_dic
