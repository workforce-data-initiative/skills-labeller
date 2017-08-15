# this file in flux while repository being built out

# Assumes AWS, firewall on, otherwise this machine may expose unncessary ports
# to the intertubes...
sudo apt update
sudo -y apt-get install build-essential python-dev git

# Python
sudo -y apt-git install python-pip python-virtualenv python-numpy python-matplotlib

# Redis
sudo -y apt-get install redis-server

# Install mongodb
sudo -y apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv EA312927
sudo echo "deb http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.2 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.2.list
sudo -y apt-get update
sudo -y apt-get install -y mongodb-org
