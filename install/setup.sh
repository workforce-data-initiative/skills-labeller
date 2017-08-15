# this file in flux while repository being built out

# Assumes AWS, firewall on, otherwise this machine may expose unncessary ports
# to the intertubes...
sudo apt update
sudo apt-get install build-essential python-dev git

# Python
sudo apt-git install python-pip python-virtualenv python-numpy python-matplotlib

# Redis
sudo apt-get install redis-server

# Install mongodb
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv EA312927
echo "deb http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.2 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.2.list
sudo apt-get update
sudo apt-get install -y mongodb-org
