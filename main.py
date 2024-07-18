import logging
import socket
from time import sleep
from zeroconf import IPVersion, ServiceInfo, Zeroconf
import pandas as pd
import schedule
import time

CSV_URL = 'https://raw.githubusercontent.com/rosscoldwell/local-dns/main/services.csv'

def read_services_from_csv(csv_url):
    services = {}
    try:
        df = pd.read_csv(csv_url)
        for index, row in df.iterrows():
            services[row['hostname']] = row['ip_address']
    except Exception as e:
        logging.error(f"Error reading {csv_url}: {e}")
    return services

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

def reload_services():
    global services, zeroconf, service_infos

    new_services = read_services_from_csv(CSV_URL)

    # Compare current services with new services
    if new_services != services:
        logging.info("Updating services...")
        # Unregister current services
        for service_info in service_infos:
            zeroconf.unregister_service(service_info)
        zeroconf.close()

        # Register new services
        services = new_services
        zeroconf, service_infos = register_services(services)
        logging.info("Services updated.")

def schedule_reload():
    # Schedule reload_services() to run every day at 2:00 AM
    schedule.every().day.at("02:00").do(reload_services)

    # Run pending tasks in schedule
    while True:
        schedule.run_pending()
        time.sleep(1)

def main():
    global services, zeroconf, service_infos
    logging.basicConfig(level=logging.DEBUG)

    # Read initial services from CSV
    services = read_services_from_csv(CSV_URL)

    zeroconf, service_infos = register_services(services)

    try:
        # Schedule reload of services daily
        schedule_reload()

    except KeyboardInterrupt:
        pass
    finally:
        # Unregister the services and close the Zeroconf object
        for service_info in service_infos:
            zeroconf.unregister_service(service_info)
        zeroconf.close()

if __name__ == "__main__":
    main()
