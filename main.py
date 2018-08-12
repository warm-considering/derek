from asciimatics.widgets import Frame, ListBox, Layout, Divider, Text, \
    Button, TextBox, Widget, Label
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.event import KeyboardEvent
from asciimatics.exceptions import ResizeScreenError, NextScene, StopApplication
import sys
from user import user
from network import Network
from multiprocessing import Process

curruser = user("NoUser")

class login(Frame):
    def __init__(self, screen):
        super(login, self).__init__(screen,
                                    screen.height * 3//4, 
                                    screen.width * 3//4,                                                                                hover_focus=True,
                                    title="Login")

        self.textbox = Text("Username", "uname")
        self.gobtn = Button("Enter", self.onBtnClick)
        self.quitbtn = Button("Quit", self.quit)
        layout = Layout([100], fill_frame=True)
        layout1 = Layout([1,1])
        self.add_layout(layout)
        self.add_layout(layout1)
        layout1.add_widget(self.quitbtn, 1)
        layout.add_widget(self.textbox)
        layout1.add_widget(self.gobtn, 0)
        self.fix()

    def onBtnClick(self):
        global curruser 
        curruser.name = self.textbox.value
        raise NextScene("Main")
    
    @staticmethod
    def quit():
        raise StopApplication("User Pressed Quit")

class main(Frame):
    def __init__(self, screen):
        super(main, self).__init__(screen,
                                    screen.height * 3//4, 
                                    screen.width * 3//4,                                                                                 
                                    hover_focus=False,
                                    on_load=self.onload,
                                    title="Main")
                
        self.layout1 = Layout([1,3], fill_frame=True)
        self.layout2 = Layout([1,1,1,1])
        self.layout3 = Layout([1,4,1])
        global curruser
        
        self.useradd = Text("Add User", "useradd")
        self.addbtn = Button("Add", self.adduser)
        
        self.quitbtn = Button("Quit", self.quit)                
        
        self.div = Divider(draw_line=True)
        self.chatarea = TextBox(screen.height * 3//4 * 1//2, as_string=True)        
        self.chatarea.disabled = True
        self.chatbox = Text("","message")
        self.sendbtn = Button("Send", self.sendmessage)
        
        self.add_layout(self.layout3)
        self.add_layout(self.layout1)
        self.add_layout(self.layout2)
        self.layout2.add_widget(self.quitbtn, 3)        
        self.layout3.add_widget(self.useradd,1)
        self.layout3.add_widget(self.addbtn,2)
        self.layout1.add_widget(self.chatarea,1)
        self.layout1.add_widget(self.div, 1)
        self.layout1.add_widget(self.chatbox,1)
        self.layout1.add_widget(self.sendbtn,1)
        self.fix()

        self.mqueue = []
    
    def adduser(self):
        remhost = self.useradd.value
        self.NetInt.makeConn(remhost)

    def onload(self):
        self.namelabel = Label(curruser.name)
        self.layout3.add_widget(self.namelabel,0)
        self.fix()
        self.NetInt = Network()
        self.listenThread = Process(target=self.NetInt.createChatConnection)
        self.listenThread.daemon = True
        self.listenThread.start()
        self.messageThread = Process(target=self.NetInt.listenMessage, args=(self.mqueue,))
        self.messageThread.daemon = True
        self.messageThread.start()
        self.putThread = Process(target=self.putmessage)
        self.putThread.daemon = True
        self.putThread.start()
        
    def sendmessage(self):
        if self.chatbox.value != "":
            self.chatarea.value += '\n' + curruser.name + ': ' + self.chatbox.value
            for conn in self.NetInt.connections:
                conn.send('\n' + curruser.name + ': ' + self.chatbox.value)

    def putmessage(self):
        while True:
            if self.mqueue != []:
                self.chatarea.value += self.mqueue.pop(0)


    @staticmethod
    def quit():
        raise StopApplication("User Pressed Quit")

def start(screen, scene):
    scenes = [
        Scene([login(screen)], -1, name="Login"),        
        Scene([main(screen)], -1, name="Main")
    ]    
    screen.play(scenes, stop_on_resize=True, start_scene=scene)

last_scene = None
while True:
    try:
        Screen.wrapper(start, catch_interrupt=True, arguments=[last_scene])
        sys.exit(0)
    except ResizeScreenError as e:
        last_scene = e.scene