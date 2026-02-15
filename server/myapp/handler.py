from rest_framework.response import Response


class APIResponse(Response):
    def __init__(self, code=0, msg='', data=None, total=0, status=200, headers=None, content_type='application/json; charset=utf-8', **kwargs):
        dic = {'code': code, 'msg': msg, 'total': total}
        if data is not None:
            dic['data'] = data

        dic.update(kwargs)  # 这里使用update
        super().__init__(data=dic, status=status,
                         template_name=None, headers=headers,
                         exception=False, content_type=content_type)
