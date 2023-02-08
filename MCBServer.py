import subprocess
import time

from Settings import *

shutdownTimer = 0
while True:
    time.sleep(30)
    activeConnectionsCount = 0
    for port in TCP_PORTS:
        activeConnections = subprocess.check_output(['netstat', '-anp']).decode('utf-8').splitlines()
        for line in activeConnections:
            if line.count(':' + str(port)) > 0 and line.count('ESTABLISHED') > 0:
                activeConnectionsCount = activeConnectionsCount + 1
    print('Found ' + str(activeConnectionsCount) + ' active connections')
    if activeConnectionsCount == 0:
        shutdownTimer = shutdownTimer + 1
    else:
        shutdownTimer = 0
    if shutdownTimer * 30 > 60 * 5:
        print('Active connection timer exceeded, shutting down.')
        subprocess.call(['shutdown', '-h', 'now'])
