#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
import logging

import requests


CALAMARI_HOST = 'http://127.0.0.1/'
CALAMARI_USERNAME = 'root'
CALAMARI_PASSWORD = 'root'

LOG = logging.getLogger(__name__)


def addStdoutHandler(logger):
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.DEBUG)
    sh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(sh)


class CalamariGraphiteMixin(object):
    """
    Graph data fetch methods from calamari frontend (romana)
    """

    def graphite_data_get(self, params):
        """
        Base method to fetch graph data

        :arg params: list of two-element tuples, not dict
        """
        params.append(('format', 'json-array'))
        data = self.get('/graphite/render/', params=params)
        return data.json()   # {'targets': ['a', 'b'], 'datapoints': [[1453947000, 1, 2], ...]}

    def graphite_metrics_find(self, query):
        """
        Search for specific metrics (CPU/disk/NIC names of a server)
        """
        data = self.get('/graphite/metrics/find', params={'query': query})
        try:
            data = data.json()
        except: # if data format error, need re-auth
            self.authenticate()
            data = self.get('/graphite/metrics/find', params={'query': query})
            data = data.json()
        return data

    def iops_data(self, cluster_id, pool_id='all', time_from='-1d'):
        """
        IOPS of a pool / pools aggretate [Cluster-Level]

        :arg pool_id: if not given, 'all' means pool aggretate IOPS
        :arg time_from: -1hour / -12hour / -1d / -3d / -7d
                        time_from <= 24h, 1min/point
                        time_from > 24h, 15min/point
        """
        params = []
        params.append(('target', 'ceph.cluster.%s.pool.%s.num_read' % (cluster_id, pool_id)))
        params.append(('target', 'ceph.cluster.%s.pool.%s.num_write' % (cluster_id, pool_id)))
        params.append(('from', time_from))
        return self.graphite_data_get(params=params)

    def disk_usage_data(self, cluster_id, time_from='-1d'):
        """
        Disk usage of all pools total [Cluster-Level]

        :arg time_from: -1hour / -12hour / -1d / -3d / -7d
        """
        params = []
        params.append(('target', 'sumSeries(scale(ceph.cluster.%s.df.total_avail,1024), ceph.cluster.%s.df.total_avail_bytes)' % (cluster_id, cluster_id)))
        params.append(('target', 'sumSeries(scale(ceph.cluster.%s.df.total_used,1024), ceph.cluster.%s.df.total_used_bytes)' % (cluster_id, cluster_id)))
        params.append(('from', time_from))
        return self.graphite_data_get(params=params)

    def server_cpu_data(self, fqdn, time_from='-1d'):
        """
        CPU usage summary of a server [Server-Level]

        :arg fdqdn: Fully qualified domain name of a server from v2 api
        :arg time_from: -1hour / -12hour / -1d / -3d / -7d
        """
        params = []
        params.append(('target', 'servers.%s.cpu.total.system' % (fqdn, )))
        params.append(('target', 'servers.%s.cpu.total.user' % (fqdn, )))
        params.append(('target', 'servers.%s.cpu.total.idle' % (fqdn, )))
        params.append(('from', time_from))
        return self.graphite_data_get(params=params)

    def server_loadavg_data(self, fqdn, time_from='-1d'):
        """
        Load average summary of a server [Server-Level]

        :arg fdqdn: Fully qualified domain name of a server from v2 api
        :arg time_from: -1hour / -12hour / -1d / -3d / -7d
        """
        params = []
        params.append(('target', 'servers.%s.loadavg.01' % (fqdn, )))
        params.append(('target', 'servers.%s.loadavg.05' % (fqdn, )))
        params.append(('target', 'servers.%s.loadavg.15' % (fqdn, )))
        params.append(('from', time_from))
        return self.graphite_data_get(params=params)

    def server_memory_data(self, fqdn, time_from='-1d'):
        """
        Memory usage summary of a server [Server-Level]

        :arg fdqdn: Fully qualified domain name of a server from v2 api
        :arg time_from: -1hour / -12hour / -1d / -3d / -7d
        """
        params = []
        params.append(('target', 'servers.%s.memory.Active' % (fqdn, )))
        params.append(('target', 'servers.%s.memory.Buffers' % (fqdn, )))
        params.append(('target', 'servers.%s.memory.Cached' % (fqdn, )))
        params.append(('target', 'servers.%s.memory.MemFree' % (fqdn, )))
        params.append(('from', time_from))
        return self.graphite_data_get(params=params)

    def server_cpu_detail_data(self, server_cpu_id, time_from='-1d'):
        """
        Detailed usage of a CPU [CPU-Level]

        :arg server_cpu_id: id in [x['id'] for x in 
            self.graphite_metrics_find('servers.%s.cpu.*' % fqdn)]
        :arg time_from: -1hour / -12hour / -1d / -3d / -7d
        """
        # 注：上面拿到的列表里包括一个特例叫total
        params = []
        params.append(('target', '%s.system' % (server_cpu_id, )))
        params.append(('target', '%s.user' % (server_cpu_id, )))
        params.append(('target', '%s.nice' % (server_cpu_id, )))
        params.append(('target', '%s.idle' % (server_cpu_id, )))
        params.append(('target', '%s.iowait' % (server_cpu_id, )))
        params.append(('target', '%s.irq' % (server_cpu_id, )))
        params.append(('target', '%s.softirq' % (server_cpu_id, )))
        params.append(('target', '%s.steal' % (server_cpu_id, )))
        params.append(('from', time_from))
        return self.graphite_data_get(params=params)

    def server_disk_detail_data(self, server_disk_id, time_from='-1d'):
        """
        Detailed usage of a disk [Disk-Level]

        :arg server_cpu_id: id in [x['id'] for x in 
            self.graphite_metrics_find('servers.%s.iostat.*' % fqdn)]
        :arg time_from: -1hour / -12hour / -1d / -3d / -7d
        """
        # 注：上面拿到的列表里磁盘和分区都会有，比如一块盘的话会有一个vda和一个vda1
        params = []
        # io bytes/s
        params.append(('target', '%s.read_byte_per_second' % (server_disk_id, )))
        params.append(('target', '%s.write_byte_per_second' % (server_disk_id, )))
        # await
        params.append(('target', '%s.read_await' % (server_disk_id, )))
        params.append(('target', '%s.write_await' % (server_disk_id, )))
        # iops
        params.append(('target', '%s.iops' % (server_disk_id, )))
        params.append(('from', time_from))
        return self.graphite_data_get(params=params)

    def server_network_detail_data(self, server_cpu_id, time_from='-1d'):
        """
        Detailed usage of a NIC [NIC-Level]

        :arg server_cpu_id: id in [x['id'] for x in 
            self.graphite_metrics_find('servers.%s.network.*' % fqdn)]
        :arg time_from: -1hour / -12hour / -1d / -3d / -7d
        """
        params = []
        # bytes
        params.append(('target', '%s.tx_byte' % (server_cpu_id, )))
        params.append(('target', '%s.rx_byte' % (server_cpu_id, )))
        # Packets
        params.append(('target', '%s.tx_packets' % (server_cpu_id, )))
        params.append(('target', '%s.rx_packets' % (server_cpu_id, )))
        params.append(('target', '%s.tx_errors' % (server_cpu_id, )))
        params.append(('target', '%s.rx_errors' % (server_cpu_id, )))
        params.append(('target', '%s.tx_drops' % (server_cpu_id, )))
        params.append(('target', '%s.rx_drops' % (server_cpu_id, )))
        params.append(('from', time_from))
        return self.graphite_data_get(params=params)


class CalamariConnection(requests.Session):
    """
    Base connection for Calamari backend with authentication
    """
    def __init__(self, host, username, password, api_version):
        self.host = host.rstrip('/')
        self.username = username
        self.password = password
        self.api_version = api_version.strip('/')
        super(CalamariConnection, self).__init__()

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.host)

    def get_api_path(self, url):
        return 'api/%s/%s' % (
            self.api_version,
            url.lstrip('/'))

    def authenticate(self):
        LOG.info('Calamari %s connection re-authenticated.', self.api_version)
        url = '%s/%s' % (self.host, self.get_api_path('auth/login'))
        data = {'username': self.username, 'password': self.password}
        return super(CalamariConnection, self).post(url, data=data)

    def get(self, url, *args, **kwargs):
        url = '%s/%s' % (self.host, url.lstrip('/'))
        LOG.debug('Request for %s', url)
        resp = super(CalamariConnection, self).get(url, *args, **kwargs)
        if resp.status_code == 403:
            self.authenticate()
            resp = super(CalamariConnection, self).get(url, *args, **kwargs)
        return resp

    def api_get(self, url, *args, **kwargs):
        url = self.get_api_path(url)
        return self.get(url, *args, **kwargs)


class CalamariAPIv1Connection(CalamariConnection, CalamariGraphiteMixin):
    """
    For v1 APIs only

    v1 API list: https://github.com/ceph/calamari/blob/master/rest-api/calamari_rest/urls/v1.py
    """
    def __init__(self, host, username, password):
        super(CalamariAPIv1Connection, self).__init__(host, username, password, 'v1')


class CalamariAPIv2Connection(CalamariConnection, CalamariGraphiteMixin):
    """
    For v2 APIs only

    v2 API list: http://calamari.readthedocs.org/en/latest/calamari_rest/resources/resources.html
    """
    def __init__(self, host, username, password):
        super(CalamariAPIv2Connection, self).__init__(host, username, password, 'v2')


v1_connection = CalamariAPIv1Connection(CALAMARI_HOST, CALAMARI_USERNAME, CALAMARI_PASSWORD)
v2_connection = CalamariAPIv2Connection(CALAMARI_HOST, CALAMARI_USERNAME, CALAMARI_PASSWORD)


addStdoutHandler(LOG)

