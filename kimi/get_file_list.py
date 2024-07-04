from client import client

file_list = client.files.list()
 
for file in file_list.data:
    print(file) # 查看每个文件的信息