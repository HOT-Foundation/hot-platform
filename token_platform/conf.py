import os

settings = dict()

settings['HOST'] = os.getenv('HOST', 'localhost:8081')
settings['ASSET_CODE'] = os.getenv('ASSET_CODE', 'HTKN')
settings['ISSUER'] = os.getenv('ISSUER', 'GDSB3JZDYKLYKWZ6NXDPPGPCYJ32ISMTZ2LVF5PYQGY4B4FGNIU2M5BJ')
settings['STELLAR_NETWORK'] = os.getenv('STELLAR_NETWORK', 'TESTNET')

