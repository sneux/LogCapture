import subprocess
from datetime import datetime
import os

time_created = datetime.now().strftime('%YY-%mM-%dD_%HH-%MM')

p = subprocess.Popen("exec" + ["python3.6", f"sudo tcpdump -i any -w /opt/'log_{time_created}.pcap'"])

max_file_size = 50_000_000

save_flag = 0

while save_flag == False:

    pcap_size = os.path.getsize() # add file for size check

    if pcap_size > 50_000_000:

        save_flag == True

     