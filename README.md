# Deprecation Notice #

This script will be deprecated.  It will be rewritten in Python to take advantage of
the [junos-eznc](https://github.com/Juniper/py-junos-eznc) module.

# Installation #
1.  Change `user` and `pass` in the `creds` file to your username and password.
2.  Make `jping.pl` executable (in Linux/OS X/BSD, open a terminal and type `chmod 700 jping.pl`).
3.  If there are routing-instances you want to ignore, open `jping.pl` and edit line `100`.  It can be any regex you want and the script won't ping anything in that routing-instance.

# Usage #
Perform your pre-work check with the command `./jping -ir <CLLI|IP>`.  If you use the CLLI (hostname), it must be one that a DNS server will respond to (which means it may need to be the FQDN).

Perform your post-work check with the command `./jping -pr <CLLI|IP>`.  Same rules apply.

If you performed step `3` in the `Installation`, you can activate the selective dismissal of routing-instances with the `-m` flag.  Example: `./jping -mir 10.1.1.1`.

# License #

BSD 2-Clause

# Author #
Tyler Christiansen
(c) 2013
tylerc@label-switched.net
http://label-switched.net/
@packettalk
