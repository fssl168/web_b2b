# Create your views here.
from datetime import timedelta

from django.db.models import Count
from django.utils import timezone
from rest_framework.decorators import api_view, authentication_classes

from myapp.auth.authentication import AdminTokenAuthtication
from myapp.handler import APIResponse
from myapp.models import OpLog, Inquiry, Thing, News, Case


@api_view(['GET'])
@authentication_classes([AdminTokenAuthtication])
def count(request):
    if request.method == 'GET':
        days = request.GET.get('days', 7)

        # 计算day之前的时间
        days_ago = timezone.now() - timedelta(days=int(days))

        # 使用 Django ORM 查询
        results = (
            OpLog.objects.filter(re_time__gte=days_ago)
            .extra({'day': 'DATE(re_time)'})  # 使用 extra() 将日期提取为 'day'
            .values('day')  # 提取日期
            .annotate(pv=Count('id'), uv=Count('re_ip', distinct=True))  # 统计总 PV 和唯一 UV
            .order_by('day')  # 按日期排序
        )

        results_dict = [
            dict(day=row['day'], pv=row['pv'], uv=row['uv']) for row in
            results]

        data = {
            'visit_data': results_dict
        }
        return APIResponse(code=0, msg='查询成功', data=data)


@api_view(['GET'])
@authentication_classes([AdminTokenAuthtication])
def dataCount(request):
    if request.method == 'GET':
        today = timezone.now().date()

        # 使用 annotate 和 aggregate 一次性获取所有统计数据
        inquiry_count = Inquiry.objects.filter(create_time__date=today).count()
        visit_count = (
            OpLog.objects.filter(re_time__date=today)
            .values('re_ip')
            .distinct()
            .count()
        )

        # 使用 aggregate 获取其他统计值
        total_counts = Thing.objects.aggregate(product_count=Count('id'))  # Things 的产品数
        news_counts = News.objects.aggregate(news_count=Count('id'))  # 新闻数
        case_counts = Case.objects.aggregate(case_count=Count('id'))  # 案例数

        data = {
            'inquiry_count': inquiry_count,
            'visit_count': visit_count,
            'product_count': total_counts['product_count'],
            'news_count': news_counts['news_count'],
            'case_count': case_counts['case_count'],
        }

        return APIResponse(code=0, msg='查询成功', data=data)
