# jping [![Build Status](https://travis-ci.org/supertylerc/jping.svg?branch=master)](https://travis-ci.org/supertylerc/jping) [![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/supertylerc/jping/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/supertylerc/jping/?branch=master)

# Rewritten!

`jping` was initially a flexible [Perl][4] script that parsed
configuration and pinged all possible IP addresses in all configured
subnets in all configured routing-instances.

Doing things this way was expensive, and excluding routing-instances was
not exactly easy.  There's also the problem of screen-scraping.  It's
possible (however unlikely) that the output could change, breaking the
script.

For this reason, `jping` has been rewritten in Python and takes
advantage of `py-junos-eznc` to communicate with Juniper Networks
devices using [NETCONF][5].  This version has been tagged as v0.2.0, and
it is now the preferred version of `jping`.

If you're still looking for the original `jping` written in perl, you
can find it in the [v0.1.0][6] tag.

## About

`jping` is a [python][1] script that connects to devices, retrieves the
ARP table/cache, and pings each of the IP addresses in the cache.

## Installation

### Prerequisites

You need [py-junos-eznc][2].

### Installing

Follow the directions below (or modify as you see fit):

```bash
mkdir $HOME/src && cd $_
git clone https://github.com/supertylerc/jping.git
mkdir $HOME/bin
ln -s $HOME/src/jping/jping.py $HOME/bin/jping
cd
```

### Updating

I recommend that you update regularly.  I run a daily cronjob that
updates all of the repositories I use.  An example:

```bash
15 0 * * * cd /Users/tyler/src/jping && git pull --no-edit --quiet > /dev/null 2>&1
```

Of course, this only works if your machine is actually _on_ at 00:15, so
you'll need to manually update if it's not:

```bash
cd $HOME/src/jping && git pull --no-edit --quiet
```

## Usage

`jping` requires two arguments: a hostname (`-r`) and a username (`-u`).
There is one option: a password (`-p`).  This script uses Python's
[`getpass`][3], so please don't put your password as an argument.

If you do not specify the `-p` argument, SSH keys are assumed.

Example:

```bash
╭─tchristiansen52 at us160536 in ~ using ‹ruby-2.1.1› 14-06-27 - 12:27:51
╰─○ jping -u tyler -r 10.49.31.1
{'10.49.30.1': {'success': True},
 '10.49.30.5': {'success': False},
 '128.0.0.17': {'success': False}}
╭─tchristiansen52 at us160536 in ~ using ‹ruby-2.1.1› 14-06-27 - 12:28:01
╰─○
```

## Author

Tyler Christiansen

## License

BSD 2-Clause

[1]: https://www.python.org/ "Python"
[2]: https://github.com/Juniper/py-junos-eznc "py-junos-eznc"
[3]: https://docs.python.org/2/library/getpass.html "Python getpass"
[4]: http://www.perl.org "Perl"
[5]: https://en.wikipedia.org/wiki/NETCONF "NETCONF"
[6]: https://github.com/supertylerc/jping/tree/v0.1.0 "jping Perl"
