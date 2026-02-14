from bluesky.callbacks.zmq import Publisher

pub = Publisher(glbl['inbound_proxy_address'], prefix=b'raw')
xrun.subscribe(pub)
RE.subscribe(pub)

