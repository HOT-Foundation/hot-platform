import os

settings = dict()

settings['HOST'] = os.getenv('HOST', '')
settings['ASSET_CODE'] = os.environ['ASSET_CODE']
settings['ISSUER'] = os.environ['ISSUER']
settings['STELLAR_NETWORK'] = os.environ['STELLAR_NETWORK']
