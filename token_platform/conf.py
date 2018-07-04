from typing import Dict, Any

import os

settings: Dict[str, Any] = dict()

settings['HOST'] = os.getenv('HOST', '')
settings['ASSET_CODE'] = os.environ['ASSET_CODE']
settings['LIMIT_ASSET'] = '10000000000'
settings['ISSUER'] = os.environ['ISSUER']
settings['HORIZON_URL'] = os.environ['HORIZON_URL']

settings['LOG_OPS'] = {
    'SUBMIT': '[SUBMIT]'
}