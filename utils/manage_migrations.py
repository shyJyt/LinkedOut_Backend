# 删除已经生成的migrations文件
import os
import shutil


def remove_migrations():
    # 当前工作目录是manage.py所在目录
    # 项目目录
    project_path = os.path.abspath(os.path.join(os.getcwd(), ".."))
    # 遍历所有app
    for app_name in os.listdir(project_path):
        app_path = os.path.join(project_path, app_name)
        # 判断是否是app
        if os.path.isdir(app_path) and os.path.exists(os.path.join(app_path, 'models.py')):
            # migrations目录
            migrations_path = os.path.join(app_path, 'migrations')
            # 判断是否存在migrations目录
            if os.path.exists(migrations_path):
                # 遍历所有文件
                for file_name in os.listdir(migrations_path):
                    file_path = os.path.join(migrations_path, file_name)
                    # 判断是否是文件
                    if os.path.isfile(file_path):
                        # 删除文件
                        os.remove(file_path)
                # 删除migrations目录
                shutil.rmtree(migrations_path)
                print('remove migrations in %s' % app_name)
            # 重新创建migrations目录
            os.mkdir(migrations_path)
            # 创建__init__.py文件
            open(os.path.join(migrations_path, '__init__.py'), 'w').close()
    print('remove migrations success')


if __name__ == '__main__':
    remove_migrations()

