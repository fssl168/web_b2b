import json
from django.db.models import Q
from rest_framework.decorators import api_view, authentication_classes
from django.utils import timezone
from datetime import datetime, timedelta

from myapp.auth.authentication import AdminTokenAuthtication
from myapp.handler import APIResponse
from myapp.models import SecurityEvent
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
                query &= Q(description__icontains=search) | Q(ip__icontains=search) | Q(username__icontains=search)

            if start_date:
                try:
                    start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
                    query &= Q(create_time__gte=start_datetime)
                except ValueError:
                    pass

            if end_date:
                try:
                    end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
                    # 将结束时间设置为当天的23:59:59
                    end_datetime = end_datetime.replace(hour=23, minute=59, second=59)
                    query &= Q(create_time__lte=end_datetime)
                except ValueError:
                    pass

            if incident_type:
                query &= Q(incident_type=incident_type)

            if incident_level:
                query &= Q(level=incident_level)

            # 查询数据
            security_events = SecurityEvent.objects.filter(query).order_by('-create_time')

            # 计算总数
            total = security_events.count()

            # 分页
            start = (page - 1) * page_size
            end = start + page_size
            security_events = security_events[start:end]

            # 构建响应数据
            data_list = []
            for event in security_events:
                data_list.append({
                    'id': event.id,
                    'incident_type': event.incident_type,
                    'incident_type_display': event.get_incident_type_display(),
                    'level': event.level,
                    'level_display': event.get_level_display(),
                    'description': event.description,
                    'username': event.username,
                    'ip': event.ip,
                    'user_agent': event.user_agent,
                    'request_url': event.request_url,
                    'request_method': event.request_method,
                    'response_status': event.response_status,
                    'is_resolved': event.is_resolved,
                    'create_time': event.create_time.strftime('%Y-%m-%d %H:%M:%S') if event.create_time else '',
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
            total_incidents = SecurityEvent.objects.count()

            # 统计高级事件数（HIGH级别）
            high_level_incidents = SecurityEvent.objects.filter(level='HIGH').count()

            # 统计严重事件数（CRITICAL级别）
            critical_incidents = SecurityEvent.objects.filter(level='CRITICAL').count()

            # 统计今日事件数
            today_incidents = SecurityEvent.objects.filter(create_time__gte=today_start).count()

            # 统计各级别事件数
            low_incidents = SecurityEvent.objects.filter(level='LOW').count()
            medium_incidents = SecurityEvent.objects.filter(level='MEDIUM').count()

            # 统计各类型事件数
            type_stats = {}
            for event_type in SecurityEvent.TYPE_CHOICES:
                type_stats[event_type[0]] = SecurityEvent.objects.filter(incident_type=event_type[0]).count()

            # 构建响应数据
            data = {
                'totalIncidents': total_incidents,
                'highLevelIncidents': high_level_incidents,
                'criticalIncidents': critical_incidents,
                'todayIncidents': today_incidents,
                'lowIncidents': low_incidents,
                'mediumIncidents': medium_incidents,
                'typeStats': type_stats
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
            security_events = SecurityEvent.objects.filter(create_time__gte=start_date).order_by('create_time')

            # 按日期分组统计
            daily_stats = {}
            for event in security_events:
                date_key = event.create_time.strftime('%Y-%m-%d')
                if date_key not in daily_stats:
                    daily_stats[date_key] = {
                        'total': 0,
                        'low': 0,
                        'medium': 0,
                        'high': 0,
                        'critical': 0
                    }

                daily_stats[date_key]['total'] += 1

                # 根据事件级别统计
                if event.level == 'LOW':
                    daily_stats[date_key]['low'] += 1
                elif event.level == 'MEDIUM':
                    daily_stats[date_key]['medium'] += 1
                elif event.level == 'HIGH':
                    daily_stats[date_key]['high'] += 1
                elif event.level == 'CRITICAL':
                    daily_stats[date_key]['critical'] += 1

            # 按事件类型统计
            type_stats = {}
            for event in security_events:
                event_type = event.incident_type
                if event_type not in type_stats:
                    type_stats[event_type] = 0
                type_stats[event_type] += 1

            # 构建响应数据
            data = {
                'startDate': start_date.strftime('%Y-%m-%d'),
                'endDate': timezone.now().strftime('%Y-%m-%d'),
                'totalEvents': security_events.count(),
                'dailyStats': daily_stats,
                'typeStats': type_stats
            }

            return APIResponse(code=0, msg='查询成功', data=data)
    except Exception as e:
        print(f"Error in get_security_report: {str(e)}")
        return APIResponse(code=1, msg='服务器错误', data={})
