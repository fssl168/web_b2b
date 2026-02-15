from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

from myapp.handler import APIResponse
from myapp.models import BasicSite, Category, BasicGlobal, BasicBanner, Thing, Faq, Download, BasicTdk
from myapp.serializers import CategorySerializer, BasicGlobalSerializer, ThingSerializer, FaqSerializer, \
    DownloadSerializer, BasicSiteSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def section(request):
    if request.method == 'GET':
        sectionData = {}

        # seo数据
        basicTdk = BasicTdk.get_solo()
        sectionData['seoData'] = {
            'seo_title': basicTdk.tdk_download_title,
            'seo_description': basicTdk.tdk_download_description,
            'seo_keywords': basicTdk.tdk_download_keywords,
        }

        # siteName
        basicSite = BasicSite.get_solo()
        basicSiteSerializer = BasicSiteSerializer(basicSite, many=False)
        sectionData['siteName'] = basicSiteSerializer.data['site_name']

        # banner数据
        basicBanner = BasicBanner.get_solo()
        sectionData['bannerData'] = basicBanner.banner_download

        # download列表
        downloads = Download.objects.all().order_by('-create_time')
        downloadSerializer = DownloadSerializer(downloads, many=True)
        sectionData['downloadData'] = downloadSerializer.data

        return APIResponse(code=0, msg='查询成功', data=sectionData)
