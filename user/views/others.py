from utils.view_decorator import allowed_methods, login_required

@allowed_methods(['GET'])
@login_required
def optimize_resume(request):
    """
    优化简历
    """
    pass
