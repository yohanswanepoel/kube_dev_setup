import os

CPU="4"
MEMORY="20g"
DISK="50g"
#RUNTIME="cri-o"
RUNTIME="docker"
PROFILE="minikube"
NETWORK="vibr1"


# TODO Check if profile exists


ADDONS=["dashboard","metrics-server","registry","ingress","ingress-dns"]

# Do Minikube Setup
os.system("minikube profile {}".format(PROFILE))
os.system("minikube config set memory {}".format(MEMORY))
os.system("minikube config set cpus {}".format(CPU))
os.system("minikube config set disk-size {}".format(DISK))
#os.system("minikube config set container-runtime {}".format(RUNTIME))

os.system("minikube start")

for addon in ADDONS:
    os.system("minikube addons enable {}".format(addon))

# TODO network setup for ingress-dns
os.system("sudo systemd-resolve --interface {} --set-dns $(minikube ip) --set-domain test".format(NETWORK))
