import time, os, errno, copy
import coloredlogs, logging
from pathlib import Path
from datetime import datetime
from time import sleep
import json
import paramiko
import cmd
import time
import sys
import csv


logger = logging.getLogger(__name__)
coloredlogs.install(level='DEBUG', logger=logger)

class Scrape:
    def __init__(self):
        self.__time = datetime.now()
        # Try to load vars from env. If not, load defaults
        self.__client_id = os.environ.get('CLIENT_ID', "default-id")
        self.__cpe_uname = os.environ.get('CPE_UNAME', "root")
        self.__cpe_passwd = os.environ.get('CPE_PASSWD', "root")
        self.__cpe_hostname = os.environ.get('CPE_HOSTNAME', "192.168.1.1")
        self.__interval = int(os.environ.get('INTERVAL', 300))
        self.__output = {}
        self.__output["client_id"] = self.__client_id
        self.__output["datetime"] = str(self.__time)

    def scrape(self):
        try:
            logger.info("Connecting to device....")

            buff = ''
            resp = ''

            bandwidth_dict = {}
            bandwidth_dict[0] = 5
            bandwidth_dict[1] = 10
            bandwidth_dict[2] = 15
            bandwidth_dict[3] = 20
            bandwidth_dict[4] = 25
            bandwidth_dict[5] = 30
            bandwidth_dict[6] = 40
            bandwidth_dict[7] = 50
            bandwidth_dict[8] = 60
            bandwidth_dict[9] = 70
            bandwidth_dict[10] = 80
            bandwidth_dict[11] = 90
            bandwidth_dict[12] = 100
            bandwidth_dict[13] = 200
            bandwidth_dict[14] = 400

            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.__cpe_hostname, username=self.__cpe_uname, password=self.__cpe_passwd)
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            chan = ssh.invoke_shell()

            logger.info("Connected to: " + self.__cpe_uname + "@" + self.__cpe_hostname)

            # turn off paging
            chan.send('terminal length 0\n')
            time.sleep(1)
            resp = chan.recv(9999)
            output = resp.decode('ascii').split(',')

            # get cell data
            chan.send('atcmd /dev/ttyUSB3 at+qeng=\\\"servingcell\\\"')
            chan.send('\n')
            time.sleep(1)
            resp = chan.recv(9999)
            output = resp.decode('ascii').strip().split(',')

            stats = {}

            stats["duplex_mode"] = output[-13].strip('"')
            stats["MCC"] = int(output[-12].strip())
            stats["MNC"] = int(output[-11])
            stats["cell_ID"] = int(output[-10])
            stats["PCID"] = int(output[-9])
            stats["TAC"] = int(output[-8])
            stats["ARFCN"] = int(output[-7])
            stats["band"] = int(output[-6])
            stats["DL_BW"] = bandwidth_dict.get(int(output[-5]))
            stats["RSRP"] = int(output[-4])
            stats["RSRQ"] = int(output[-3])
            stats["SINR"] = int(output[-2])

            # make sure modulation monitoring command is enabled
            chan.send('atcmd /dev/ttyUSB3 at+qnwcfg=\\\"nr5g_dlmcs\\\",1')
            chan.send('\n')
            time.sleep(1)
            resp = chan.recv(9999)
            chan.send('atcmd /dev/ttyUSB3 at+qnwcfg=\\\"nr5g_ulmcs\\\",1')
            chan.send('\n')
            time.sleep(1)
            resp = chan.recv(9999)

            # get modulation data DL
            chan.send('atcmd /dev/ttyUSB3 at+qnwcfg=\\\"nr5g_dlmcs\\\"')
            chan.send('\n')
            time.sleep(1)
            resp = chan.recv(9999)
            output = resp.decode('ascii').strip().split(',')
            stats["DL_MCS"] = int(output[2])
            stats["DL_MOD"] = int(output[3][0])

            # get modulation data UL
            chan.send('atcmd /dev/ttyUSB3 at+qnwcfg=\\\"nr5g_ulmcs\\\"')
            chan.send('\n')
            time.sleep(1)
            resp = chan.recv(9999)
            output = resp.decode('ascii').strip().split(',')
            stats["UL_MCS"] = int(output[2])
            stats["UL_MOD"] = int(output[3][0])

            logger.info("Stats Dump:\n" + json.dumps(stats, indent=2))

            ssh.close()  
            self.__output["rf_stats"] = stats

        except Exception as e:
            logger.error(e)
            logger.warning(
                "There was an error gathering RF stats. Proceeding...")
            pass

   
    def get_output(self):
        return self.__output
    
    def get_time(self):
        return self.__time
    
    def get_interval(self):
        return self.__interval

def check_filename(filename):
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

if __name__ == "__main__":
    Path('/share/scrape.json').touch()
    while True:
        scraper = Scrape()
        # perf.iperf_test()
        scraper.scrape()

        
        scrape_file = "/share/scrape.json"
        log_file = "/log/" + str(scraper.get_time()) + ".json"
        
        logger.info("Exporting logs to " + scrape_file + " and " + log_file)
        check_filename(scrape_file)
        check_filename(log_file)

        with open('%s' % scrape_file, 'w') as f:
            json.dump(scraper.get_output(), f)

        with open('%s' % log_file, 'w') as f:
            json.dump(scraper.get_output(), f)

        logger.info("Complete! Sleeping for " + str(scraper.get_interval()) + " secs.")

        sleep(scraper.get_interval())
