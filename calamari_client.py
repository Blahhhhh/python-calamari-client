#!/usr/bin/env python
#-*- coding: utf-8 -*-

import json
import logging

import requests


LOG = logging.getLogger(__name__)


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

    def server_network_detail_data(self, server_nic_id, time_from='-1d'):
        """
        Detailed usage of a NIC [NIC-Level]

        :arg server_nic_id: id in [x['id'] for x in 
            self.graphite_metrics_find('servers.%s.network.*' % fqdn)]
        :arg time_from: -1hour / -12hour / -1d / -3d / -7d
        """
        params = []
        # bytes
        params.append(('target', '%s.tx_byte' % (server_nic_id, )))
        params.append(('target', '%s.rx_byte' % (server_nic_id, )))
        # Packets
        params.append(('target', '%s.tx_packets' % (server_nic_id, )))
        params.append(('target', '%s.rx_packets' % (server_nic_id, )))
        params.append(('target', '%s.tx_errors' % (server_nic_id, )))
        params.append(('target', '%s.rx_errors' % (server_nic_id, )))
        params.append(('target', '%s.tx_drops' % (server_nic_id, )))
        params.append(('target', '%s.rx_drops' % (server_nic_id, )))
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

    def logout(self):
        LOG.info('Calamari %s connection logout.', self.api_version)
        url = '%s/%s' % (self.host, self.get_api_path('auth/logout'))
        return super(CalamariConnection, self).post(url)

    def get(self, url, *args, **kwargs):
        url = '%s/%s' % (self.host, url.lstrip('/'))
        LOG.debug('GET request for %s', url)
        resp = super(CalamariConnection, self).get(url, *args, **kwargs)
        if resp.status_code == 403:
            self.authenticate()
            resp = super(CalamariConnection, self).get(url, *args, **kwargs)
        return resp

    def post(self, url, *args, **kwargs):
        url = '%s/%s' % (self.host, url.lstrip('/'))
        LOG.debug('POST request for %s', url)
        resp = super(CalamariConnection, self).post(url, *args, **kwargs)
        if resp.status_code == 403:
            self.authenticate()
            resp = super(CalamariConnection, self).post(url, *args, **kwargs)
        return resp

    def api_get(self, url, *args, **kwargs):
        url = self.get_api_path(url)
        response = self.get(url, *args, **kwargs)
        response.raise_for_status()
        return response.json()

    def api_post(self, url, *args, **kwargs):
        url = self.get_api_path(url)
        response = self.post(url, *args, **kwargs)
        response.raise_for_status()
        return response.json()


class CalamariAPIv1Connection(CalamariConnection, CalamariGraphiteMixin):
    """
    For v1 APIs only

    v1 API URL list: https://github.com/ceph/calamari/blob/master/rest-api/calamari_rest/urls/v1.py
    """
    def __init__(self, host, username, password):
        super(CalamariAPIv1Connection, self).__init__(host, username, password, 'v1')

    def info(self):
        return self.api_get('/info')

    def cluster_list(self):
        return self.api_get('/cluster')

    def cluster_health(self, fsid):
        return self.api_get('/cluster/%s/health' % (fsid,))

    def cluster_health_counters(self, fsid):
        return self.api_get('/cluster/%s/health_counters' % (fsid,))

    def cluster_space(self, fsid):
        return self.api_get('/cluster/%s/space' % (fsid,))

    def osd_list(self, fsid):
        return self.api_get('/cluster/%s/osd' % (fsid,))

    def osd_get(self, fsid, osd_id):
        return self.api_get('/cluster/%s/osd/%s' % (fsid, osd_id))

    def pool_list(self, fsid):
        return self.api_get('/cluster/%s/pool' % (fsid,))

    def pool_get(self, fsid, pool_id):
        return self.api_get('/cluster/%s/pool/%s' % (fsid, pool_id))

    def server_list(self, fsid):
        return self.api_get('/cluster/%s/server' % (fsid,))


class CalamariAPIv2Connection(CalamariConnection, CalamariGraphiteMixin):
    """
    For v2 APIs only

    v2 API list: http://calamari.readthedocs.org/en/latest/calamari_rest/resources/resources.html
    v2 API URL list: https://github.com/ceph/calamari/blob/master/rest-api/calamari_rest/urls/v2.py
    """
    def __init__(self, host, username, password):
        super(CalamariAPIv2Connection, self).__init__(host, username, password, 'v2')

    def cli(self, fsid, command):
        """ Ceph CLI access
        """
        data = {'command': command}
        return self.api_post('/cluster/%s/cli' % (fsid,), data=json.dumps(data))

    def cluster_list(self):
        return self.api_get('/cluster')

    def cluster_get(self, fsid):
        return self.api_get('/cluster/%s' % (fsid,))

    def cluster_config_list(self, fsid):
        return self.api_get('/cluster/%s/config' % (fsid,))

    def cluster_config_get(self, fsid, key):
        return self.api_get('/cluster/%s/config/%s' % (fsid, key))

    def cluster_crush_map(self, fsid):
        return self.api_get('/cluster/%s/crush_map' % (fsid,))

    def cluster_crush_node_list(self, fsid):
        return self.api_get('/cluster/%s/crush_node' % (fsid,))

    def cluster_crush_node_get(self, fsid, node_id):
        return self.api_get('/cluster/%s/crush_node/%s' % (fsid, node_id))

    def cluster_crush_rule_set(self, fsid):
        return self.api_get('/cluster/%s/crush_rule_set' % (fsid,))

    def cluster_crush_rule(self, fsid):
        return self.api_get('/cluster/%s/crush_rule' % (fsid,))

    def cluster_crush_type_list(self, fsid):
        return self.api_get('/cluster/%s/crush_type' % (fsid,))

    def cluster_crush_type_get(self, fsid, type_id):
        return self.api_get('/cluster/%s/crush_type/%s' % (fsid, type_id))

    def event_list(self):
        return self.api_get('/event')

    def cluster_event_list(self, fsid):
        return self.api_get('/cluster/%s/event' % (fsid,))

    def server_event_list(self, fqdn):
        return self.api_get('/server/%s/event' % (fqdn,))

    def info(self):
        return self.api_get('/info')

    def cluster_log_tail(self, fsid, lines=10):
        params = {'lines': lines}
        return self.api_get('/cluster/%s/log' % (fsid,), params=params)

    def server_log_file_list(self, fqdn):
        return self.api_get('/server/%s/log' % (fqdn,))

    def server_log_file_tail(self, fqdn, log_path, lines=10):
        params = {'lines': lines}
        return self.api_get('/server/%s/log/%s' % (fqdn, log_path), params=params)

    def cluster_mon_list(self, fsid):
        return self.api_get('/cluster/%s/mon' % (fsid,))

    def cluster_mon_get(self, fsid, mon_id):
        return self.api_get('/cluster/%s/mon/%s' % (fsid, mon_id))

    def cluster_mon_status(self, fsid, mon_id):
        return self.api_get('/cluster/%s/mon/%s/status' % (fsid, mon_id))

    def cluster_osd_config(self, fsid):
        return self.api_get('/cluster/%s/osd_config' % (fsid,))

    def cluster_osd_list(self, fsid):
        return self.api_get('/cluster/%s/osd' % (fsid,))

    def cluster_osd_get(self, fsid, osd_id):
        return self.api_get('/cluster/%s/osd/%s' % (fsid, osd_id))

    def cluster_pool_list(self, fsid):
        return self.api_get('/cluster/%s/pool' % (fsid,))

    def cluster_pool_get(self, fsid, pool_id):
        return self.api_get('/cluster/%s/pool/%s' % (fsid, pool_id))

    def request_list(self, state=None):
        params = {}
        if state:
            params['state'] = state
        return self.api_get('/request', params=params)

    def request_get(self, request_id):
        return self.api_get('/request/%s' % (request_id,))

    def request_cancel(self, request_id):
        return self.api_post('/request/%s/cancel' % (request_id,))

    def cluster_request_list(self, fsid, state=None):
        params = {}
        if state:
            params['state'] = state
        return self.api_get('/cluster/%s/request' % (fsid,), params=params)

    def cluster_request_get(self, fsid, request_id):
        return self.api_get('/cluster/%s/request/%s' % (fsid, request_id))

    def key_list(self):
        return self.api_get('/key')

    def key_get(self, minion_id):
        return self.api_get('/key/%s' % (minion_id,))

    def cluster_server_list(self, fsid):
        return self.api_get('/cluster/%s/server' % (fsid,))

    def cluster_server_get(self, fsid, fqdn):
        return self.api_get('/cluster/%s/server/%s' % (fsid, fqdn))

    def server_list(self):
        return self.api_get('/server')

    def server_get(self, fqdn):
        return self.api_get('/server/%s' % (fqdn,))

    def server_grains(self, fqdn):
        return self.api_get('/server/%s/grains' % (fqdn,))

    def cluster_sync_object_list(self, fsid):
        return self.api_get('/cluster/%s/sync_object' % (fsid,))

    def cluster_sync_object_get(self, fsid, sync_type):
        return self.api_get('/cluster/%s/sync_object/%s' % (fsid, sync_type))

    def user_list(self):
        return self.api_get('/user')

    def user_get(self, pk):
        return self.api_get('/user/%s' % (pk,))

    def grains(self):
        return self.api_get('/grains')
