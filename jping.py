import json
import argparse
import getpass
from pprint import pprint
from lib.encoder import TableJSONEncoder
from jnpr.junos import Device
from jnpr.junos.op.arp import ArpTable

def main():
    args = parse()
    rtr = connect(args.router, args.user, args.password)
    results = get_arp(rtr)
    pprint(results)
def parse():
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
def connect(r, u, p):
    rtr = Device(host=r, user=u, password=p)
    rtr.open()
    return rtr
def get_arp(rtr):
    arp = ArpTable(rtr)
    arp.get()

    arp_json = json.loads(json.dumps(arp, cls=TableJSONEncoder))

    ping_results = []
    results = {}

    for entry in arp_json:
        ping_results.append(rtr.rpc.ping(
            host=arp_json[entry]['ip_address'], count='3', rapid=True))

    for entry in ping_results:
        ip = entry.findtext('target-ip').replace('\n', '')
        results[ip] = {}
        if entry.findtext('ping-success') is not None:
            results[ip]['success'] = True
        else:
            results[ip]['success'] = False
    return results

main()
