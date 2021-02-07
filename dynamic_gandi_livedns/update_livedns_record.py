from os import environ
from asyncio import run, get_running_loop
from aiohttp import ClientSession
from aiodns import DNSResolver
from socket import AF_INET, AF_INET6
import json

ADDON_CONFIG_FILE_LOCATION = "/data/options.json"
SUPERVISOR_API_URL = "http://supervisor"
LIVEDNS_API_URL = "https://api.gandi.net/v5/livedns"

addon_config = None
with open(ADDON_CONFIG_FILE_LOCATION) as addon_config_file:
    addon_config = json.load(addon_config_file)

supervisor_api_access_token = environ.get('SUPERVISOR_TOKEN')
supervisor_api_request_headers = {
    "Authorization": f"Bearer {supervisor_api_access_token}",
    "Content-Type": "application/json",
}

livedns_api_request_headers = {
    "Authorization": f"Apikey {addon_config['api_key']}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}


async def main():
    print(addon_config['update_interval'])

    default_dns_resolver = DNSResolver(loop=get_running_loop())
    opendns_resolver_ip = await default_dns_resolver.gethostbyname('resolver4.opendns.com', AF_INET)

    opendns_resolver = DNSResolver(
        loop=get_running_loop(), nameservers=opendns_resolver_ip.addresses)
    [myip_record] = await opendns_resolver.query('myip.opendns.com', 'A')
    print(myip_record.host)

    async with ClientSession(headers=supervisor_api_request_headers) as session:
        resp = await session.get(f"{SUPERVISOR_API_URL}/network/info")
        print("HTTP response status code", resp.status)
        print("HTTP response JSON content", await resp.json())

    async with ClientSession(headers=livedns_api_request_headers) as session:
        resp = await session.get(f"{LIVEDNS_API_URL}/domains/{addon_config['domain']}/records/{addon_config['subdomain']}/A")
        record = await resp.json()

        previous_ip = record['rrset_values'][0]

        if previous_ip != myip_record.host:
            print(
                f"Pointing record {addon_config['subdomain']}.{addon_config['domain']} to '{myip_record.host}' (was: {previous_ip})")
            record['rrset_values'][0] = myip_record.host
            await session.put(record['rrset_href'], json=record)
        else:
            print(
                f"Record {addon_config['subdomain']}.{addon_config['domain']} is already up-to-date ({previous_ip})")

run(main())
