Python wrapper for Calamari REST APIs
=====================================

python-calamari-client is a thin Python wrapper for Calamari (`Ceph <http://ceph.com>`_ Manager) REST APIs, based on Python `Requests <http://docs.python-requests.org/en/master/>`_.

Project `Romana <https://github.com/ceph/romana>`_ (former `calamari-clients <https://github.com/ceph/calamari-clients>`_) has already offered a calamari UI for Ceph cluster management. This repo wraps most of the APIs in Romana for development based on Calamari, including

* A client for Calamari V1 APIs
* A client for Calamari V2 APIs
* Interfaces for graph data used in Romana

How to use
----------

.. code-block:: python

    import calamari_client as cc

    # Initialize a v1 client with graphite mixin
    v1_connection = cc.CalamariAPIv1Connection(CALAMARI_HOST, CALAMARI_USERNAME, CALAMARI_PASSWORD)

    # Initialize a v2 client with graphite mixin
    v2_connection = cc.CalamariAPIv2Connection(CALAMARI_HOST, CALAMARI_USERNAME, CALAMARI_PASSWORD)

    # Get Ceph cluster info
    print v2_connection.info()

    # Get cluster iops data in recent 24 hours
    cluster = v2_connection.cluster_list()[0]
    print v2_connection.iops_data(cluster['id'])
