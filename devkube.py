import os
import sys
import platform

CPU="4"
MEMORY="20g"
DISK="50g"
#RUNTIME="cri-o"
RUNTIME="docker"
PROFILE="minikube"
DOMAIN="test"

# Check of the profile exists
check_profile = os.popen("minikube profile | grep {}".format(PROFILE)).read().strip()
print(check_profile)
if check_profile != PROFILE:
    # Do Minikube Setup
    os.system("minikube profile {}".format(PROFILE))
    os.system("minikube config set memory {}".format(MEMORY))
    os.system("minikube config set cpus {}".format(CPU))
    os.system("minikube config set disk-size {}".format(DISK))
    #os.system("minikube config set container-runtime {}".format(RUNTIME))
else:
    print("Existing Profile")

# Check if the profile is running
is_started = os.popen("minikube --profile minikube status | grep apiserver").read().strip()
if "Running" in is_started:
    print("Minikube started already - moving on to enabling addons")
else:
    os.system("minikube start")
    
ADDONS=["metrics-server","dashboard","registry","ingress","ingress-dns"]

# This does not hurt to run it again - so just run it
for addon in ADDONS:
    os.system("minikube addons enable {}".format(addon))

# TODO network setup for ingress-dns on MAC

# Linux and mac does it differently
host_os = platform.system()
ip_addr = os.popen("minikube ip".format(PROFILE)).read().strip()
if host_os == "Linux":
    # Get the network name
    # minikube logs | grep "domain minikube has defined MAC address" | tail -1
    # libmachine: (minikube) DBG | domain minikube has defined MAC address 52:54:00:e5:de:d8 in network virbr1
    # virsh domiflist minikube
    vnet = os.popen("virsh domifaddr {} | grep -i {}".format(PROFILE, ip_addr)).read().strip().split()[0]
    bridge = os.popen("virsh domiflist {} | grep -i {}".format(PROFILE, vnet)).read().strip().split()[2]
    # This command is idempotent so no harm  in running it twice
    print("....Setting up local ingress-dns resolution for *.{} to minikube ip: {} on bridge: {}".format(DOMAIN, ip_addr, bridge))
    os.system("sudo systemd-resolve --interface {} --set-dns $(minikube ip) --set-domain {}".format(bridge, DOMAIN))
else:
    # For MacOS
    file_contents = """
        domain {}
        nameserver {}
        search_order 1
        timeout 5
    """.format(DOMAIN, ip_addr)
    os.system("sudo echo '{}' > /etc/resolver/minikube-{}-{}".format(file_contents, PROFILE, DOMAIN))
