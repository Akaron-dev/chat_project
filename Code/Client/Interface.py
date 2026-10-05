from tkinter import *
from tkinter import ttk

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
    for child in Options_box.winfo_children():
        child.grid_forget()
    Options_box.grid(column=1, row=2, sticky=(N, W, E, S))
    Settings_box.grid(column=1, row=1, sticky=(N, W, E, S))

def open_userlist():
    chat_box.grid_forget()
    for child in Options_box.winfo_children():
        child.grid_forget()
    Options_box.grid(column=1, row=2, sticky=(N, W, E, S))
    Userlist_box.grid(column=1, row=1, sticky=(N, W, E, S))

def open_credits():
    chat_box.grid_forget()
    for child in Options_box.winfo_children():
        child.grid_forget()
    Options_box.grid(column=1, row=2, sticky=(N, W, E, S))
    Credits_box.grid(column=1, row=1, sticky=(N, W, E, S))

root = Tk()
root.title("PY Chat")
root.geometry("1100x550+20+20")
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

username = StringVar()

# Fonts
fat_font = ("TkDefault", 24, "bold")
user_font = ("TkDefault", 14, "bold")
message_font = ("TkDefault", 12, "normal")

style = ttk.Style()
style.configure("Chat_Button.TButton", font=("Helvetica", 14, "normal"), width=20, anchor="w", padding=3)

mainframe = ttk.Frame(root, padding=(12, 12, 12, 12))
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(1, weight=1)
mainframe.rowconfigure(2, weight=1)

#Changable Button
Option_button = ttk.Button(mainframe, text="Options", command=open_menu)
Option_button.grid(column=2, row=1, sticky=(E))

Chats_button = ttk.Button(mainframe, text="Chats", command=open_chats)

#Get own username
ttk.Label(mainframe, text="Logged in as: Bernard", font=user_font, padding=(0,0,0,5)).grid(column=1, row=1, sticky=(W))

#First Column
Options_box = ttk.Frame(mainframe, width=500, borderwidth=1, relief="solid", padding= 4)
Options_box.columnconfigure(1, weight=1)
Options_box.rowconfigure(2, weight=1)

chat_box = ttk.Frame(mainframe, width=500, borderwidth=1, relief="solid")
chat_box.grid(column=1, row=2, sticky=(N, W, E, S)) 
chat_box.columnconfigure(1, weight=1)
chat_box.rowconfigure(2, weight=1)

message_box = ttk.Frame(chat_box, padding= 7, width=450, borderwidth=1, relief="solid")
message_box.grid(column=1, row=2, sticky=(N, W, E, S))
message_box.columnconfigure(1, weight=1)

#Settings
Settings_box = ttk.Frame(Options_box, width=500)
Settings_box.columnconfigure(1, weight=1)
Settings_box.rowconfigure(2, weight=1)

ttk.Label(Settings_box, text="Settings", font=("TkDefault", 16, "bold"), padding=(5,5,5,5)).grid(column=1, row=1, sticky=(N, W))

ttk.Button(Settings_box, text="Setting 1", style="Chat_Button.TButton").grid(column=1, row=2, sticky=(N, W))

#Userlist
Userlist_box = ttk.Frame(Options_box, width=500)
Userlist_box.columnconfigure(1, weight=1)
Userlist_box.rowconfigure(2, weight=1)

ttk.Label(Userlist_box, text="Users", font=("TkDefault", 16, "bold"), padding=(5,5,5,5)).grid(column=1, row=1, sticky=(N, W))

#Get Users
ttk.Button(Userlist_box, text="Bernard", style="Chat_Button.TButton").grid(column=1, row=2, sticky=(N, W))
ttk.Button(Userlist_box, text="Bastian", style="Chat_Button.TButton").grid(column=1, row=3, sticky=(N, W))
ttk.Button(Userlist_box, text="Tim", style="Chat_Button.TButton").grid(column=1, row=4, sticky=(N, W))

#Credits
Credits_box = ttk.Frame(Options_box, width=500)
Credits_box.columnconfigure(1, weight=1)    
Credits_box.rowconfigure(2, weight=1)

ttk.Label(Credits_box, text="Credits", font=fat_font, padding=5, anchor="center").grid(column=1, row=1, sticky=(W, E))
ttk.Label(Credits_box, text="Programming :", font=user_font, padding=5, anchor="center").grid(column=1, row=2, sticky=(W, E))
ttk.Label(Credits_box, text="Bernard Rognon, Tim Frauenfelder", font=message_font, padding=2, anchor="center").grid(column=1, row=3, sticky=(W, E))
ttk.Label(Credits_box, text="Supervised by :", font=user_font, padding=5, anchor="center").grid(column=1, row=4, sticky=(W, E))
ttk.Label(Credits_box, text="Thomas Graf", font=message_font, padding=2, anchor="center").grid(column=1, row=5, sticky=(W, E))
ttk.Label(Credits_box, text="Special Thanks to :", font=user_font, padding=5, anchor="center").grid(column=1, row=6, sticky=(W, E))
ttk.Label(Credits_box, text="Felix Angerer, Silas Roth", font=message_font, padding=2, anchor="center").grid(column=1, row=7, sticky=(W, E))

# Send message 
chat_entry = ttk.Entry(chat_box, width=50, font=message_font)
chat_entry.grid(column=1, row=3, sticky=(W, E))
chat_entry.focus()

# Load Chat
# Get Username
username.set("Bastian")
ttk.Label(chat_box, textvariable=username, font=user_font).grid(column=1, row=1, sticky=(N, W, E, S))

# Get Messages
ttk.Label(message_box, text="Hoi", font=message_font).grid(column=1, row=1, sticky=(W))
ttk.Label(message_box, text="Hoi Zrugg", font=message_font).grid(column=1, row=2, sticky=(E))

#Second Column
Column_two = ttk.Frame(mainframe, width=200, padding= 0)
Column_two.grid(column=2, row=2, sticky=(N, W, E, S))
Column_two.columnconfigure(1, weight=1)

chat_list = ttk.Frame(Column_two, width=200, padding= (7,0,7,0))
chat_list.grid(column=1, row=1, sticky=(N, W, E, S))
chat_list.columnconfigure(1, weight=1)

menu_list = ttk.Frame(Column_two, width=200, padding= (7,0,7,0))
menu_list.columnconfigure(1, weight=1)

# Get Chats
ttk.Label(chat_list, text="Chats", font=("TkDefault", 16, "bold"), padding=(5,0,5,5)).grid(column=1, row=1, sticky=(N, W, E, S))

chat1 = ttk.Button(chat_list, text="Chat 1", style="Chat_Button.TButton")
chat1.grid(column=1, row=2, sticky=(W))

chat2 = ttk.Button(chat_list, text="Chat 2", style="Chat_Button.TButton")
chat2.grid(column=1, row=3, sticky=(W))

# Options
ttk.Label(menu_list, text="Options", font=("TkDefault", 16, "bold"), padding=(5,0,5,5)).grid(column=1, row=1, sticky=(N, W, E, S))

ttk.Button(menu_list, text="Settings", style="Chat_Button.TButton", command=open_settings).grid(column=1, row=2, sticky=(W))
ttk.Button(menu_list, text="Find User", style="Chat_Button.TButton", command=open_userlist).grid(column=1, row=3, sticky=(W))
ttk.Button(menu_list, text="Credits", style="Chat_Button.TButton", command=open_credits).grid(column=1, row=4, sticky=(W))
ttk.Button(menu_list, text="Logout", style="Chat_Button.TButton").grid(column=1, row=5, sticky=(W))

root.mainloop()