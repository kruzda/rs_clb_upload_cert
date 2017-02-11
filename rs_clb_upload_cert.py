#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c)2012 Rackspace US, Inc.

# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from __future__ import print_function

import argparse
import time
import os
import pyrax

parser = argparse.ArgumentParser()
parser.add_argument('domain')
parser.add_argument('clbname')
args = parser.parse_args()

domain = args.domain
clbname = args.clbname
done = False
the_clb_id = False

pyrax.set_setting("identity_type", "rackspace")
creds_file = os.path.expanduser("~/.rackspace_cloud_credentials")
pyrax.set_credential_file(creds_file)

cert_directory = "~/dehydrated/certs/"

cert = open(os.path.expanduser("{0}/{1}/cert.pem".format(cert_directory, domain))).read()
key = open(os.path.expanduser("{0}/{1}/privkey.pem".format(cert_directory, domain))).read()
chain = open(os.path.expanduser("{0}/{1}/chain.pem".format(cert_directory, domain))).read()

clb = pyrax.cloud_loadbalancers

for lb in clb.list():
    if clbname in lb.name:
            the_clb_id = lb.id

if not the_clb_id:
    print("no clb found with the name {0}".format(clbname))
    sys.exit(1)

while not done:
    the_clb = clb.get(the_clb_id)
    if the_clb.status == 'ACTIVE':
        if the_clb.get_ssl_termination() == {}:
            print("no existing ssl_termination, good")
            print("adding new ssl_termination")
            the_clb.add_ssl_termination(securePort = 8082, enabled = True, secureTrafficOnly = True, certificate = cert, privatekey = key, intermediateCertificate = chain)
            done = True
        else:
            print("there is already an ssl_termination here")
            print("getting rid of it!")
            the_clb.delete_ssl_termination()
    else:
        print("clb is in {0} status, waiting..".format(the_clb.status))
        time.sleep(5)

print("done")
