#!/usr/bin/env python2.7
"""This script pings one or more IP addresses from one or more devices.

The IP addresses are retrieved from the ARP table of the device(s).
"""
import lib.router as router
import lib.utilities as utilities
from os import path
from prettytable import PrettyTable

DATABASE = utilities.DBase()
SETTINGS = utilities.Utils.parse_yaml(path.realpath('etc/settings.yml'))
VENDORS = dict(juniper=router.Juniper, ios=router.CiscoIos)


def main():
    """Primary entry point.

    Parses command-line arguments to determine if the check is pre- or post-change.
    Connects to a Juniper router and queries the ARP table (pre-chagne) or database (post-change).
    """
    args = utilities.Utils.parse_arguments()
    table = None

    for host in SETTINGS['routers']:
        if host['vendor'] not in VENDORS:
            raise AttributeError('Unsupported vendor: {}'.format(host['vendor']))
        connection_args = dict(user=SETTINGS['user'], password=SETTINGS['passwd'])
        NetworkElement = VENDORS[host['vendor']]
        with NetworkElement(host['hostname'], **connection_args) as rtr:
            if args.check == 'post' or args.post:
                heading = ['Router', 'Interface', 'IP Address',
                           'Success on First Run', 'Success on Second Run']
                table = PrettyTable(heading)
                table = post_check(rtr, table)
            elif args.check == 'pre' or args.pre:
                update_arp_database(rtr)
    if table:
        print table


def post_check(rtr, table):
    query = 'SELECT * FROM jping WHERE hostname=?'
    pre_results = DATABASE.query(query, [rtr.hostname])
    pre_results = pre_results.fetchall()
    for result in pre_results:
        post_result = rtr.ping(result['ip_address'])
        hostname = result['hostname']
        interface = result['interface']
        ip_address = result['ip_address']
        pre_result = bool(result['ping_results'])
        row = [hostname, interface, ip_address, pre_result, post_result]
        table.add_row(row)
    return table


def update_arp_database(rtr):
    """Updates the database for the pre-check.

    :param rtr: Juniper Device object.
    :type rtr: ``Device``
    """
    arp_table = rtr.arp_table
    for entry in arp_table:
        entry['ping_results'] = rtr.ping(entry['ip_address'])
        columns = ', '.join(entry.keys())
        placeholders = ', '.join('?' * len(entry))
        query = 'INSERT OR REPLACE INTO jping ({}) VALUES ({})'.format(columns, placeholders)
        DATABASE.query(query, entry.values())


main()
