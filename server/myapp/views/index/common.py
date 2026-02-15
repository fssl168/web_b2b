from django.core.cache import cache
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from myapp.handler import APIResponse
from myapp.models import BasicSite, Category, BasicGlobal
from myapp.serializers import BasicGlobalSerializer, BasicSiteSerializer


def create_nav_item(name, href, type="link", subItems=None):
    """
    创建导航项目的工具函数，减少代码重复
    """
    nav_item = {
        "name": name,
        "href": href,
        "type": type
    }
    if subItems:
        nav_item["subItems"] = subItems
    return nav_item


from django.http import HttpResponse

def simple_test(request):
    """
    简单测试视图函数
    """
    # 直接返回一个简单的响应
    return HttpResponse('Simple test success', content_type='text/plain')

def test(request):
    """
    测试视图函数
    """
    # 打印请求信息
    print(f"Test request received: {request.method} {request.path}")
    print(f"Test request headers: {dict(request.headers)}")
    print(f"Test request params: {dict(request.GET)}")
    
    # 返回一个简单的响应
    return HttpResponse('Test success', content_type='text/plain')

@csrf_exempt
@api_view(['GET'])
def section(request):
    """
    获取导航和页脚数据的接口
    """
    try:
        if request.method == 'GET':
            # 打印请求信息
            print(f"Request received: {request.method} {request.path}")
            print(f"Request headers: {dict(request.headers)}")
            print(f"Request params: {dict(request.GET)}")
            
            # 获取基本站点信息
            basic_site = BasicSite.objects.first() or {}
            basic_site_data = {
                "site_gaid": getattr(basic_site, 'site_gaid', ''),
                "site_logo": getattr(basic_site, 'site_logo', ''),
                "status": getattr(basic_site, 'status', '1')
            }
            
            # 获取全局设置信息
            basic_global = BasicGlobal.objects.first() or {}
            basic_global_data = {
                "global_facebook": getattr(basic_global, 'global_facebook', ''),
                "global_twitter": getattr(basic_global, 'global_twitter', ''),
                "global_instagram": getattr(basic_global, 'global_instagram', ''),
                "global_linkedin": getattr(basic_global, 'global_linkedin', ''),
                "global_youtube": getattr(basic_global, 'global_youtube', ''),
                "global_whatsapp": getattr(basic_global, 'global_whatsapp', ''),
                "global_email": getattr(basic_global, 'global_email', ''),
                "global_phone": getattr(basic_global, 'global_phone', ''),
                "global_address": getattr(basic_global, 'global_address', ''),
                "global_company_name": getattr(basic_global, 'global_company_name', '')
            }
            
            # 获取产品分类数据
            categories = Category.objects.all()
            category_data = [
                {
                    "id": str(category.id),
                    "title": category.title
                }
                for category in categories
            ]
            
            # 构建导航数据
            navigation_items = [
                create_nav_item("首页", "/"),
                create_nav_item("关于我们", "/about"),
                create_nav_item(
                    "产品中心", "/product", "dropdown",
                    [create_nav_item(category.title, f"/product/category/{category.id}") for category in categories]
                ),
                create_nav_item("新闻资讯", "/news"),
                create_nav_item("案例展示", "/case"),
                create_nav_item("常见问题", "/faq"),
                create_nav_item("下载中心", "/download"),
                create_nav_item("联系我们", "/contact")
            ]
            
            # 构建页脚导航数据
            nav_data = [
                create_nav_item("首页", "/"),
                create_nav_item("关于我们", "/about"),
                create_nav_item("产品中心", "/product"),
                create_nav_item("新闻资讯", "/news"),
                create_nav_item("案例展示", "/case"),
                create_nav_item("常见问题", "/faq"),
                create_nav_item("下载中心", "/download"),
                create_nav_item("联系我们", "/contact")
            ]
            
            # 构建响应数据
            data = {
                "basicSite": basic_site_data,
                "basicGlobal": basic_global_data,
                "navigationItems": navigation_items,
                "navData": nav_data,
                "categoryData": category_data,
                "contactData": basic_global_data
            }
            
            response = APIResponse(code=0, msg='查询成功', data=data)
            print(f"Response: {response.data}")
            return response
    except Exception as e:
        print(f"Error in section view: {str(e)}")
        import traceback
        traceback.print_exc()
        return APIResponse(code=1, msg='服务器错误', data={})

