from socket import *

class CN_Socket(socket):
    """\
CN_Socket subclasses standard Python 3 socket class 
to add support for keyboard interrupt (ctl-C) 
"""
    
    def __exit__(self,argException,argString,argTraceback):
        
        if argException is KeyboardInterrupt:
            #print (argString)
            self.close()   # return socket resources on ctl-c keyboard interrupt
            return True
        
        else:  # invoke normal socket context manager __exit__
            super().__exit__(arg.Exception,argString,argTraceback)

    

