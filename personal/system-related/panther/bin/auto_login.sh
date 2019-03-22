#!/usr/bin/expect -f

trap {
 set rows [stty rows]
 set cols [stty columns]
 stty rows $rows columns $cols < $spawn_out(slave,name)
} WINCH

spawn /usr/bin/ssh -X z8j@cades-extlogin1.ornl.gov
expect "*password:"
#send "zyt070ab\r"
send "zjy915ha\r"
expect "*#"
interact
