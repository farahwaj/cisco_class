#!/usr/bin/env python
################################################################################
#                 _    ____ ___   _____           _ _    _ _                   #
#                / \  / ___|_ _| |_   _|__   ___ | | | _(_) |_                 #
#               / _ \| |    | |    | |/ _ \ / _ \| | |/ / | __|                #
#              / ___ \ |___ | |    | | (_) | (_) | |   <| | |_                 #
#        ____ /_/   \_\____|___|___|_|\___/ \___/|_|_|\_\_|\__|                #
#       / ___|___   __| | ___  / ___|  __ _ _ __ ___  _ __ | | ___  ___        #
#      | |   / _ \ / _` |/ _ \ \___ \ / _` | '_ ` _ \| '_ \| |/ _ \/ __|       #
#      | |__| (_) | (_| |  __/  ___) | (_| | | | | | | |_) | |  __/\__ \       #
#       \____\___/ \__,_|\___| |____/ \__,_|_| |_| |_| .__/|_|\___||___/       #
#                                                    |_|                       #
################################################################################
#                                                                              #
# Copyright (c) 2015 Cisco Systems                                             #
# All Rights Reserved.                                                         #
#                                                                              #
#    Licensed under the Apache License, Version 2.0 (the "License"); you may   #
#    not use this file except in compliance with the License. You may obtain   #
#    a copy of the License at                                                  #
#                                                                              #
#         http://www.apache.org/licenses/LICENSE-2.0                           #
#                                                                              #
#    Unless required by applicable law or agreed to in writing, software       #
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT #
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the  #
#    License for the specific language governing permissions and limitations   #
#    under the License.                                                        #
#                                                                              #
################################################################################
"""
It logs in to the APIC and will create the tenant.
"""
import sys
import acitoolkit.acitoolkit as aci
import credentials
from acitoolkit.acisession import Session
from acitoolkit.acitoolkit import Credentials, Tenant, AppProfile, EPG
from acitoolkit.acitoolkit import Context, BridgeDomain, Contract, FilterEntry

# Define static values to pass (edit these if you wish to set differently)
TENANT_NAME = 'Cisco'
APP_NAME = 'WebApp'
EPG_NAME = 'MSsharepoint'
INTERFACE = {'type': 'eth',
             'pod': '1', 'node': '101', 'module': '1', 'port': '35'}
VLAN = {'name': 'vlan5',
        'encap_type': 'vlan',
        'encap_id': '5'}


def main():
    """
    Main create tenant routine
    :return: None
    """
    # Get all the arguments
    description = 'It logs in to the APIC and will create the tenant.'
    creds = aci.Credentials('apic', description)
    creds.add_argument('-t', '--tenant', help='The name of tenant',
                       default=TENANT_NAME)
    args = creds.get()

    # Login to the APIC
    session = aci.Session(args.url, args.login, args.password, subscription_enabled=False)
    resp = session.login()
    if not resp.ok:
        print('%% Could not login to APIC')

    # Create the Tenant
    tenant = aci.Tenant(TENANT_NAME)
    app = aci.AppProfile(APP_NAME, tenant)
    epg = aci.EPG(EPG_NAME, app)
    

    # Create a Context and BridgeDomain
    # Place both EPGs in the Context and in the same BD
    context = Context('VRF-1', tenant)
    bd = BridgeDomain('BD-1', tenant)
    bd.add_context(context)
    epg.add_bd(bd)

    # Define a contract with a single entry
    contract = Contract('mysql-contract', tenant)
    entry1 = FilterEntry('entry1',
                         applyToFrag='no',
                         arpOpc='unspecified',
                         dFromPort='3306',
                         dToPort='3306',
                         etherT='ip',
                         prot='tcp',
                         sFromPort='1',
                         sToPort='65535',
                         tcpRules='unspecified',
                         parent=contract)

    # Provide the contract from 1 EPG 
    epg.provide(contract)
    


    # Create the physical interface object
    intf = aci.Interface(INTERFACE['type'],
                         INTERFACE['pod'],
                         INTERFACE['node'],
                         INTERFACE['module'],
                         INTERFACE['port'])

    # Create a VLAN interface and attach to the physical interface
    vlan_intf = aci.L2Interface(VLAN['name'], VLAN['encap_type'], VLAN['encap_id'])
    vlan_intf.attach(intf)

    # Attach the EPG to the VLAN interface
    epg.attach(vlan_intf)


      # Create the Endpoint
    mac = '00:11:11:11:11:11'
    ip = '10.2.1.4'
    

    # Assign it to the L2Interface
    #ep.attach(vlan_intf)


    # Push the tenant to the APIC
    resp = session.push_to_apic(tenant.get_url(),
                                tenant.get_json())
    
    # Download all of the tenants
    print("-------------------------")
    print("LIST OF AVAILABLE TENANTS")
    print("-------------------------")
    tenants = aci.Tenant.get(session)
    for tenant in tenants:
        print(tenant.name)

    if not resp.ok:
        print('%% Error: Could not push configuration to APIC')
        print(resp.text)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
