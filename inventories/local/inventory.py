#!/usr/bin/env python

import os
import json
import argparse
import subprocess
import sys
import libvirt

def main():
    inventory = {'all': {'hosts': [],
                         'vars': {'ansible_user': os.environ['USER']}},
                 'cluster': {'hosts': [],
                             'vars': {'cluster_netmask': '255.255.0.0',
                                      'cluster_broadcast': '10.0.255.255'}}}
    inventory['host'] = {'hosts': ['localhost'],
                         'vars': {'ansible_python_interpreter':
                                  '/usr/bin/python2'}}
    inventory['master'] = master()
    inventory['node'] = node()

    hostvars = {}
    for type in ['master', 'node']:
        for host in inventory[type]['hosts']:
            num = int(filter(str.isdigit, host))
            inventory['all']['hosts'].append(host)
            inventory['cluster']['hosts'].append(host)
            hostvars[host] = {'name': host,
                              # Pick the first master as the master.
                              'master': inventory['master']['hosts'][0],
                              'cluster_node_ip': '10.0.0.%d' % num}

    # noqa https://github.com/ansible/ansible/commit/bcaa983c2f3ab684dca6c2c2c8d1997742260761
    inventory['_meta'] = {'hostvars': hostvars}

    parser = argparse.ArgumentParser(description="KVM inventory")
    parser.add_argument('--list', action='store_true',
                        help="List KVM inventory")
    parser.add_argument('--host', help='List details of a KVM inventory')
    args = parser.parse_args()

    if args.list:
        print(json.dumps(inventory))
    elif args.host:
        print(json.dumps(hostvars.get(args.host, {})))


def master():
    master = {'hosts': [],
              'vars': {'ansible_python_interpreter': '/usr/bin/python'}}

    c = libvirt.openReadOnly("qemu:///system")
    if c != None:
        for i in c.listDomainsID():
            dom = c.lookupByID(i)
            if dom.name().startswith('kube') == True:
                master['hosts'].append(dom.name())

    return master


def node():
    node = {'hosts': [],
            'vars': {'ansible_python_interpreter': '/usr/bin/python'}}

    c = libvirt.openReadOnly("qemu:///system")
    if c != None:
        for i in c.listDomainsID():
            dom = c.lookupByID(i)
            if dom.name().startswith('node'):
                node['hosts'].append(dom.name())

    return node


if __name__ == "__main__":
    main()
