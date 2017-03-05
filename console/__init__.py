from tkinter import Tk, Button, Frame, Label, Entry 
from tkinter import LEFT, BOTTOM, TOP, RIGHT
from tkinter import END

from multiprocessing import cpu_count
from server.NIOServer import Server
from server.message_forwarder import forward_messages
from server.message_processor import process_messages
from common.humansize import approximate_size

class Console:
    def __init__(self):
        self.handler_number_template = "Handler {0}:"
        self.clients_count_template=" {0} clients |"
        self.received_template="received {0} |"
        self.sent_template = "sent {0}"        
        
        self.handler_labels={}
        
        self.cpu_cnt = cpu_count()
        self.handler_cnt = self.cpu_cnt
        self.listening_port=10000
        self.stop_updating=False
        self.server = Server(self.listening_port,self.handler_cnt, False, forward_messages, process_messages)
        
        self.root = Tk()
        self.root.wm_title("Server console")
        
        #input for number of handlers
        handler_frame = Frame(self.root)
        
        handler_label = Label(handler_frame, text="Number of handlers:")
        self.n_handlers = Entry(handler_frame)
        self.n_handlers.insert(0, self.cpu_cnt)
        
        handler_label.pack(side=LEFT)
        self.n_handlers.pack(side=LEFT)
        handler_frame.pack(side=TOP, padx=5, pady=5)
        
        #listening port
        fr = Frame(self.root)        
        port_label = Label(fr, text="Listening port:")
        self.port = Entry(fr)
        self.port.insert(0, self.listening_port)
        
        port_label.pack(side=LEFT)
        self.port.pack(side=LEFT)
        fr.pack(padx=5, pady=5)
        
        #handler info        
        self.info_frame = Frame(self.root)
        self.info_frame.pack()
        
        #buttons for stopping and starting the server
        frame = Frame(self.root)
        self.start_btn = Button(frame, text="Start", command=self.start)
        self.shutdown_btn = Button(frame, text="Shutdown", command=self.shutdown, state="disabled")
        
        self.start_btn.pack(side=LEFT)
        self.shutdown_btn.pack(side=LEFT)
        
        frame.pack(side=BOTTOM, padx=5, pady=5)
        
        self.root.mainloop()
        
    def start(self):
        try:
            n_handlers = int(self.n_handlers.get()) 
            port = int(self.port.get())           
        except Exception as ex:
            # TODO: show some message that user should enter only integers
            print(ex)                
        else:    
            self.listening_port=port
            #destroy old frames with handler info        
            for x in range(0, self.handler_cnt):
                try:
                    frame = self.handler_labels[x]["frame"]
                except KeyError as ex:
                    pass
                else:
                    frame.destroy()
            
            #more handlers than core count does not achieve much
            if n_handlers>self.cpu_cnt:
                self.handler_cnt=self.cpu_cnt                
                self.n_handlers.delete(0, END)
                self.n_handlers.insert(0, self.handler_cnt)
            else:
                self.handler_cnt=n_handlers
            
            info_frame = self.info_frame
            
            #create new handler info frames for each handler
            for x in range(0, self.handler_cnt):
                frame = Frame(info_frame)
                handler_lbl = Label(frame, text=self.handler_number_template.format(x))
                client_cnt_lbl = Label(frame, text=self.clients_count_template)
                received_lbl = Label(frame, text=self.received_template)
                sent_lbl = Label(frame, text=self.sent_template)
                
                handler_lbl.pack(side=LEFT)
                client_cnt_lbl.pack(side=LEFT)
                received_lbl.pack(side=LEFT)
                sent_lbl.pack(side=LEFT)
                
                labels = {}
                labels["frame"]=frame
                labels["handler"]=handler_lbl
                labels["clients"]=client_cnt_lbl
                labels["received"]=received_lbl
                labels["sent"]=sent_lbl
                
                self.handler_labels[x]=labels
                
                frame.pack(padx=5, pady=1)            
            
            self.server.set_port(self.listening_port)
            self.server.set_n_handlers(self.handler_cnt)
            self.server.start()
            self.stop_updating=False
            self.update_info()
            
            self.start_btn.config(state="disabled")
            self.shutdown_btn.config(state="normal")
        pass
    
    def shutdown(self):
        self.server.shutdown()
        self.stop_updating=True
        
        self.start_btn.config(state="normal")
        self.shutdown_btn.config(state="disabled")
    
    def update_info(self):        
        if not self.stop_updating:
            for x in range(0, self.handler_cnt):            
                cnt = self.server.client_count(x)
                
                label = self.handler_labels[x]["clients"]
                label.config(text=self.clients_count_template.format(cnt))
                
                total_received = self.server.total_received(x)
                label = self.handler_labels[x]["received"]
                label.config(text=self.received_template.format(approximate_size(total_received, True)))
                
                total_sent = self.server.total_sent(x)
                label = self.handler_labels[x]["sent"]
                label.config(text=self.sent_template.format(approximate_size(total_sent, True)))
            
            self.root.after(1000, self.update_info)
        
if __name__=="__main__":
    console = Console()
        