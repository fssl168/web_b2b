from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny

from myapp import utils
from myapp.handler import APIResponse
from myapp.models import BasicSite, Category, BasicGlobal, BasicBanner, Thing, Faq, Case, BasicTdk
from myapp.serializers import CategorySerializer, BasicGlobalSerializer, ThingSerializer, FaqSerializer, CaseSerializer, \
    NormalCategorySerializer, ListThingSerializer, BasicSiteSerializer


class MyPageNumberPagination(PageNumberPagination):
    page_size = 9  # 每页的默认项
    page_size_query_param = 'pageSize'  # 允许通过 URL 参数设置每页的大小
    max_page_size = 100  # 最大页尺寸


@api_view(['GET'])
@permission_classes([AllowAny])
def section(request):
    if request.method == 'GET':
        sectionData = {}

        # seo数据
        basicTdk = BasicTdk.get_solo()
        if basicTdk:
            sectionData['seoData'] = {
                'seo_title': basicTdk.tdk_case_title,
                'seo_description': basicTdk.tdk_case_description,
                'seo_keywords': basicTdk.tdk_case_keywords,
            }
        else:
            sectionData['seoData'] = {
                'seo_title': 'Case',
                'seo_description': 'Case',
                'seo_keywords': 'Case',
            }

        # siteName
        basicSite = BasicSite.get_solo()
        if basicSite:
            basicSiteSerializer = BasicSiteSerializer(basicSite, many=False)
            sectionData['siteName'] = basicSiteSerializer.data.get('site_name', 'B2B外贸演示站')
        else:
            sectionData['siteName'] = 'B2B外贸演示站'

        # banner数据
        basicBanner = BasicBanner.get_solo()
        sectionData['bannerData'] = basicBanner.banner_case if basicBanner else ''

        # 分页列表
        cases = Case.objects.all().order_by('-create_time')
        paginator = MyPageNumberPagination()
        paginated_list = paginator.paginate_queryset(cases, request)
        total = cases.count()

        caseSerializer = CaseSerializer(paginated_list, many=True)
        sectionData['caseData'] = caseSerializer.data
        sectionData['total'] = total

        return APIResponse(code=0, msg='查询成功', data=sectionData)


@api_view(['GET'])
@permission_classes([AllowAny])
def detail(request):
    data = {}
    try:
        pk = request.GET.get('id', -1)
        case = Case.objects.get(pk=pk)
    except Case.DoesNotExist:
        utils.log_error(request, '对象不存在')
        return APIResponse(code=1, msg='对象不存在')

    if request.method == 'GET':
        serializer = CaseSerializer(case)

        # 详情数据
        data['detailData'] = serializer.data

        # 推荐产品
        things = Thing.objects.filter(status=0, dimension__icontains="Recommend").order_by('-create_time')[:4]
        thingSerializer = ListThingSerializer(things, many=True)
        data['recommendData'] = thingSerializer.data

        # 产品分类
        categories = Category.objects.filter(pid=-1).order_by('sort', '-id')
        categorySerializer = NormalCategorySerializer(categories, many=True)
        data['categoryData'] = categorySerializer.data

        return APIResponse(code=0, msg='查询成功', data=data)
