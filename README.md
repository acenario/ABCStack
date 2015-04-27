# ABCStack
Custom Network Stack implementation.

Instructions
have laptop on switch
ssh into 192.168.128.103 (Router)
and 192.168.128.101 (Client)

on 103 - run router.py
on 101:
  - run client.py
  - then in another termial run server pychat (AFTER Stack has initialized)
  - in another one run client pychat. 

Cannot run pycaht server until ABC intitailized. Client.py tries to get an IP from the Router and will keep trying until it gets one. Wait until initialization to run PyChat_Server.

list of errors:
-KeyError, should be fine. Just retry sending a message.
  -If there's a Key error as soon as you start a program, then restart the program

-You have to restart the stack before you can restart PyChat Client and Server if you need to

