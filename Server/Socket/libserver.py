import re
def data_to_msg(data):
    print(data)
    header = data.split(' ', 1)[0]
    msg = data.split(' ', 1)[1]
    header = header.encode('utf-8')
    msg = msg.encode('utf-8')
    return header, msg
    
