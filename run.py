import subprocess

def exec_cmd(cmd):
    return subprocess.check_output(cmd.split(" "), universal_newlines=True)

output = exec_cmd("uname -r")

vers_number = output[0:3]

print("For kernel version", output.replace("\n", ""), ", we get ", vers_number)

print("Grabbing webpage...")
webpage = exec_cmd("curl https://www.kernel.org/")

import re

regex = "https://cdn\.kernel\.org.+?linux-"+vers_number+".+?\.tar.xz"

link = re.search(regex, webpage).group(0)

print("Found link in webpage:", link)
print("Downloading link...")

download_string = "curl -o kernel.tar.xz "+link
download = exec_cmd(download_string)

print("Unzipping...")

import tarfile

with tarfile.open('kernel.tar.xz') as f:
    f.extractall('.')
    pass
    
import os

dirs = os.listdir(".")

for dir in dirs:
    if dir.startswith("linux-"+vers_number):
        os.rename(dir, "kernel")
        
print("Grabbing drivers/net/wireless/mediatek/mt7601u...")

move = exec_cmd("mv kernel/drivers/net/wireless/mediatek/mt7601u/* .")

wd = os.getcwd()
os.chdir("./mt7601u")

print("Erasing out buggy functions")

with open("phy.c", "r") as phy_c:
    x1 = re.sub(r"ret = mt7601u_mcu_calibrate\(dev, MCU_CAL_RXIQ, 0\);[\s\S]+?return ret;", "", "".join(phy_c.readlines()))
    x2 = re.sub(r"ret = mt7601u_mcu_calibrate\(dev, MCU_CAL_DPD, dev->dpd_temp\);[\s\S]+?return ret;", "", x1)
    x3 = re.sub(r"mt7601u_mcu_calibrate\(dev, MCU_CAL_DPD, dev->curr_temp\);", "", x2);
    
with open("phy.c", "w") as phy_c:
    phy_c.write(x3)

print("Make-ing driver")
make = subprocess.check_output("make -C /lib/modules/$(uname -r)/build M=$(pwd) modules", shell=True, universal_newlines=True)

rmmod = exec_cmd("rmmod mt7601u")
insmod = exec_cmd("insmod ./mt7601u.ko")

os.chdir(wd)

