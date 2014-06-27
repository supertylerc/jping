# jping [![Build Status](https://travis-ci.org/supertylerc/jping.svg?branch=master)](https://travis-ci.org/supertylerc/jping) [![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/supertylerc/jping/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/supertylerc/jping/?branch=master)

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
