
BALANCES = [{
        'balance': '7.0000000',
        'limit': '922337203685.4775807',
        'asset_type': 'credit_alphanum4',
        'asset_code': 'RNTK',
        'asset_issuer': 'GAKGRSAWXQBPU4GNGHUBFV5QNKMN5BDJ7AA5DNHLZGQG6VPO52WU5TQD'
    },
    {
        'balance': '9.9999200',
        'asset_type': 'native'
    }]


SIGNERS = [{
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


WALLET = expect_data = {
        '@url': 'localhost:8081/wallet/GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
        '@id': 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
        'asset': {
            'RNTK': {
                'balance': '7.0000000',
                'issuer': 'GAKGRSAWXQBPU4GNGHUBFV5QNKMN5BDJ7AA5DNHLZGQG6VPO52WU5TQD'
            },
            'XLM': {
                'balance': '9.9999200',
                'issuer': 'native'
            }
        },
        'thresholds': {
            'low_threshold': 1,
            'med_threshold': 2,
            'high_threshold': 2
        },
        'signers': [
            {
                'public_key': 'GDBNKZDZMEKXOH3HLWLKFMM7ARN2XVPHWZ7DWBBEV3UXTIGXBTRGJLHF',
                'weight': 1,
                'type': 'ed25519_public_key'
            }, {
                'public_key': 'GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI',
                'weight': 1,
                'type': 'ed25519_public_key'
            }, {
                'public_key': 'GBVJJJH6VS5NNM5B4FZ3JQHWN6ANEAOSCEU4STPXPB24BHD5JO5VTGAD',
                'weight': 0,
                'type': 'ed25519_public_key'
            }
        ]
    }

def thresholds(low=1, med=1, high=1):
    return {
        'low_threshold': low,
        'med_threshold': med,
        'high_threshold': high
    }


class StellarWallet(object):
        def get(self):
            pass

        @property
        def balances(self):
            return BALANCES

        @property
        def signers(self):
            return SIGNERS

        @property
        def thresholds(self):
            return thresholds(1,2,2)