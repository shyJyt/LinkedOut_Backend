import os

from django.http import StreamingHttpResponse

from enterprise.models import User

from utils.view_decorator import allowed_methods, login_required
from utils.response import response
from utils.status_code import PARAMS_ERROR, SUCCESS, OSS_ERROR
from utils.qos import save_file_local, generate_time_stamp, upload_file, get_file, delete_file

from kimi.kimi import kimi
from tencent.ocr import ocr

@allowed_methods(['POST'])
@login_required
def optimize_resume(request):
    """
    优化简历
    """
    resume = request.FILES.get('resume', None)

    if resume:
        resume_path = save_file_local(resume)
        result = kimi(resume_path, resume.name)
        return StreamingHttpResponse(result, content_type='text/plain')
    else:
        return response(PARAMS_ERROR, '未上传简历！', error=True)


@allowed_methods(['POST'])
@login_required
def get_pdf_content(request):
    """
    获取 PDF 内容
    """
    resume = request.FILES.get('resume', None)

    user = request.user
    user: User

    if resume:
        local_file = save_file_local(resume)
        key = str(user.id) + '_ocr_'+ generate_time_stamp() + '.pdf'
        # 上传到七牛云
        ret = upload_file(key, local_file)
        os.remove(local_file)
        if ret:
            resume_path = get_file(key)
        else:
            return response(OSS_ERROR, 'ocr上传简历失败！', error=True)
        
        # 识别 PDF 内容
        data = {
            'content': ocr(resume_path)
        }

        # 删除七牛云上的文件
        delete_file(key)

        return response(SUCCESS, '获取 PDF 内容成功！', data=data)
    else:
        return response(PARAMS_ERROR, '未上传简历！', error=True)



@allowed_methods(['GET'])
@login_required
def reduce_gpt_limit(request):
    user = request.user
    user: User
    user.gpt_limit = user.gpt_limit - 1
    user.save()

    return response(SUCCESS, '减少简历优化次数成功！')
