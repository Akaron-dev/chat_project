from tkinter import *
from tkinter import ttk
import time 
#import whatever for functions to work

#Test for is logged in Remove !!!
def is_loggedin():
    return (1,"Bernard","7567")

def open_menu():
    chat_list.grid_forget()
    Option_button.grid_forget()
    menu_list.grid(column=1, row=2, sticky=(N, W, E, S))
    Chats_button.grid(column=2, row=1, sticky=(E))

def open_chats():
    menu_list.grid_forget()
    Chats_button.grid_forget()
    chat_list.grid(column=1, row=2, sticky=(N, W, E, S))
    Option_button.grid(column=2, row=1, sticky=(E))

def open_settings():
    chat_box.grid_forget()
    chat_entry.delete(0, END)
    for child in Options_box.winfo_children():
        child.grid_forget()
    Options_box.grid(column=1, row=2, sticky=(N, W, E, S))
    Settings_box.grid(column=1, row=1, sticky=(N, W, E, S))

def open_add_contact():
    chat_box.grid_forget()
    chat_entry.delete(0, END)
    for child in Options_box.winfo_children():
        child.grid_forget()
    Options_box.grid(column=1, row=2, sticky=(N, S, E, W))
    newcontact_box.grid(column=1, row=1)
    not_filled.grid_forget()
    already_exists.grid_forget()
    no_exist.grid_forget()
    name_entry.delete(0,END)
    uid_entry.delete(0,END)
    uid_entry.focus()

def open_credits():
    chat_box.grid_forget()
    chat_entry.delete(0, END)
    for child in Options_box.winfo_children():
        child.grid_forget()
    Options_box.grid(column=1, row=2, sticky=(N, W, E, S))
    Credits_box.grid(column=1, row=1, sticky=(N, W, E, S))

def open_chat(user_tuple):
    username, uid = user_tuple
    Options_box.grid_forget()
    chat_box.grid(column=1, row=2, sticky=(N, W, E, S))
    chat_entry.delete(0, END)
    chat_username.set(username)
    open_chat_uid.set(uid)
    for child in message_box.winfo_children():
        child.destroy()
    ttk.Label(chat_box, textvariable=chat_username, font=user_font).grid(column=1, row=1, sticky=(N, W, E, S))
    if user_tuple in get_chats_if():
        load_messages_if(uid)
    chat_entry.grid(column=1, row=3, sticky=(W, E))
    send_button.grid(column=2, row=3, sticky=(W))
    chat_entry.focus()

def get_chats_if() :
    #replace all of this function in the places with the bigger function
    #get_open_chats()
    # Remove this !!!
    if own_username.get() == "Bernard":
        open_chats = [("Bastian","33973397"), ("Lukas","12345678")]
    elif own_username.get() == "Tim":
        open_chats = [("Bastian","33973397"),("Felix","98765432")]
    return open_chats

def build_chats() :
    open_chats = get_chats_if()
    for i, user in enumerate(open_chats):
        username = user[0]
        uid = user[1]
        chat1 = ttk.Button(chat_list, text=username, command=lambda c=user: open_chat(c), style="Chat_Button.TButton")
        chat1.grid(column=1, row=i+2, sticky=(W))

def load_messages_if(chat_uid):
    # Get Messages
    if chat_uid == "33973397":
        ttk.Label(message_box, text="Hoi", font=message_font).grid(column=1, row=1, sticky=(W))
        ttk.Label(message_box, text="Hoi Zrugg", font=message_font).grid(column=1, row=2, sticky=(E))
    elif chat_uid == "12345678":
        ttk.Label(message_box, text="Hallo", font=message_font).grid(column=1, row=1, sticky=(W))
        ttk.Label(message_box, text="Hallo Zrugg", font=message_font).grid(column=1, row=2, sticky=(E))
    elif chat_uid == "98765432":
        ttk.Label(message_box, text="Hi", font=message_font).grid(column=1, row=1, sticky=(W))
        ttk.Label(message_box, text="Hi Zrugg", font=message_font).grid(column=1, row=2, sticky=(E))

def check_login_if(own_uid, own_password):
    attempts = 0
    #login_status = check_login(own_uid, own_password)
    login_status = 1
    if login_status == 1 :
        login_frame.grid_forget()
        mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        own_username.set(own_uid)
        own_userstring.set("Logged in as: " + own_uid)
        login_entry.delete(0, END)
        password_entry.delete(0, END)
        build_chats()
        root.bind('<Return>', lambda event: send_message_if(chat_entry.get(),open_chat_uid.get()))
        logged_in_as = ttk.Label(mainframe, textvariable=own_userstring, font=user_font, padding=(0,0,0,5))
        logged_in_as.grid(column=1, row=1, sticky=(W))
        bad_login.grid_forget()
    elif attempts < 1:
        bad_login.grid(column=0, row=6, columnspan=2)
        attempts += 1


def logout_if():
    #logout()
    mainframe.grid_forget()
    login_frame.grid(column=0, row=0, sticky=(N, W, E, S))
    own_username.set("")
    own_userstring.set("")
    chat_username.set("")
    open_chat_uid.set("")
    not_filled.grid_forget()
    already_exists.grid_forget()
    no_exist.grid_forget()
    name_entry.delete(0,END)
    uid_entry.delete(0,END)
    chat_entry.delete(0, END)
    Options_box.grid_forget()
    root.bind('<Return>', lambda event: login_button.invoke())
    for child in chat_list.winfo_children():
        if isinstance(child, ttk.Button):
            child.destroy()
    for child in message_box.winfo_children():
        child.destroy()
    for child in chat_box.winfo_children():
        child.grid_forget()
    open_chats()
    login_entry.focus()

def sign_up_if(new_password, invite_code):
    attempts = 0
    if new_password == "" or invite_code == "" :
        bad_invite.grid_forget()
        no_cridentials.grid(column=0,row=8, columnspan=2)
        return
    #remove this !!!!!
    signup_status = 2
    #signup_status = sign_up(new_password, invite_code)
    if signup_status == 1 :
        signup_window.grid_forget()
        success_window.grid(column=0, row=0)
        npassword_entry.delete(0,END)
        invite_entry.delete(0,END)
        root.after(2500, finish_signup)
    elif signup_status == 2 and attempts < 1:
        no_cridentials.grid_forget()
        bad_invite.grid(column=0,row=8, columnspan=2)
        attempts += 1

def finish_signup():
        success_window.grid_forget()
        root.bind('<Return>', lambda event: login_button.invoke())
        login_window.grid(column=0, row=0)

def tosignup():
    login_window.grid_forget()
    signup_window.grid(column=0, row=0)
    login_entry.delete(0, END)
    password_entry.delete(0, END)
    invite_entry.focus()
    bad_invite.grid_forget()
    no_cridentials.grid_forget()
    root.bind('<Return>', lambda event: signup_button.invoke())

def tologin():
    signup_window.grid_forget()
    login_window.grid(column=0, row=0)
    bad_login.grid_forget()
    npassword_entry.delete(0,END)
    invite_entry.delete(0,END)
    login_entry.focus()
    root.bind('<Return>', lambda event: login_button.invoke())

def send_message_if(outgoing_message, recipient):
    if chat_entry.get() == "" or open_chat_uid.get == "" :
        chat_entry.focus()
        return
    else :
        # Remove this !!!
        print(outgoing_message, recipient,"sent")
        # send_message(outgoing_message, recipient)
        chat_entry.delete(0,END)
        chat_entry.focus()

def add_contact_if(uid, Nickname):
    # Remove this !!!
    add_status = 1
    attempts = 0
    #add_status = add_contact(uid, Nickname)
    if uid == "" or Nickname == "" :
        not_filled.grid_forget()
        already_exists.grid_forget()
        no_exist.grid_forget()
        not_filled.grid(column=1, row=8, columnspan=2)
        return
    #add_status = add_contact(uid, Nickname)
    if add_status == 1 :
        usertuple = (Nickname,uid)
        not_filled.grid_forget()
        already_exists.grid_forget()
        no_exist.grid_forget()
        open_chat(usertuple)
        name_entry.delete(0,END)
        uid_entry.delete(0,END)
    elif add_status == 2 and attempts < 1:
        not_filled.grid_forget()
        no_exist.grid_forget()
        already_exists.grid(column=1, row=8, columnspan=2)
    elif add_status == 3 :
        not_filled.grid_forget()
        already_exists.grid_forget()
        no_exist.grid_forget()
        no_exist.grid(column=1, row=8, columnspan=2)

root = Tk()
root.title("PY Chat")
root.geometry("1100x550+20+20")
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

own_username = StringVar()
chat_username = StringVar()
own_userstring = StringVar()
open_chat_uid = StringVar()

# Fonts
fat_font = ("TkDefault", 24, "bold")
user_font = ("TkDefault", 14, "bold")
message_font = ("TkDefault", 12, "normal")

style = ttk.Style()
style.configure("Chat_Button.TButton", font=("Helvetica", 14, "normal"), width=20, anchor="w", padding=3)
login_button_style = ttk.Style()
login_button_style.configure("Login_Button.TButton", font=("Helvetica", 11, "normal"), width=12, anchor="center", padding=3)

mainframe = ttk.Frame(root, padding=12)
mainframe.columnconfigure(1, weight=1)
mainframe.rowconfigure(2, weight=1)

login_frame = ttk.Frame(root, padding=12)
login_frame.grid(column=0, row=0, sticky=(N, W, E, S))
login_frame.columnconfigure(0, weight=1)
login_frame.rowconfigure(0, weight=1)

login_window = ttk.Frame(login_frame, width=500, borderwidth=1, relief="solid", padding= 4)
login_window.grid(column=0, row=0)

ttk.Label(login_window, text="Log In", font=fat_font, padding=5).grid(column=0, row=0, columnspan=2)
ttk.Label(login_window, text="UID", font=user_font, padding=5).grid(column=0, row=1, columnspan=2)
login_entry = ttk.Entry(login_window, width=20, font=message_font)
login_entry.grid(column=0, row=2, columnspan=2)
ttk.Label(login_window, text="Password", font=user_font, padding=5).grid(column=0, row=3, columnspan=2)
password_entry = ttk.Entry(login_window, width=20, font=message_font, show="*")
password_entry.grid(column=0, row=4, columnspan=2)
ttk.Button(login_window, text="Sign Up", style="Login_Button.TButton", command=tosignup).grid(column=0, row=5, pady=7)
login_button = ttk.Button(login_window, text="Log In", style="Login_Button.TButton", command=lambda: check_login_if(login_entry.get(), password_entry.get()))
login_button.grid(column=1, row=5, pady=7)
bad_login = ttk.Label(login_window, text="Wrong UID or Password", font=("TkDefault", 10, "bold"), foreground="red")

signup_window = ttk.Frame(login_frame, width=500, borderwidth=1, relief="solid", padding= 4)

ttk.Label(signup_window, text="Sign Up", font=fat_font, padding=5).grid(column=0, row=0, columnspan=2)
ttk.Label(signup_window, text="Password", font=user_font, padding=5).grid(column=0, row=3, columnspan=2)
npassword_entry = ttk.Entry(signup_window, width=20, font=message_font, show="*")
npassword_entry.grid(column=0, row=4, columnspan=2)
ttk.Label(signup_window, text="Invite Code", font=user_font, padding=5).grid(column=0, row=1, columnspan=2)
invite_entry = ttk.Entry(signup_window, width=20, font=message_font)
invite_entry.grid(column=0, row=2, columnspan=2)
signup_button = ttk.Button(signup_window, text="Sign Up", style="Login_Button.TButton", command= lambda: sign_up_if(npassword_entry.get(),invite_entry.get()))
signup_button.grid(column=0, row=7, pady=7)
tologin_button = ttk.Button(signup_window, text="Log In", style="Login_Button.TButton", command=tologin)
tologin_button.grid(column=1, row=7, pady=7)
bad_invite = ttk.Label(signup_window, text="Invalid invite code", font=("TkDefault", 10, "bold"), foreground="red",anchor=CENTER)
no_cridentials = ttk.Label(signup_window, text="Enter invite code and password", font=("TkDefault", 8, "bold"), foreground="red",anchor=CENTER)
success_window = ttk.Frame(login_frame, width=500, borderwidth=1, relief="solid", padding= 4)
ttk.Label(success_window, text="Sign Up Successfull", font=("TkDefault", 22, "bold"), foreground="Green",anchor=CENTER).grid(row=0,column=0)

#Changable Button
Option_button = ttk.Button(mainframe, text="Options", command=open_menu)
Option_button.grid(column=2, row=1, sticky=(E))

Chats_button = ttk.Button(mainframe, text="Chats", command=open_chats)

#First Column
Options_box = ttk.Frame(mainframe, width=500, borderwidth=1, relief="solid", padding= 4)
Options_box.columnconfigure(1, weight=1)
Options_box.rowconfigure(1, weight=1)

chat_box = ttk.Frame(mainframe, width=500, borderwidth=1, relief="solid")
chat_box.grid(column=1, row=2, sticky=(N, W, E, S)) 
chat_box.columnconfigure(1, weight=1)
chat_box.rowconfigure(2, weight=1)

message_box = ttk.Frame(chat_box, padding= 7, width=450, borderwidth=1, relief="solid")
message_box.grid(column=1, row=2,columnspan=2,sticky=(N, W, E, S))
message_box.columnconfigure(1, weight=1)

#Settings
Settings_box = ttk.Frame(Options_box, width=500)
Settings_box.columnconfigure(1, weight=1)
Settings_box.rowconfigure(2, weight=1)

ttk.Label(Settings_box, text="Settings", font=("TkDefault", 16, "bold"), padding=(5,5,5,5)).grid(column=1, row=1, sticky=(N, W))

ttk.Button(Settings_box, text="Setting 1", style="Chat_Button.TButton").grid(column=1, row=2, sticky=(N, W))

#Add Contact
newcontact_box = ttk.Frame(Options_box, width=500, padding=10, borderwidth=1, relief="solid")

ttk.Label(newcontact_box, text="Add Contact", font=("TkDefault", 16, "bold"), padding=5).grid(column=1, row=1, columnspan=2)
ttk.Label(newcontact_box, text="UID", font=user_font, padding=5).grid(column=1, row=2, columnspan=2)
uid_entry = ttk.Entry(newcontact_box, width=20, font=message_font)
uid_entry.grid(column=1, row=3, columnspan=2)
ttk.Label(newcontact_box, text="Name", font=user_font, padding=5).grid(column=1, row=4, columnspan=2)
name_entry = ttk.Entry(newcontact_box, width=20, font=message_font)
name_entry.grid(column=1, row=5, sticky=(W))
save_button = ttk.Button(newcontact_box, text="Save", style="Login_Button.TButton", command=lambda: add_contact_if(uid_entry.get(), name_entry.get()))
save_button.grid(column=1, row=7, pady=7)
already_exists = ttk.Label(newcontact_box, text="This Contact already exists", font=("TkDefault", 10, "bold"), foreground="red")
not_filled = ttk.Label(newcontact_box, text="Please enter UID and Name", font=("TkDefault", 10, "bold"), foreground="red")
no_exist = ttk.Label(newcontact_box, text="This UID doesn't exist", font=("TkDefault", 10, "bold"), foreground="red")

#Credits
Credits_box = ttk.Frame(Options_box, width=500)
Credits_box.columnconfigure(1, weight=1)

ttk.Label(Credits_box, text="Credits", font=fat_font, padding=5, anchor="center").grid(column=1, row=0, sticky=(W, E))
ttk.Label(Credits_box, text="Programming :", font=user_font, padding=5, anchor="center").grid(column=1, row=2, sticky=(W, E))
ttk.Label(Credits_box, text="Bernard Rognon, Tim Frauenfelder", font=message_font, padding=2, anchor="center").grid(column=1, row=3, sticky=(W, E))
ttk.Label(Credits_box, text="Supervised by :", font=user_font, padding=5, anchor="center").grid(column=1, row=4, sticky=(W, E))
ttk.Label(Credits_box, text="Thomas Graf", font=message_font, padding=2, anchor="center").grid(column=1, row=5, sticky=(W, E))
ttk.Label(Credits_box, text="Special Thanks to :", font=user_font, padding=5, anchor="center").grid(column=1, row=6, sticky=(W, E))
ttk.Label(Credits_box, text="Felix Angerer, Silas Roth, Irina Läubli", font=message_font, padding=2, anchor="center").grid(column=1, row=7, sticky=(W, E))

# Send message 
chat_entry = ttk.Entry(chat_box, width=40, font=message_font)
send_button = ttk.Button(chat_box,text="Send",command= lambda : send_message_if(chat_entry.get(),open_chat_uid.get()))

#Second Column
Column_two = ttk.Frame(mainframe, width=200, padding= 0)
Column_two.grid(column=2, row=2, sticky=(N, W, E, S))
Column_two.columnconfigure(1, weight=1)

chat_list = ttk.Frame(Column_two, width=200, padding= (7,0,7,0))
chat_list.grid(column=1, row=1, sticky=(N, W, E, S))
chat_list.columnconfigure(1, weight=1)

ttk.Label(chat_list, text="Chats", font=("TkDefault", 16, "bold"), padding=(5,0,5,5)).grid(column=1, row=1, sticky=(N, W, E, S))

menu_list = ttk.Frame(Column_two, width=200, padding= (7,0,7,0))
menu_list.columnconfigure(1, weight=1)

# Options
ttk.Label(menu_list, text="Options", font=("TkDefault", 16, "bold"), padding=(5,0,5,5)).grid(column=1, row=1, sticky=(N, W, E, S))

ttk.Button(menu_list, text="Settings", style="Chat_Button.TButton", command=open_settings).grid(column=1, row=2, sticky=(W))
ttk.Button(menu_list, text="Add Contact", style="Chat_Button.TButton", command=open_add_contact).grid(column=1, row=3, sticky=(W))
ttk.Button(menu_list, text="Credits", style="Chat_Button.TButton", command=open_credits).grid(column=1, row=4, sticky=(W))
ttk.Button(menu_list, text="Logout", style="Chat_Button.TButton", command=logout_if).grid(column=1, row=5, sticky=(W))

login_entry.focus()
root.bind('<Return>', lambda event: login_button.invoke())

logindata = is_loggedin()
if logindata[0] == 1 :
    number, uid, password = logindata
    check_login_if(uid, password)

root.mainloop()