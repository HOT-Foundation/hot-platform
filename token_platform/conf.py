import os

settings = dict()

settings['HOST'] = os.getenv('HOST')
settings['ASSET_CODE'] = os.getenv('ASSET_CODE')
settings['ISSUER'] = os.getenv('ISSUER')
