from tiled.client import from_profile
from bluesky.callbacks.zmq import Publisher


''' Address
pass-319561 [32]: glbl['inbound_proxy_address']
Out[32]: 'ipc:///var/lib/bluesky-zmq-proxy/pdf-tcp-in-ipc-out/out.sock'
'''

''' defined in 95-zmq.py
pub = Publisher(glbl['inbound_proxy_address'], prefix=b'raw')
xrun.subscribe(pub)
RE.subscribe(pub)
'''

tiled_client = from_profile('pdf')
tiled_client.context.http_client.headers['tiled-qos'] = 'acquisition'

uid = '004bbfe2-11e6-4658-9ae3-75ed6019eb5d'

run = tiled_client[uid]

for name, doc in run.documents():
    pub(name, dict(doc))

