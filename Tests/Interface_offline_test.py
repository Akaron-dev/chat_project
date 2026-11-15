from tkinter import *
from tkinter import ttk
from time import *

# --- DUMMY BACKEND FUNCTIONS (MULTIPLE ACCOUNTS & MULTI-MESSAGE) ---

MOCK_USERS = {
    "10000001": ("password123", "Alice"),
    "20000002": ("password123", "Bob"),
    "30000003": ("password123", "Charlie"),
    "40000004": ("password123", "Diana"),
    "50000005": ("password123", "Ethan")
}

CURRENT_USER_UID = None

def check_login(own_uid, own_password):
    global CURRENT_USER_UID
    if own_uid in MOCK_USERS and MOCK_USERS[own_uid][0] == own_password:
        CURRENT_USER_UID = own_uid
        return 1
    return 0

def get_open_chats():
    # Automatically generates chat list of all other users except the logged-in one
    if not CURRENT_USER_UID:
        return []
    chats = []
    for uid, (pwd, name) in MOCK_USERS.items():
        if uid != CURRENT_USER_UID:
            chats.append((name, uid))
    return chats

def get_chats_if():
    return get_open_chats()

def load_messages(chat_uid):
    current_time = time()
    
    # Predefined multi-message back-and-forth conversations for realism
    conversations = {
        "10000001": [
            ("Hey there! Are we still on for the project sync?", "10000001", current_time - 3600),
            ("Yes, absolutely! Let's meet at 3 PM sharp.", CURRENT_USER_UID, current_time - 3500),
            ("Perfect. Should I bring the draft presentation slides?", "10000001", current_time - 3400),
            ("Please do, and also bring the budget spreadsheet.", CURRENT_USER_UID, current_time - 3300),
            ("Got it. See you in the conference room!", "10000001", current_time - 3200),
        ],
        "20000002": [
            ("Did you check out the latest Python update?", "20000002", current_time - 7200),
            ("Not yet, is Tkinter getting any major improvements?", CURRENT_USER_UID, current_time - 7100),
            ("Mostly performance and clean bug fixes.", "20000002", current_time - 7000),
            ("That's awesome, I'll look into the changelog later.", CURRENT_USER_UID, current_time - 6900),
        ],
        "30000003": [
            ("Can you review my pull request when you have a free minute?", "30000003", current_time - 10000),
            ("Sure thing! I'll take a look right now.", CURRENT_USER_UID, current_time - 9900),
            ("Thanks! Let me know if you spot any issues with the grid layout.", "30000003", current_time - 9800),
            ("Will do, checking it out now...", CURRENT_USER_UID, current_time - 9700),
        ],
        "40000004": [
            ("Hello! Is this the new chat application test channel?", "40000004", current_time - 15000),
            ("Yes it is! Feel free to test multi-line messages and scrolling here.", CURRENT_USER_UID, current_time - 14900),
            ("Awesome, testing long text wrapping right now to see how the UI handles layout scaling.", "40000004", current_time - 14800),
            ("Looks like it wraps correctly and adjusts nicely.", CURRENT_USER_UID, current_time - 14750),
        ],
        "50000005": [
            ("Grab coffee later today?", "50000005", current_time - 20000),
            ("Count me in! Where should we meet up?", CURRENT_USER_UID, current_time - 19950),
            ("The usual cafe down the street works best.", "50000005", current_time - 19900),
            ("Sounds like a plan, see you at 2 PM.", CURRENT_USER_UID, current_time - 19850),
        ]
    }
    
    # Fallback multi-message generator for any newly added 8-digit contact
    if chat_uid not in conversations:
        messages = []
        for i in range(1, 15):
            msg_time = current_time - (15 - i) * 120
            sender = CURRENT_USER_UID if i % 2 == 0 else chat_uid
            text = f"Multi-message sequence item #{i}: Testing scrollable canvas behavior and layout bounds."
            messages.append((text, sender, str(msg_time)))
        return conversations.get(chat_uid, messages)

    return conversations[chat_uid]

def logout():
    global CURRENT_USER_UID
    CURRENT_USER_UID = None
    print("Logged out successfully.")

def sign_up(new_password, invite_code):
    if invite_code == "SECRET":
        return 1
    return 2

def get_last_created_uid():
    return "60000006"  # Generates an 8-digit UID on successful signup

def send_message(outgoing_message, recipient):
    print(f"[MOCK SEND] To UID {recipient}: {outgoing_message}")

def add_contact(uid, Nickname):
    # Ensures entered UID is strictly an 8-digit number
    if not uid.isdigit() or len(uid) != 8:
        return 3  # Invalid UID format / doesn't exist
    if uid in MOCK_USERS or uid == CURRENT_USER_UID:
        return 2  # Already exists
    return 1      # Success

def is_loggedin():
    return (0, "", "")

def register_ui_callbacks(get_active_uid, on_message, on_new_chat):
    pass

#end of dummy backend functions

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

def build_chats() :
    open_chats = get_open_chats()
    for i, user in enumerate(open_chats):
        username = user[0]
        uid = user[1]
        chat1 = ttk.Button(chat_list, text=username, command=lambda c=user: open_chat(c), style="Chat_Button.TButton")
        chat1.grid(column=1, row=i+2, sticky=(W))
    global chats_number
    chats_number = len(open_chats)

def load_messages_if(chat_uid):
    global message_counter
    messages_render = load_messages(chat_uid)
    for i, msg in enumerate(messages_render) :
        text ,uid ,time = msg
        real_time = strftime('%H:%M:%S %d.%m.%Y', localtime(float(time)))
        if uid == own_username.get() : 
            ttk.Label(message_box, text="You" , font=("TkDefault", 13, "bold"), ).grid(column=1, row=message_counter, sticky=(E))
            ttk.Label(message_box, text=text , font=message_font2, foreground="blue", wraplength=620, justify="right").grid(column=1, row=message_counter+1, sticky=(E))
            ttk.Label(message_box, text=real_time , font=("TkDefault", 8, "normal"), ).grid(column=1, row=message_counter+2, sticky=(E))
            message_counter += 3
        else :
            ttk.Label(message_box, text=chat_username.get() , font=("TkDefault", 12, "bold"), ).grid(column=1, row=message_counter, sticky=(W))
            ttk.Label(message_box, text=text , font=message_font2,justify="left",wraplength=620).grid(column=1, row=message_counter+1, sticky=(W))
            ttk.Label(message_box, text=real_time , font=("TkDefault", 8, "normal"), ).grid(column=1, row=message_counter+2, sticky=(W))
            message_counter += 3

    message_canvas.yview_moveto(0)
    

def load_new_message_if(message):
    global message_counter
    text ,uid ,time = message
    real_time = strftime('%H:%M:%S %d.%m.%Y', localtime(float(time)))
    if uid == own_username.get() : 
        ttk.Label(message_box, text="You" , font=("TkDefault", 13, "bold"), ).grid(column=1, row=message_counter, sticky=(E))
        ttk.Label(message_box, text=text , font=message_font2, foreground="blue").grid(column=1, row=message_counter+1, sticky=(E))
        ttk.Label(message_box, text=real_time , font=("TkDefault", 8, "normal"), ).grid(column=1, row=message_counter+2, sticky=(E))
        message_counter += 3
    else :
        ttk.Label(message_box, text=chat_username.get() , font=("TkDefault", 12, "bold"), ).grid(column=1, row=message_counter, sticky=(W))
        ttk.Label(message_box, text=text , font=message_font2).grid(column=1, row=message_counter+1, sticky=(W))
        ttk.Label(message_box, text=real_time , font=("TkDefault", 8, "normal"), ).grid(column=1, row=message_counter+2, sticky=(W))
        message_counter += 3

def check_login_if(own_uid, own_password):
    attempts = 0
    login_status = check_login(own_uid, own_password)
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
    logout()
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
    signup_status = sign_up(new_password, invite_code)
    if signup_status == 1 :
        login_entry.delete(0, END)
        login_entry.insert(0, str(get_last_created_uid()))
        signup_window.grid_forget()
        success_window.grid(column=0, row=0)
        npassword_entry.delete(0,END)
        invite_entry.delete(0,END)
        
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
    if chat_entry.get() == "" or open_chat_uid.get() == "" :
        chat_entry.focus()
        return
    else :
        send_message(outgoing_message, recipient)
        chat_entry.delete(0,END)
        chat_entry.focus()

def add_contact_if(uid, Nickname):
    attempts = 0
    if uid == "" or Nickname == "" :
        not_filled.grid_forget()
        already_exists.grid_forget()
        no_exist.grid_forget()
        not_filled.grid(column=1, row=8, columnspan=2)
        return
    add_status = add_contact(uid, Nickname)
    if add_status == 1 :
        global chats_number
        user = (Nickname,uid)
        not_filled.grid_forget()
        already_exists.grid_forget()
        no_exist.grid_forget()
        open_chat(user)
        username = Nickname
        chat1 = ttk.Button(chat_list, text=username, command=lambda c=user: open_chat(c), style="Chat_Button.TButton")
        chat1.grid(column=1, row=chats_number+2, sticky=(W))
        name_entry.delete(0,END)
        uid_entry.delete(0,END)
        open_chats()
        chats_number += 1
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
chats_number = 0
message_counter = 0

# Fonts
fat_font = ("TkDefault", 24, "bold")
user_font = ("TkDefault", 14, "bold")
message_font = ("TkDefault", 12, "normal")
message_font2 = ("TkDefault", 14, "normal")

style = ttk.Style()
style.configure("Chat_Button.TButton", font=("Helvetica", 14, "normal"), width=20, anchor="w", padding=3)
login_button_style = ttk.Style()
login_button_style.configure("Login_Button.TButton", font=("Helvetica", 11, "normal"), width=12, anchor="center", padding=3)
signup_button_style = ttk.Style()
signup_button_style.configure("Signup_Button.TButton", font=("Helvetica", 11, "normal"), anchor="center", padding=3)


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
ttk.Label(signup_window, text="Invite Code", font=user_font, padding=5).grid(column=0, row=1, columnspan=2)
invite_entry = ttk.Entry(signup_window, width=20, font=message_font)
invite_entry.grid(column=0, row=2, columnspan=2)
npassword_entry = ttk.Entry(signup_window, width=20, font=message_font, show="*")
npassword_entry.grid(column=0, row=4, columnspan=2)
signup_button = ttk.Button(signup_window, text="Sign Up", style="Login_Button.TButton", command= lambda: sign_up_if(npassword_entry.get(),invite_entry.get()))
signup_button.grid(column=0, row=7, pady=7)
tologin_button = ttk.Button(signup_window, text="Log In", style="Login_Button.TButton", command=tologin)
tologin_button.grid(column=1, row=7, pady=7)
bad_invite = ttk.Label(signup_window, text="Invalid invite code", font=("TkDefault", 10, "bold"), foreground="red",anchor=CENTER)
no_cridentials = ttk.Label(signup_window, text="Enter invite code and password", font=("TkDefault", 8, "bold"), foreground="red",anchor=CENTER)
success_window = ttk.Frame(login_frame, width=500, borderwidth=1, relief="solid", padding= 4)
ttk.Label(success_window, text="Sign Up Successfull", font=("TkDefault", 22, "bold"), foreground="Green",anchor=CENTER).grid(row=0,column=0)
ttk.Label(success_window, text="This is your UID, it is used to log in.", font=("TkDefault", 13, "bold"),anchor=CENTER).grid(row=1,column=0)
ttk.Label(success_window, text="Please save it.", font=("TkDefault", 13, "bold"),anchor=CENTER).grid(row=2,column=0)
text_box = ttk.Entry(success_window, font=("TkDefault", 12, "normal"), justify="center")
text_box.grid(row=3,column=0)
text_box.insert(0,"UID: " + str(get_last_created_uid()))
text_box.state(["readonly"])
ttk.Button(success_window, text="Continue to Log In", style="Signup_Button.TButton", command=finish_signup).grid(row=4,column=0, pady=7)


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

message_canvas = Canvas(chat_box)
message_canvas.grid(column=1, row=2, columnspan=2, sticky=NSEW)
message_canvas.rowconfigure(2,weight=1)

message_box = ttk.Frame(message_canvas, padding= 7, width=450, borderwidth=1, relief="solid")
message_box.columnconfigure(1, weight=1)

message_scrollbar = ttk.Scrollbar(chat_box, orient="vertical", command=message_canvas.yview)
message_scrollbar.grid(column=3,row=2,sticky=NS)
message_box.bind("<Configure>",lambda e: message_canvas.configure(scrollregion=message_canvas.bbox("all")))
message_canvas.configure(yscrollcommand=message_scrollbar.set)
message_window = message_canvas.create_window(0, 0, window=message_box, anchor=NW)
message_canvas.bind("<Configure>", lambda e: message_canvas.itemconfig(message_window, width=e.width))

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

chats_canvas = Canvas(Column_two,width=244, height=500)
chats_canvas.grid(column=1,row=1, sticky=NSEW)

chat_list = ttk.Frame(chats_canvas, width=200, padding= (7,0,7,0))
chats_canvas.create_window((0, 0), window=chat_list, anchor="nw")
chat_list.columnconfigure(1, weight=1)

chat_list.bind("<Configure>",lambda e: chats_canvas.configure(scrollregion=chats_canvas.bbox("all")))

scrollbar = ttk.Scrollbar(mainframe, orient="vertical", command=chats_canvas.yview)
scrollbar.grid(row=2,column=3, sticky=NS)

chats_canvas.configure(yscrollcommand=scrollbar.set)



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

def refresh_chat_list():
    for child in chat_list.winfo_children():
        if isinstance(child, ttk.Button):
            child.destroy()
    build_chats()

register_ui_callbacks(
    get_active_uid=lambda: open_chat_uid.get(),
    on_message=lambda msg: root.after(0, lambda: load_new_message_if(msg)),
    on_new_chat=lambda: root.after(0, refresh_chat_list)
)

root.mainloop()