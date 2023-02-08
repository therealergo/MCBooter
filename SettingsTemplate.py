ip_allocationId     = 'eipalloc-'
launcher_instanceId = 'i-'
server_instanceId   = 'i-'
server_regionName   = 'us-east-'
TCP_PORTS = [25565]
REASSOC_TIMEOUT = 8
MINECONN_TIMEOUT = 10
RESP_JSON_PREPRO = \
'''{
    "version": {
        "name": "1.19.3",
        "protocol": 
'''
RESP_JSON_POSTPRO = \
'''
    },
    "players": {
        "max": 2000,
        "online": 0,
        "sample": [
        ]
    },
    "description": {
        "text": "Booting server, please wait...\nThis may take 1-2 minutes!"
    },
    "favicon": "data:image/png;base64,<data>"
}'''
