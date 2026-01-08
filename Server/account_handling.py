import json


Account_names = []
new_user=()
password_hash=()

def create_account():
    Account_names.append(new_user)
    with open(f'/home/steinbock/chat_project/userdata/password_{new_user}.json', "a") as f:
        f.write(json.dumps(password_hash))
    open(f"/home/steinbock/chat_project/userdata/chatdata_{new_user}.json", "w")                  
    print("Account was Created")                                                        #Send response to Client


