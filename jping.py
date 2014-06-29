#!/usr/bin/env python2.7
import json
import argparse
import getpass
from pprint import pprint
from lib.encoder import TableJSONEncoder
from jnpr.junos import Device
from jnpr.junos.op.arp import ArpTable

def main():
    """Main function that kicks off the script.

    Args:
        router (str):  The network element you want to connect to.
        user (str):  The username you wish to connect as.
        password (bool):  Indicate whether you'll use a password or SSH key.

    Returns:
        int.  The return code::
            0 -- Success
            1 -- Failure

    """
    args = parse()
    rtr = connect(args.router, args.user, args.password)
    results = get_arp(rtr)
    pprint(results)
def parse():
    """Parse script arguments.

    Returns:
        A dict of the arguments passed.

    """
    parser = argparse.ArgumentParser(description="Ping all ARP entries.")
    parser.add_argument("-u", "--user", help="Username", required=True)
    parser.add_argument("-r", "--router",
                        help="Network Element Hostname/IP", required=True)
    parser.add_argument("-p", "--password",
                        help="Password-based login", required=False)
    args = parser.parse_args()
    if args.password is not None:
        args.password = getpass.getpass()
    return args
def connect(hostname, username, passwd):
    """Connect to the device

    Args:
        hostname (str): The device you're connecting to.
        username (str): The username you're authenticating as.
        passwd (str): (Optional) The password you're authenticating with.

    Retruns:
        A jnpr.junos.Device object.

    """
    rtr = Device(host=hostname, user=username, password=passwd)
    rtr.open()
    return rtr
def get_arp(rtr):
    """Get the ARP table/cache and ping all of its entries.
       IPv4 and inet.0 only.

    Args:
        rtr (jnpr.junos.Device): A Device object to use to perform actions.

    Returns:
        dict.  A dict of IPs and their success or failure.  Structure::

            {"10.0.0.1": {"success": True}}

    """
    arp = ArpTable(rtr)
    arp.get()

    arp_json = json.loads(json.dumps(arp, cls=TableJSONEncoder))

    ping_results = []
    results = {}

    for entry in arp_json:
        ping_results.append(rtr.rpc.ping(
            host=arp_json[entry]['ip_address'], count='3', rapid=True))

    for entry in ping_results:
        ip_address = entry.findtext('target-ip').replace('\n', '')
        results[ip_address] = {}
        if entry.findtext('ping-success') is not None:
            results[ip_address]['success'] = True
        else:
            results[ip_address]['success'] = False
    return results

main()
