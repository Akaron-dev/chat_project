from tkinter import *
from tkinter import ttk

user_font = ("TkDefault", 14, "bold")
message_font = ("TkDefault", 12, "normal")

root = Tk()
root.title("PY Chat")
root.geometry("1100x550+20+20")
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)


mainframe = ttk.Frame(root, padding=(12, 12, 12, 12))
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(1, weight=1)
mainframe.rowconfigure(2, weight=1)

# Get the username
username = StringVar()
username.set("Bastian")

chat_box = ttk.Frame(mainframe, width=500, borderwidth=1, relief="solid")
chat_box.grid(column=1, row=2, sticky=(N, W, E, S)) 
chat_box.columnconfigure(1, weight=1)
chat_box.rowconfigure(2, weight=1)

message_box = ttk.Frame(chat_box, padding= 7, width=450, borderwidth=1, relief="solid")
message_box.grid(column=1, row=2, sticky=(N, W, E, S))
message_box.columnconfigure(1, weight=1)

ttk.Label(chat_box, textvariable=username, font=user_font).grid(column=1, row=1, sticky=(N, W, E, S))

# Send message 
ttk.Entry(chat_box, width=50, font=message_font).grid(column=1, row=3, sticky=(W, E))

#   Load Messages
ttk.Label(message_box, text="Hoi", font=message_font).grid(column=1, row=1, sticky=(W))
ttk.Label(message_box, text="Hoi Zrugg", font=message_font).grid(column=1, row=2, sticky=(E))

chat_list = ttk.Frame(mainframe, width=200, padding= 7)
chat_list.grid(column=2, row=2, sticky=(N, W, E, S))
chat_list.columnconfigure(1, weight=1)

ttk.Label(chat_list, text="Chats", font=("TkDefault", 16, "bold"), padding=5).grid(column=1, row=1, sticky=(N, W, E, S))

style = ttk.Style()
style.configure("Chat_Button.TButton", font=("Helvetica", 14, "normal"), width=20, anchor="w", padding=3)

# Load Chats
chat1 = ttk.Button(chat_list, text="Chat 1", style="Chat_Button.TButton")
chat1.grid(column=1, row=2, sticky=(W))

chat2 = ttk.Button(chat_list, text="Chat 2", style="Chat_Button.TButton")
chat2.grid(column=1, row=3, sticky=(W))




root.mainloop()