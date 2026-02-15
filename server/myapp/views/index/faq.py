from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from myapp.handler import APIResponse
from myapp.models import BasicSite, Category, BasicGlobal, BasicBanner, Thing, Faq, BasicTdk
from myapp.serializers import CategorySerializer, BasicGlobalSerializer, ThingSerializer, FaqSerializer, \
    BasicSiteSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def section(request):
    if request.method == 'GET':
        sectionData = {}

        # seo数据
        basicTdk = BasicTdk.get_solo()
        sectionData['seoData'] = {
            'seo_title': basicTdk.tdk_faq_title,
            'seo_description': basicTdk.tdk_faq_description,
            'seo_keywords': basicTdk.tdk_faq_keywords,
        }

        # siteName
        basicSite = BasicSite.get_solo()
        basicSiteSerializer = BasicSiteSerializer(basicSite, many=False)
        sectionData['siteName'] = basicSiteSerializer.data['site_name']

        # banner数据
        basicBanner = BasicBanner.get_solo()
        sectionData['bannerData'] = basicBanner.banner_faq

        # faq列表
        faqs = Faq.objects.all().order_by('-create_time')
        faqSerializer = FaqSerializer(faqs, many=True)
        sectionData['faqData'] = faqSerializer.data

        return APIResponse(code=0, msg='查询成功', data=sectionData)
