"""Implements several classes for interacting with routers.
"""
import base64
from fabric.api import run
from fabric.tasks import execute
from fabric import state
from fabric.context_managers import env as fabric_env
from jnpr.junos import Device
from os import getenv
import logging


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
        if self.connection:
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

        :returns: ARP entries
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


class CiscoIos(Router):
    """Subclass for Cisco IOS devices.

    Implements IOS-specific details.

    :attr:`hostname`: router hostname
    :attr:`user`: user for logging into `hostname`
    :attr:`password`: password for logging into `hostname`
    :attr:`arp_table`: a list of ARP entries
    """
    def __init__(self, *args, **kwargs):
        logging.basicConfig()
        paramiko_logger = logging.getLogger("paramiko.transport")
        paramiko_logger.disabled = True
        state.output['everything'] = False
        state.output['output'] = False
        super(CiscoIos, self).__init__(*args, **kwargs)
        fabric_env.password = base64.b64decode(self.password)

    def _connect(self):
        """Pretend to connect to a device.

        Managing an IOS device through anything pretending to be an API hurts.
        We return `False` here to avoid the parent class exception and attempt to prevent confusion.
        We will use `fabric` to make this work.
        """
        return False

    @property
    def fabric_host(self):
        return '{}@{}'.format(self.user, self.hostname)

    def _get_arp_table(self):
        return run('show ip arp', shell=False)

    @property
    def arp_table(self):
        """A list of ARP entries.

        :returns: ARP entries
        :rtype: list
        """
        table = []
        old_table = execute(self._get_arp_table, hosts=[self.fabric_host])
        old_table = old_table.values()[0]
        old_table = [x.strip() for x in old_table.splitlines() if not x.startswith('Protocol')]
        for old_entry in old_table:
            old_entry = old_entry.split()
            entry = dict(ip_address=old_entry[1],
                         interface=old_entry[5],
                         hostname=self.hostname.strip())
            table.append(entry)
        return table

    def _ping(self, ip=None, count='5'):
        return run('ping {} repeat {}'.format(ip, count), shell=False)

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
        results = execute(self._ping, ip=host, count=count, hosts=[self.fabric_host])
        results = results.values()[0]
        results = results.splitlines()[2]
        if '!' in results:
            results = True
        else:
            results = False
        return results
