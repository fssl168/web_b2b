from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from myapp.handler import APIResponse
from myapp.models import BasicSite, Category, BasicGlobal, BasicBanner, Thing, BasicTdk
from myapp.serializers import CategorySerializer, BasicGlobalSerializer, ThingSerializer, ListThingSerializer, \
    BasicSiteSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def section(request):
    if request.method == 'GET':

        # 使用请求相关缓存键
        cache_key = f"section_view:{request.get_full_path()}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return APIResponse(code=0, msg='查询成功', data=cached_data)

        sectionData = {}

        # seo数据
        basicTdk = BasicTdk.get_solo()
        sectionData['seoData'] = {
            'seo_title': basicTdk.tdk_contact_title,
            'seo_description': basicTdk.tdk_contact_description,
            'seo_keywords': basicTdk.tdk_contact_keywords,
        }

        # banner数据
        basicBanner = BasicBanner.get_solo()
        sectionData['bannerData'] = basicBanner.banner_contact

        # 联系信息
        basicGlobal = BasicGlobal.get_solo()
        basicGlobalSerializer = BasicGlobalSerializer(basicGlobal, many=False)
        sectionData['contactData'] = basicGlobalSerializer.data

        # 推荐数据
        things = Thing.objects.filter(status=0, dimension__icontains="Recommend").order_by('-create_time')[:4]
        thingSerializer = ListThingSerializer(things, many=True)
        sectionData['recommendData'] = thingSerializer.data

        basicSite = BasicSite.get_solo()
        basicSiteSerializer = BasicSiteSerializer(basicSite, many=False)
        sectionData['siteName'] = basicSiteSerializer.data['site_name']

        # 缓存数据
        cache.set(cache_key, sectionData, 3600)  # 缓存3600秒

        return APIResponse(code=0, msg='查询成功', data=sectionData)
