# Create your views here.

from rest_framework.decorators import api_view, authentication_classes
from rest_framework.pagination import PageNumberPagination

from myapp import utils
from myapp.auth.authentication import AdminTokenAuthtication
from myapp.handler import APIResponse
from myapp.models import Category, Thing
from myapp.permission.permission import isDemoAdminUser, check_if_demo
from myapp.serializers import ThingSerializer, UpdateThingSerializer
from myapp.utils import after_call, clear_cache


class MyPageNumberPagination(PageNumberPagination):
    page_size = 10  # 每页的默认项
    page_size_query_param = 'pageSize'  # 允许通过 URL 参数设置每页的大小
    max_page_size = 100  # 最大页尺寸


@api_view(['GET'])
@authentication_classes([AdminTokenAuthtication])
def list_api(request):
    if request.method == 'GET':
        keyword = request.GET.get("keyword", None)
        c = request.GET.get("c", None)
        if keyword:
            things = Thing.objects.filter(title__contains=keyword).order_by('-create_time')
        elif c:
            category = Category.objects.get(pk=c)
            things = category.category_thing.all()
        else:
            things = Thing.objects.all().order_by('-create_time')

        # 分页
        paginator = MyPageNumberPagination()
        paginated_things = paginator.paginate_queryset(things, request)
        total = things.count()

        serializer = ThingSerializer(paginated_things, many=True)
        return APIResponse(code=0, msg='查询成功', data=serializer.data, total=total)


@api_view(['GET'])
@authentication_classes([AdminTokenAuthtication])
def detail(request):
    try:
        pk = request.GET.get('id', -1)
        thing = Thing.objects.get(pk=pk)
    except Thing.DoesNotExist:
        utils.log_error(request, '对象不存在')
        return APIResponse(code=0, msg='对象不存在')

    if request.method == 'GET':
        serializer = ThingSerializer(thing)
        return APIResponse(code=0, msg='查询成功', data=serializer.data)


@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
@check_if_demo
@after_call(clear_cache)
def create(request):

    serializer = ThingSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return APIResponse(code=0, msg='创建成功', data=serializer.data)
    else:
        print(serializer.errors)
        utils.log_error(request, '参数错误')

    return APIResponse(code=1, msg='创建失败')


@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
@check_if_demo
@after_call(clear_cache)
def update(request):

    try:
        pk = request.data['id']
        thing = Thing.objects.get(pk=pk)
    except Thing.DoesNotExist:
        return APIResponse(code=1, msg='对象不存在')

    serializer = UpdateThingSerializer(thing, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return APIResponse(code=0, msg='查询成功', data=serializer.data)
    else:
        print(serializer.errors)
        utils.log_error(request, '参数错误')

    return APIResponse(code=1, msg='更新失败')


@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
@check_if_demo
@after_call(clear_cache)
def delete(request):

    try:
        ids = request.data['ids']
        ids_arr = ids.split(',')
        Thing.objects.filter(id__in=ids_arr).delete()
    except Thing.DoesNotExist:
        return APIResponse(code=1, msg='对象不存在')
    return APIResponse(code=0, msg='删除成功')
