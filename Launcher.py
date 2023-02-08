import boto3
import time
import socket
import struct
import select
from io import BytesIO
from Settings import *

def getInstanceState(ec2):
  running_instances = ec2.describe_instances()
  for r in running_instances['Reservations']:
    for i in r['Instances']:
      if i['InstanceId'] == server_instanceId:
        return i['State']['Name']
  return 'error'

def getAddressTarget(ec2):
  live_addresses = ec2.describe_addresses()
  for r in live_addresses['Addresses']:
    if r['AllocationId'] == ip_allocationId:
      return r['InstanceId']

def recvFixed(conn, size):
    data = bytearray()
    while len(data) < size:
        more = conn.recv(size - len(data))
        if not more:
            raise EOFError()
        data.extend(more)
    return data

def readByte(data):
    if type(data) == socket.socket:
        return struct.unpack('B', data.recv(1))[0]
    else:
        return struct.unpack('B', data.read(1))[0]

def unpack_varint(conn):
    total = 0
    shift = 0
    val = 0x80
    while val&0x80:
        val = readByte(conn)
        total |= ((val&0x7F)<<shift)
        shift += 7
    if total&(1<<31):
        total = total - (1<<32)
    return total

def pack_varint(val):
    total = b''
    if val < 0:
        val = (1<<32)+val
    while val>=0x80:
        bits = val&0x7F
        val >>= 7
        total += struct.pack('B', (0x80|bits))
    bits = val&0x7F
    total += struct.pack('B', bits)
    return total

ec2 = boto3.client('ec2', region_name=server_regionName)

socks = []
for port in TCP_PORTS:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.settimeout(MINECONN_TIMEOUT)
    s.bind((socket.gethostname(), port))
    s.listen(1)
    socks.append(s)

lastReassocTime = time.time()
while True:
    if time.time() > lastReassocTime + REASSOC_TIMEOUT:
        lastReassocTime = time.time()
        print('Attempt reassociation')
        isServerTarget  = getAddressTarget(ec2) == server_instanceId
        isServerRunning = getInstanceState(ec2) == 'running'
        print('isServerTarget: ' + str(isServerTarget))
        print('isServerRunning: ' + str(isServerRunning))

        if (not isServerTarget) and isServerRunning:
            print('Reassociate ip to server')
            ec2.associate_address(AllocationId=ip_allocationId, InstanceId=server_instanceId)
        if isServerTarget and (not isServerRunning):
            print('Reassociate ip to launcher')
            ec2.associate_address(AllocationId=ip_allocationId, InstanceId=launcher_instanceId)

    try:
        read_sockets, write_sockets, error_sockets = select.select(socks, [], [], MINECONN_TIMEOUT)
	if len(read_sockets) > 0:
            conn, addr = read_sockets[0].accept()
            conn.settimeout(MINECONN_TIMEOUT)
            print('Connection address:', addr)

            length = unpack_varint(conn)
            print('len: ' + str(length))
            data = BytesIO(recvFixed(conn, length))
            pid = unpack_varint(data)
            print('pid: ' + str(pid))
            version = unpack_varint(data)
            print('version: ' + str(version))

            length = unpack_varint(conn)
            print('len: ' + str(length))
            data = BytesIO(recvFixed(conn, length))
            pid = unpack_varint(data)
            print('pid: ' + str(pid))

            if (length == 1) and (pid == 0):
                RESP_JSON = RESP_JSON_PREPRO + str(version) + RESP_JSON_POSTPRO
                pid = pack_varint(0)
                jsonlen = pack_varint(len(RESP_JSON.encode('utf-8')))
                length = pack_varint(len(pid) + len(jsonlen) + len(RESP_JSON.encode('utf-8')))
                conn.sendall(length)
                conn.sendall(pid)
                conn.sendall(jsonlen)
                conn.sendall(RESP_JSON.encode('utf-8'))

                length = unpack_varint(conn)
                print('len: ' + str(length))
                data = BytesIO(recvFixed(conn, length))
                pid = unpack_varint(data)
                print('pid: ' + str(pid))
                timestamp = struct.unpack('!q', data.read(8))[0]
                print('timestamp: ' + str(timestamp))

                if (pid == 1):
                    pid = pack_varint(1)
                    length = pack_varint(len(pid) + 8)
                    conn.sendall(length)
                    conn.sendall(pid)
                    conn.sendall(struct.pack('!q', timestamp))

                    instanceState = getInstanceState(ec2)
                    print('Server is in ' + instanceState + ' state')
                    if instanceState == 'stopped':
                        print('Booting server...')
                        ec2.start_instances(InstanceIds=[server_instanceId])

    except KeyboardInterrupt:
        raise
    except Exception as e:
        print(e)
        pass
    try:
        conn.close()
    except:
        pass
