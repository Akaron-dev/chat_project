import re
def data_to_msg(data):
    data = data.decode('utf-8')
    header = data.split(' ', 1)[0]
    msg = data.split(' ', 1)[1]
    return header, msg
    
#fix function for new code layout