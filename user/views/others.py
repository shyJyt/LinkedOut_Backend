import os

from django.http import StreamingHttpResponse

from utils.view_decorator import allowed_methods, login_required
from utils.response import response
from utils.status_code import PARAMS_ERROR, SUCCESS
from utils.qos import save_file_local

from kimi.kimi import kimi

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
