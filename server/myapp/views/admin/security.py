from django.db.models import Q
from rest_framework.decorators import api_view, authentication_classes
from django.utils import timezone
from datetime import datetime, timedelta

from myapp.auth.authentication import AdminTokenAuthtication
from myapp.handler import APIResponse
from myapp.models import ErrorLog
from myapp.permission.permission import check_if_demo


@api_view(['GET'])
@authentication_classes([AdminTokenAuthtication])
@check_if_demo
def list_security_events(request):
    """
    获取安全事件列表
    """
    try:
        if request.method == 'GET':
            # 获取查询参数
            page = int(request.GET.get('page', 1))
            page_size = int(request.GET.get('page_size', 10))
            search = request.GET.get('search', '')
            start_date = request.GET.get('start_date', '')
            end_date = request.GET.get('end_date', '')
            incident_type = request.GET.get('incident_type', '')
            incident_level = request.GET.get('incident_level', '')

            # 构建查询条件
            query = Q()

            if search:
                query &= Q(url__icontains=search) | Q(ip__icontains=search) | Q(content__icontains=search)

            if start_date:
                try:
                    start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
                    query &= Q(log_time__gte=start_datetime)
                except ValueError:
                    pass

            if end_date:
                try:
                    end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
                    # 将结束时间设置为当天的23:59:59
                    end_datetime = end_datetime.replace(hour=23, minute=59, second=59)
                    query &= Q(log_time__lte=end_datetime)
                except ValueError:
                    pass

            if incident_type:
                query &= Q(method=incident_type)

            if incident_level:
                query &= Q(content__icontains=f'Level: {incident_level}')

            # 查询数据
            error_logs = ErrorLog.objects.filter(query).order_by('-log_time')

            # 计算总数
            total = error_logs.count()

            # 分页
            start = (page - 1) * page_size
            end = start + page_size
            error_logs = error_logs[start:end]

            # 构建响应数据
            data_list = []
            for log in error_logs:
                # 提取事件级别
                level = 'MEDIUM'  # 默认级别
                content = log.content
                if 'Level: ' in content:
                    level_start = content.find('Level: ') + len('Level: ')
                    level_end = content.find(' - ', level_start)
                    if level_end != -1:
                        level = content[level_start:level_end].strip()

                data_list.append({
                    'id': log.id,
                    'method': log.method,
                    'level': level,
                    'url': log.url,
                    'ip': log.ip,
                    'log_time': log.log_time,
                    'content': content
                })

            data = {
                'list': data_list,
                'total': total,
                'page': page,
                'page_size': page_size
            }

            return APIResponse(code=0, msg='查询成功', data=data)
    except Exception as e:
        print(f"Error in list_security_events: {str(e)}")
        return APIResponse(code=1, msg='服务器错误', data={})


@api_view(['GET'])
@authentication_classes([AdminTokenAuthtication])
@check_if_demo
def get_security_stats(request):
    """
    获取安全事件统计数据
    """
    try:
        if request.method == 'GET':
            # 获取今天的开始时间
            today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

            # 统计总事件数
            total_incidents = ErrorLog.objects.count()

            # 统计高级事件数（HIGH级别）
            high_level_incidents = ErrorLog.objects.filter(content__icontains='Level: HIGH').count()

            # 统计严重事件数（CRITICAL级别）
            critical_incidents = ErrorLog.objects.filter(content__icontains='Level: CRITICAL').count()

            # 统计今日事件数
            today_incidents = ErrorLog.objects.filter(log_time__gte=today_start).count()

            # 构建响应数据
            data = {
                'totalIncidents': total_incidents,
                'highLevelIncidents': high_level_incidents,
                'criticalIncidents': critical_incidents,
                'todayIncidents': today_incidents
            }

            return APIResponse(code=0, msg='查询成功', data=data)
    except Exception as e:
        print(f"Error in get_security_stats: {str(e)}")
        return APIResponse(code=1, msg='服务器错误', data={})


@api_view(['GET'])
@authentication_classes([AdminTokenAuthtication])
@check_if_demo
def get_security_report(request):
    """
    获取安全事件报告
    """
    try:
        if request.method == 'GET':
            # 获取查询参数
            days = int(request.GET.get('days', 7))

            # 计算开始时间
            start_date = timezone.now() - timedelta(days=days)

            # 查询时间范围内的事件
            error_logs = ErrorLog.objects.filter(log_time__gte=start_date).order_by('log_time')

            # 按日期分组统计
            daily_stats = {}
            for log in error_logs:
                date_key = log.log_time.strftime('%Y-%m-%d')
                if date_key not in daily_stats:
                    daily_stats[date_key] = {
                        'total': 0,
                        'low': 0,
                        'medium': 0,
                        'high': 0,
                        'critical': 0
                    }

                daily_stats[date_key]['total'] += 1

                # 提取事件级别
                content = log.content
                if 'Level: LOW' in content:
                    daily_stats[date_key]['low'] += 1
                elif 'Level: MEDIUM' in content:
                    daily_stats[date_key]['medium'] += 1
                elif 'Level: HIGH' in content:
                    daily_stats[date_key]['high'] += 1
                elif 'Level: CRITICAL' in content:
                    daily_stats[date_key]['critical'] += 1

            # 构建响应数据
            data = {
                'startDate': start_date.strftime('%Y-%m-%d'),
                'endDate': timezone.now().strftime('%Y-%m-%d'),
                'totalEvents': error_logs.count(),
                'dailyStats': daily_stats
            }

            return APIResponse(code=0, msg='查询成功', data=data)
    except Exception as e:
        print(f"Error in get_security_report: {str(e)}")
        return APIResponse(code=1, msg='服务器错误', data={})
