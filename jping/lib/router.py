"""Implements several classes for interacting with routers.
"""
import base64
from jnpr.junos import Device
from os import getenv


class Router(object):
    """Base class for routers.

    Implements high-level attributes.
    Raises errors on attributes and methods that are not generic.

    :attr:`hostname`: router hostname
    :attr:`user`: user for logging into `hostname`
    :attr:`password`: password for logging into `hostname`
    :attr:`timeout`: time to wait for a response
    :attr:`connection`: connection to `hostname`
    """
    @property
    def arp_table(self):
        """A list of ARP entries.

        :raises AttributeError: Base class doesn't implement this.
        """
        raise AttributeError('{} does not implement attribute {}'
                             .format(self.__class__.__name__, repr('arp_table')))

    def __init__(self, *args, **kwargs):
        self.hostname = args[0] if len(args) else kwargs.get('host')
        self.user = kwargs.get('user', getenv('USER'))
        self.password = kwargs.get('password')
        self.timeout = kwargs.get('timeout')
        self.connection = self._connect()
        self.password = base64.b64encode(self.password)

    def __enter__(self):
        return self

    def __exit__(self, exctype, excisnt, exctb):
        self.connection.close()

    def _connect(self):
        """Connect to a device.

        :raises NotImplementedError: Base class doesn't implement this.
        """
        raise NotImplementedError('{} does not implement method {}'
                                  .format(self.__class__.__name__, repr('_connect')))

    def ping(self, *args, **kwargs):
        """Ping an IP.

        :raises NotImplementedError: Base class doesn't implement this.
        """
        raise NotImplementedError('{} does not implement method {}'
                                  .format(self.__class__.__name__, repr('ping')))


class Juniper(Router):
    """Subclass for Juniper Networks devices.

    Implements Juniper-specific details.

    :attr:`hostname`: router hostname
    :attr:`user`: user for logging into `hostname`
    :attr:`password`: password for logging into `hostname`
    :attr:`timeout`: time to wait for a response
    :attr:`connection`: connection to `hostname`
    :attr:`arp_table`: a list of ARP entries
    """
    def _connect(self):
        """Connect to a device.

        :returns: a connection to a Juniper Networks device.
        :rtype: ``Device``
        """
        dev = Device(self.hostname, user=self.user, password=self.password)
        dev.open()
        dev.timeout = self.timeout
        return dev

    @property
    def arp_table(self):
        """A list of ARP entries.

        :returns: returns ARP entries
        :rtype: list
        """
        table = []
        old_table = self.connection.rpc.get_arp_table_information()
        for old_entry in old_table:
            if old_entry.tag != 'arp-table-entry':
                continue
            entry = dict(ip_address=old_entry.findtext('ip-address').strip(),
                         interface=old_entry.findtext('interface-name').strip(),
                         hostname=self.hostname.strip())
            table.append(entry)
        return table

    def ping(self, *args, **kwargs):
        """Ping an IP.

        :param host: IP or hostname of the host to ping
        :type host: string or unicode
        :param count: number of times to ping the host
        :type count: integer
        :returns: success or failure
        :rtype: bool
        """
        host = args[0] if len(args) else kwargs.get('host')
        count = str(kwargs.get('count', 5))
        results = self.connection.rpc.ping(host=host, count=count, rapid=True)
        results = results.find('ping-success')
        if results is not None:
            results = True
        else:
            results = False
        return results
