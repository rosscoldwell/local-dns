import logging
import socket
import sys
from time import sleep
from zeroconf import IPVersion, ServiceInfo, Zeroconf


def register_services(services):
    zeroconf = Zeroconf(ip_version=IPVersion.V4Only)
    service_infos = []

    for hostname, ip_address in services.items():
        # Ensure the hostname ends with '.local.'
        if not hostname.endswith(".local."):
            hostname += ".local."

        # Create a unique service name
        service_name = f"{hostname[:-1]}._http._tcp.local."

        # Create a ServiceInfo object
        service_info = ServiceInfo(
            "_http._tcp.local.",
            service_name,
            addresses=[socket.inet_aton(ip_address)],
            port=80,
            properties={},
            server=hostname,
        )

        # Register the service
        zeroconf.register_service(service_info)
        service_infos.append(service_info)

        print(f"Registered {service_name} with IP {ip_address}")

    return zeroconf, service_infos


def main():
    logging.basicConfig(level=logging.DEBUG)

    services = {
        "nas": "192.168.0.245",
        "proxmox": "192.168.0.150",  # port 8006
        # Add more hostnames and IP addresses as needed
    }

    zeroconf, service_infos = register_services(services)

    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        # Unregister the services and close the Zeroconf object
        for service_info in service_infos:
            zeroconf.unregister_service(service_info)
        zeroconf.close()


if __name__ == "__main__":
    main()