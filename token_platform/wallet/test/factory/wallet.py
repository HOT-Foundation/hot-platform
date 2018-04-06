class StellarWallet(object):
        def __init__(self):
            pass

        def get(self):
            pass

        @property
        def id(self):
            return 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD'

        @property
        def balances(self):
            return [{
                'balance': '7.0000000',
                'limit': '922337203685.4775807',
                'asset_type': 'credit_alphanum4',
                'asset_code': 'HTKN',
                'asset_issuer': 'GAKGRSAWXQBPU4GNGHUBFV5QNKMN5BDJ7AA5DNHLZGQG6VPO52WU5TQD'
            },
            {
                'balance': '9.9999200',
                'asset_type': 'native'
            }]

        @property
        def signers(self):
            return [{
                'public_key': 'GDBNKZDZMEKXOH3HLWLKFMM7ARN2XVPHWZ7DWBBEV3UXTIGXBTRGJLHF',
                'weight': 1,
                'key': 'GDBNKZDZMEKXOH3HLWLKFMM7ARN2XVPHWZ7DWBBEV3UXTIGXBTRGJLHF',
                'type': 'ed25519_public_key'
            },
            {
                'public_key': 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI',
                'weight': 1,
                'key': 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI',
                'type': 'ed25519_public_key'
            },
            {
                'public_key': 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
                'weight': 0,
                'key': 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
                'type': 'ed25519_public_key'
            }]

        @property
        def thresholds(self):
            return {
            'low_threshold': 1,
            'med_threshold': 2,
            'high_threshold': 2
        }