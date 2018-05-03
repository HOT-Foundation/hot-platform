import os

settings = dict()

settings['HOST'] = os.getenv('HOST', 'localhost:8081')
settings['ASSET_CODE'] = os.getenv('ASSET_CODE', 'HTKN')
settings['ISSUER'] = os.getenv('ISSUER', 'GD3YX4FYDGEMS3HKOTBX6EED6II62G7YTY3JJ4KTKMCEHW6L2QLFNANV')
settings['STELLAR_NETWORK'] = os.getenv('STELLAR_NETWORK', 'TESTNET')