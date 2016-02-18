#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
import logging

from client import LOG, CalamariAPIv1Connection, CalamariAPIv2Connection


CALAMARI_HOST = 'http://127.0.0.1/'
CALAMARI_USERNAME = 'root'
CALAMARI_PASSWORD = 'root'


def add_stdout_handler(logger):
    logger.setLevel(logging.DEBUG)
    sh = logging.StreamHandler(sys.stdout)
    sh.setLevel(logging.DEBUG)
    sh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(sh)


if __name__ == '__main__':
    add_stdout_handler(LOG)
    v1_connection = CalamariAPIv1Connection(CALAMARI_HOST, CALAMARI_USERNAME, CALAMARI_PASSWORD)
    v2_connection = CalamariAPIv2Connection(CALAMARI_HOST, CALAMARI_USERNAME, CALAMARI_PASSWORD)

    # # v1 APIs manual test
    # print v1_connection.info()
    # for cluster in v1_connection.cluster_list():
    #     # print v1_connection.cluster_health(cluster['id'])
    #     # print v1_connection.cluster_health_counters(cluster['id'])
    #     # print v1_connection.cluster_space(cluster['id'])

    #     # print v1_connection.osd_list(cluster['id'])
    #     # for osd in v1_connection.osd_list(cluster['id'])['osds']:
    #     #     print v1_connection.osd_get(cluster['id'], osd['uuid'])

    #     # print v1_connection.pool_list(cluster['id'])
    #     # for osd in v1_connection.pool_list(cluster['id']):
    #     #     print v1_connection.pool_get(cluster['id'], osd['pool_id'])

    #     # print v1_connection.server_list(cluster['id'])
    #     pass


    # # v2 APIs manual test
    # print v2_connection.info()
    # print v2_connection.event_list()
    # print v2_connection.request_list()
    # for key in v2_connection.key_list():
    #     print v2_connection.key_get(key['id'])
    # for user in v2_connection.user_list():
    #     print v2_connection.user_get(user['id'])
    # print v2_connection.grains()

    # for cluster in v2_connection.cluster_list():
    #     # print v2_connection.cli(cluster['id'], 'version')
    #     # print v2_connection.cluster_get(cluster['id'])

    #     # print v2_connection.cluster_config_list(cluster['id'])
    #     # print v2_connection.cluster_config_get(cluster['id'], 'auth_mon_ticket_ttl')

    #     # print v2_connection.cluster_crush_map(cluster['id'])
    #     # for crush_node in v2_connection.cluster_crush_node_list(cluster['id']):
    #     #     print v2_connection.cluster_crush_node_get(cluster['id'], crush_node['id'])
    #     # print v2_connection.cluster_crush_rule_set(cluster['id'])
    #     # print v2_connection.cluster_crush_rule(cluster['id'])
    #     # for crush_type in v2_connection.cluster_crush_type_list(cluster['id']):
    #     #     print v2_connection.cluster_crush_type_get(cluster['id'], crush_type['id'])
    #     # print v2_connection.cluster_event_list(cluster['id'])

    #     # print v2_connection.cluster_log_tail(cluster['id'], lines=20)['lines']

    #     # for mon in v2_connection.cluster_mon_list(cluster['id']):
    #     #     print v2_connection.cluster_mon_get(cluster['id'], mon['name'])
    #     #     print v2_connection.cluster_mon_status(cluster['id'], mon['name'])

    #     # print v2_connection.cluster_osd_config(cluster['id'])
    #     # for osd in v2_connection.cluster_osd_list(cluster['id']):
    #     #     print v2_connection.cluster_osd_get(cluster['id'], osd['id'])

    #     # for pool in v2_connection.cluster_pool_list(cluster['id']):
    #     #     print v2_connection.cluster_pool_get(cluster['id'], pool['id'])

    #     # print v2_connection.cluster_request_list(cluster['id'])

    #     # for server in v2_connection.cluster_server_list(cluster['id']):
    #     #     print v2_connection.cluster_server_get(cluster['id'], server['fqdn'])

    #     # for sync_object in v2_connection.cluster_sync_object_list(cluster['id']):
    #     #     print v2_connection.cluster_sync_object_get(cluster['id'], sync_object)
    #     pass

    # for server in v2_connection.server_list():
    #     # print v2_connection.server_event_list(server['fqdn'])
    #     # server_log_files = v2_connection.server_log_file_list(server['fqdn'])
    #     # print v2_connection.server_log_file_tail(server['fqdn'], server_log_files[0])

    #     # print v2_connection.server_get(server['fqdn'])
    #     # print v2_connection.server_grains(server['fqdn'])
    #     pass


    # # Graph data interfaces manual test
    # fsid = v2_connection.cluster_list()[0]['id']
    # fqdn = v2_connection.server_list()[0]['fqdn']
    # # print v2_connection.iops_data(fsid, time_from='-12hour')
    # # print v2_connection.disk_usage_data(fsid)
    # # print v2_connection.server_cpu_data(fqdn)
    # # print v2_connection.server_loadavg_data(fqdn)
    # # print v2_connection.server_memory_data(fqdn)

    # # server_cpu_id = v2_connection.graphite_metrics_find('servers.%s.cpu.*' % fqdn)[0]['id']
    # # print v2_connection.server_cpu_detail_data(server_cpu_id)

    # # server_disk_id = v2_connection.graphite_metrics_find('servers.%s.iostat.*' % fqdn)[0]['id']
    # # print v2_connection.server_disk_detail_data(server_disk_id)

    # # server_nic_id = v2_connection.graphite_metrics_find('servers.%s.network.*' % fqdn)[0]['id']
    # # print v2_connection.server_network_detail_data(server_nic_id)

    v1_connection.logout()
    v2_connection.logout()
