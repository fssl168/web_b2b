import os
from pathlib import Path

from django.core.files.storage import default_storage
from django.http import JsonResponse
from rest_framework.decorators import api_view, authentication_classes

from myapp import utils
from myapp.auth.authentication import AdminTokenAuthtication
from myapp.handler import APIResponse
from myapp.permission.permission import check_if_demo, isDemoAdminUser
from server.settings import MEDIA_ROOT, BASE_HOST_URL, CDN_IMAGE_UPLOAD_SIZE, CDN_VIDEO_UPLOAD_SIZE, \
    CDN_FILE_UPLOAD_SIZE

# 尝试导入magic库，如果失败则设置为None
try:
    import magic
    has_magic = True
except ImportError:
    magic = None
    has_magic = False


def validate_file_content(file, expected_types):
    """
    验证文件内容是否符合预期类型
    """
    try:
        if not has_magic:
            # 如果没有magic库，跳过文件内容验证
            return True
        
        # 重置文件指针到开头
        file.seek(0)
        # 使用python-magic库检测文件类型
        mime = magic.Magic(mime=True)
        file_type = mime.from_buffer(file.read(2048))
        # 重置文件指针到开头
        file.seek(0)
        
        return any(expected in file_type for expected in expected_types)
    except:
        # 如果无法检测文件类型，返回False
        return False


def set_file_permissions(file_path):
    """
    设置文件权限，确保文件只能被授权访问
    """
    try:
        # 设置文件权限为644（所有者可读写，其他人可读）
        os.chmod(file_path, 0o644)
        return True
    except:
        return False


# 用于上传Logo图片
@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
@check_if_demo
def upload_logo_img(request):
    if request.method == 'POST':
        # 确保存在文件
        myfile = request.FILES.get('my-file')
        if not myfile:
            return JsonResponse({"code": 1, "message": "请选择要上传的文件"}, status=400)

        # 文件类型和大小验证
        max_size = CDN_IMAGE_UPLOAD_SIZE
        valid_extensions = ['.png']  # 允许的文件扩展名
        expected_mime_types = ['image/png']  # 预期的MIME类型

        if myfile.size > max_size:
            return JsonResponse({"code": 1, "message": f"文件太大，需小于{max_size/(1024*1024):.1f}MB"})

        file_extension = Path(myfile.name).suffix.lower()
        if file_extension not in valid_extensions:
            return JsonResponse({"code": 1, "message": f"仅支持{', '.join(valid_extensions)}格式的文件"})

        # 验证文件内容
        if not validate_file_content(myfile, expected_mime_types):
            return JsonResponse({"code": 1, "message": "文件内容不符合要求"})

        # 生成新文件名
        new_name = "logo.png"

        # 保存文件
        try:
            # 使用 Django 的默认存储来保存文件
            relative_path = os.path.join('img', new_name)
            # 如果目标文件已存在，先删除
            if default_storage.exists(relative_path):
                default_storage.delete(relative_path)
            # 执行保存
            default_storage.save(relative_path, myfile)

            # 设置文件权限
            absolute_path = os.path.join(MEDIA_ROOT, relative_path)
            set_file_permissions(absolute_path)

            return JsonResponse({"code": 0, "data": new_name})

        except Exception as e:
            return JsonResponse({"code": 1, "message": f"文件保存失败: {str(e)}"})

    return JsonResponse({"code": 1, "message": "请求方法错误"})


# 用于上传Ico图片
@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
@check_if_demo
def upload_ico_img(request):
    if request.method == 'POST':
        # 确保存在文件
        myfile = request.FILES.get('my-file')
        if not myfile:
            return JsonResponse({"code": 1, "message": "请选择要上传的文件"}, status=400)

        # 文件类型和大小验证
        max_size = CDN_IMAGE_UPLOAD_SIZE
        valid_extensions = ['.ico']  # 允许的文件扩展名
        expected_mime_types = ['image/x-icon']  # 预期的MIME类型

        if myfile.size > max_size:
            return JsonResponse({"code": 1, "message": f"文件太大，需小于{max_size/(1024*1024):.1f}MB"})

        file_extension = Path(myfile.name).suffix.lower()
        if file_extension not in valid_extensions:
            return JsonResponse({"code": 1, "message": f"仅支持{', '.join(valid_extensions)}格式的文件"})

        # 验证文件内容
        if not validate_file_content(myfile, expected_mime_types):
            return JsonResponse({"code": 1, "message": "文件内容不符合要求"})

        # 生成新文件名
        new_name = "favicon.ico"

        # 保存文件
        try:
            # 使用 Django 的默认存储来保存文件
            relative_path = os.path.join('img', new_name)
            # 如果目标文件已存在，先删除
            if default_storage.exists(relative_path):
                default_storage.delete(relative_path)
            # 执行保存
            default_storage.save(relative_path, myfile)

            # 设置文件权限
            absolute_path = os.path.join(MEDIA_ROOT, relative_path)
            set_file_permissions(absolute_path)

            return JsonResponse({"code": 0, "data": new_name})

        except Exception as e:
            return JsonResponse({"code": 1, "message": f"文件保存失败: {str(e)}"})

    return JsonResponse({"code": 1, "message": "请求方法错误"})


# 用于普通上传图片
@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
@check_if_demo
def upload_img(request):
    if request.method == 'POST':
        # 确保存在文件
        myfile = request.FILES.get('my-file')
        if not myfile:
            return JsonResponse({"code": 1, "message": "请选择要上传的文件"}, status=400)

        # 文件类型和大小验证
        max_size = CDN_IMAGE_UPLOAD_SIZE
        valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.ico']  # 允许的文件扩展名
        expected_mime_types = ['image/jpeg', 'image/png', 'image/gif', 'image/x-icon']  # 预期的MIME类型

        if myfile.size > max_size:
            return JsonResponse({"code": 1, "message": f"文件太大，需小于{max_size/(1024*1024):.1f}MB"})

        file_extension = Path(myfile.name).suffix.lower()
        if file_extension not in valid_extensions:
            return JsonResponse({"code": 1, "message": f"仅支持{', '.join(valid_extensions)}格式的文件"})

        # 验证文件内容
        if not validate_file_content(myfile, expected_mime_types):
            return JsonResponse({"code": 1, "message": "文件内容不符合要求"})

        # 生成新文件名
        new_name = f"{utils.get_timestamp()}{file_extension}"

        # 保存文件
        try:
            # 使用 Django 的默认存储来保存文件
            relative_path = os.path.join('img', new_name)
            default_storage.save(relative_path, myfile)

            # 设置文件权限
            absolute_path = os.path.join(MEDIA_ROOT, relative_path)
            set_file_permissions(absolute_path)

            return JsonResponse({"code": 0, "data": new_name})

        except Exception as e:
            return JsonResponse({"code": 1, "message": f"文件保存失败: {str(e)}"})

    return JsonResponse({"code": 1, "message": "请求方法错误"})


# 用于普通上传文件（下载管理）
@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
@check_if_demo
def upload_normal_file(request):
    if request.method == 'POST':
        # 确保存在文件
        myfile = request.FILES.get('my-file')
        if not myfile:
            return JsonResponse({"code": 1, "message": "请选择要上传的文件"}, status=400)

        # 文件类型和大小验证
        max_size = CDN_FILE_UPLOAD_SIZE
        valid_extensions = ['.jpg', '.jpeg', '.png', '.docx', '.pdf', '.zip', '.rar']  # 允许的文件扩展名
        expected_mime_types = ['image/jpeg', 'image/png', 'application/msword', 'application/pdf', 'application/zip', 'application/x-rar-compressed']  # 预期的MIME类型

        if myfile.size > max_size:
            return JsonResponse({"code": 1, "message": f"文件太大，需小于{max_size/(1024*1024):.1f}MB"})

        file_extension = Path(myfile.name).suffix.lower()
        if file_extension not in valid_extensions:
            return JsonResponse({"code": 1, "message": f"仅支持{', '.join(valid_extensions)}格式的文件"})

        # 验证文件内容
        if not validate_file_content(myfile, expected_mime_types):
            return JsonResponse({"code": 1, "message": "文件内容不符合要求"})

        # 生成新文件名
        new_name = f"{utils.get_timestamp()}{file_extension}"

        # 保存文件
        try:
            # 使用 Django 的默认存储来保存文件
            relative_path = os.path.join('file', new_name)
            default_storage.save(relative_path, myfile)

            # 设置文件权限
            absolute_path = os.path.join(MEDIA_ROOT, relative_path)
            set_file_permissions(absolute_path)

            return JsonResponse({"code": 0, "data": new_name})

        except Exception as e:
            return JsonResponse({"code": 1, "message": f"文件保存失败: {str(e)}"})

    return JsonResponse({"code": 1, "message": "请求方法错误"})


# 用于富文本上传文件
@api_view(['POST'])
@authentication_classes([AdminTokenAuthtication])
def upload_file(request):
    if request.method == 'POST':
        # 特殊情况 (需返回特殊json)
        if isDemoAdminUser(request):
            return JsonResponse({"errno": 1, "message": "演示账号无法操作"})

        # 确保存在文件
        myfile = request.FILES.get('my-file')
        if not myfile:
            return JsonResponse({"errno": 1, "message": "请选择要上传的文件"}, status=400)

        file_extension = Path(myfile.name).suffix.lower()

        # 定义文件类型和大小限制
        video_extensions = ['.mp4']
        image_extensions = ['.jpeg', '.jpg', '.png']
        expected_image_mime_types = ['image/jpeg', 'image/png']
        expected_video_mime_types = ['video/mp4']

        if file_extension in image_extensions:
            max_size = CDN_IMAGE_UPLOAD_SIZE
            if myfile.size > max_size:
                return JsonResponse({"errno": 1, "message": f"图片太大，需小于{max_size/(1024*1024):.1f}MB"})

            # 验证文件内容
            if not validate_file_content(myfile, expected_image_mime_types):
                return JsonResponse({"errno": 1, "message": "文件内容不符合要求"})

        elif file_extension in video_extensions:
            max_size = CDN_VIDEO_UPLOAD_SIZE
            if myfile.size > max_size:
                return JsonResponse({"errno": 1, "message": f"视频太大，需小于{max_size/(1024*1024):.1f}MB"})

            # 验证文件内容
            if not validate_file_content(myfile, expected_video_mime_types):
                return JsonResponse({"errno": 1, "message": "文件内容不符合要求"})

        if file_extension not in image_extensions and file_extension not in video_extensions:
            return JsonResponse({"errno": 1, "message": f"仅支持{', '.join(image_extensions + video_extensions)}格式的文件"})

        # 生成新文件名
        new_name = f"{utils.get_timestamp()}{file_extension}"

        # 保存文件
        try:
            # 使用 Django 的默认存储来保存文件
            relative_path = os.path.join('file', new_name)
            default_storage.save(relative_path, myfile)

            # 设置文件权限
            absolute_path = os.path.join(MEDIA_ROOT, relative_path)
            set_file_permissions(absolute_path)

            resp_json = {
                "errno": 0,
                "data": {
                    "url": BASE_HOST_URL + '/upload/file/' + new_name,
                }
            }
            return JsonResponse(resp_json)

        except Exception as e:
            return JsonResponse({"errno": 1, "message": f"文件保存失败: {str(e)}"})

    return JsonResponse({"errno": 1, "message": "请求方法错误"})
