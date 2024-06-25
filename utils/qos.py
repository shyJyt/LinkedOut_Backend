import random
import time

from qiniu import Auth, put_file, etag, BucketManager
from config import ACCESS_KEY, SECRET_KEY, BUCKET_NAME, BASE_URL


def generate_time_stamp() -> str:
    """
    生成时间戳
    :return: 时间戳
    """
    return str(int(time.time()))


def save_file_local(file):
    """
    保存文件到本地
    :param file: 文件对象
    :return: 文件名
    """
    # 获取文件名
    file_name = file.name
    # 获取文件后缀名
    file_suffix = file_name.split('.')[-1]
    # 生成文件名
    file_name = str(random.randint(100000, 999999)) + '.' + file_suffix
    # 保存文件
    file_path = 'tempFile/' + file_name
    with open(file_path, 'wb+') as f:
        for chunk in file.chunks():
            f.write(chunk)
    return file_path


def upload_file(key: str, file_path) -> bool:
    """
    上传文件
    :param key: 上传的文件保存的文件名
    :param file_path: 要上传的文件在本地的存储路径
    :return: 重名False,否则上传成功True
    """
    # 构建鉴权对象
    q = Auth(ACCESS_KEY, SECRET_KEY)
    # 检查是否重名
    bucket = BucketManager(q)
    ret, info = bucket.stat(BUCKET_NAME, key)
    # 如果存在则删除
    if ret:
        ret, info = bucket.delete(BUCKET_NAME, key)
        if ret:
            assert ret == {}
        else:
            return False
    # 生成上传 Token，可以指定过期时间等
    token = q.upload_token(BUCKET_NAME, key, 3600)
    # 要上传文件的本地路径
    local_file = file_path
    ret, info = put_file(token, key, local_file)
    if ret:
        assert ret['key'] == key
        assert ret['hash'] == etag(local_file)
        return True
    else:
        print(ret + '\n' + info)
        return False


def get_file(key: str) -> str:
    """
    获取文件
    :param key: 文件名
    :return: url
    """
    # 检查是否存在
    q = Auth(ACCESS_KEY, SECRET_KEY)
    bucket = BucketManager(q)
    ret, info = bucket.stat(BUCKET_NAME, key)
    if not ret:
        return ''
    # 生成下载链接
    url = BASE_URL + key
    return q.private_download_url(url, expires=3600)


def delete_file(key: str) -> bool:
    """
    删除文件
    :param key: 文件名
    :return: 删除成功True,否则False
    """
    q = Auth(ACCESS_KEY, SECRET_KEY)
    bucket = BucketManager(q)
    ret, info = bucket.delete(BUCKET_NAME, key)
    if ret:
        assert ret == {}
        return True
    else:
        return False


if __name__ == '__main__':
    # upload_file("default_institution.png", "./default_institution.png")
    print(get_file("语境（考古学）.png"))
