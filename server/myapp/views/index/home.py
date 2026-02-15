# Create your views here.

from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from django.core.cache import cache

from myapp import utils
from myapp.handler import APIResponse
from myapp.models import Category, Thing, BasicTdk, BasicBanner, BasicAdditional, BasicGlobal, Comment, News, BasicSite
from myapp.serializers import ThingSerializer, CategorySerializer, ListThingSerializer, BasicGlobalSerializer, \
    CommentSerializer, NewsSerializer, NewsListSerializer, NormalCategorySerializer, BasicSiteSerializer


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
            'seo_title': basicTdk.tdk_home_title,
            'seo_description': basicTdk.tdk_home_description,
            'seo_keywords': basicTdk.tdk_home_keywords,
        }

        # banner数据
        basicBanner = BasicBanner.get_solo()
        sectionData['bannerData'] = basicBanner.banner_home

        # 分类数据
        categories = Category.objects.filter(pid=-1).order_by('sort', '-id')
        categorySerializer = NormalCategorySerializer(categories, many=True)
        sectionData['categoryData'] = categorySerializer.data

        # 精选产品
        featuredThings = Thing.objects.filter(status=0, dimension__icontains="Feature").order_by('-create_time')[:8]
        thingSerializer = ListThingSerializer(featuredThings, many=True)
        sectionData['featuredData'] = thingSerializer.data

        # about us
        basicAdditional = BasicAdditional.get_solo()
        sectionData['aboutData'] = {
            'aboutText': basicAdditional.additional_about,
            'aboutCover': basicAdditional.global_addition_about_image,
        }
        basicGlobal = BasicGlobal.get_solo()
        basicGlobalSerializer = BasicGlobalSerializer(basicGlobal, many=False)
        sectionData['companyName'] = basicGlobalSerializer.data['global_company_name']

        basicSite = BasicSite.get_solo()
        basicSiteSerializer = BasicSiteSerializer(basicSite, many=False)
        sectionData['siteName'] = basicSiteSerializer.data['site_name']

        # stats
        sectionData['statsData'] = {
            'param_one_name': basicAdditional.param_one_name,
            'param_one_value': basicAdditional.param_one_value,
            'param_two_name': basicAdditional.param_two_name,
            'param_two_value': basicAdditional.param_two_value,
            'param_three_name': basicAdditional.param_three_name,
            'param_three_value': basicAdditional.param_three_value,
            'param_four_name': basicAdditional.param_four_name,
            'param_four_value': basicAdditional.param_four_value,
        }

        # hero文案
        sectionData['heroText'] = basicAdditional.ext01

        # 客评
        comments = Comment.objects.all()[:4]
        commentSerializer = CommentSerializer(comments, many=True)
        sectionData['commentData'] = commentSerializer.data

        # news
        news = News.objects.all()[:3]
        newsSerializer = NewsListSerializer(news, many=True)
        sectionData['newsData'] = newsSerializer.data

        # 联系底图
        sectionData['contactData'] = basicAdditional.global_addition_contact_image

        # 缓存数据
        cache.set(cache_key, sectionData, 3600)  # 缓存3600秒

        return APIResponse(code=0, msg='查询成功', data=sectionData)
