# Pi & OS Version
Pi: Model 3B
Os: Raspberry Pi OS Legacy 32-bit Lite


# SSH
## Configure SSH without a screen
1. – Put the SD card into your computer
....
1. – Navigate to the boot directory
`cd /Volumes/boot`
1. – Create an empty file called ssh
`touch ssh`
2. Insert the SD card into the Pi and power on


## SSH into Pi
`ssh pi@raspberrypi`
Or whatever user was setup for Pi.
Alternatively use ip-address:
`ssh pi@192.168.2.50`


# Transfer Files

## To Pi
`scp f1.txt f2.txt pi@raspberrypi:/path/to/target/dir/`
Will only work when ssh is setup

## From Pi


# Install Python x.y.z


Source: https://itheo.tech/install-python-38-on-a-raspberry-pi

## Step 1
Install required packages
```bash
sudo apt-get update
sudo apt-get install -y build-essential tk-dev libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libsqlite3-dev libssl-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev libffi-dev
```
Compile (yes… it takes a while, grab a coffee and get me one to!!)


## Step 2
Download Python & Compile
```bash
wget https://www.python.org/ftp/python/3.8.0/Python-3.8.0.tar.xz
tar xf Python-3.8.0.tar.xz
cd Python-3.8.0
./configure --enable-optimizations --prefix=/usr
make
```

## Step 3
Let’s install what was compiled!
```bash 
sudo make altinstall
```

## Remove files
And remove the files you don’t need anymore
```bash
cd ..
sudo rm -r Python-3.8.0
rm Python-3.8.0.tar.xz
. ~/.bashrc
```

## Step 4
And yes!!! Let’s make Python 3.8 the default version, make aliases

```bash
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.8 1
And verify:
```

## Step 5
```bash
python -V
```