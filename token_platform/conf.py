import os

settings = dict()

settings['HOST'] = os.getenv('HOST')
settings['ASSET_CODE'] = os.getenv('ASSET_CODE', 'htkn')
settings['ISSUER'] = os.getenv('ISSUER')
settings['STELLAR_NETWORK'] = os.getenv('STELLAR_NETWORK', 'TESTNET')
settings['LIMIT_TRUST'] = '2000'