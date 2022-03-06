Docker runs server-plus.py and to connect use client-plus.py

Not a pro with python console outputs so thread messages overlap with client console interface
when running a client you first enter yout name, and then you gain access to console:
"connect" allows to enter ip and port to reach the server
"move" allows to change voice chat rooms
"disconnect" closes connection

voice is detected automatically with amplitude through input rms

Due to no gui present, all notifications are written in the console. This includes active speakers and room member updates.

Known errors (not required directly in the task):
-- non-unique names lead to UB
-- reconnection after a disconnect is impossible
-- audio buffer is unstable in the first second of speech (but still delivers most of the sound)
