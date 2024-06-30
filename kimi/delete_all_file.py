from client import client

file_list = client.files.list()
 
for file in file_list.data:
    file_id = file.id
    ret = client.files.delete(file_id=file_id)
    print(f'删除文件:{ret.id}，结果：{ret.deleted}')
