from typing import Dict, Any

import os

settings: Dict[str, Any] = dict()

settings['HOST'] = os.getenv('HOST', '')
settings['ASSET_CODE'] = os.environ['ASSET_CODE']
settings['LIMIT_ASSET'] = '10000000000'
settings['ISSUER'] = os.environ['HOT_ISSUER']
settings['PASSPHRASE'] = os.environ['PASSPHRASE']
settings['HORIZON_URL'] = os.environ['HORIZON_URL']
settings['TRACK_COLLECTOR_ADDRESS'] = os.environ['TRACK_COLLECTOR_ADDRESS']

settings['LOG_OPS'] = {
    'SUBMIT': '[SUBMIT]'
}

settings['SENTRY_ENDPOINT'] = os.getenv('SENTRY_ENDPOINT', False)