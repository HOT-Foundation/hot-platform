class HorizonData(object):
    def transaction(self, tx_hash):
        transaction = {
            "id": "4c239561b64f2353819452073f2ec7f62a5ad66f533868f89f7af862584cdee9",
            "paging_token": "34980756279271424",
            "ledger": 8144592,
            "created_at": "2018-03-28T08:34:22Z",
            "source_account": "GDBNKZDZMEKXOH3HLWLKFMM7ARN2XVPHWZ7DWBBEV3UXTIGXBTRGJLHF",
            "source_account_sequence": "33497802856202246",
            "fee_paid": 200,
            "signatures": [
                "Fy+wn01aXyIYbmbnt/lUcqDEElIqeNoISByLRYQYQhB1To23bR32RApsz/QS/zqPFnK75zoNScmDHfGt9AVtBg==",
                "kGrXKXqXdfeY0zkT4YsgZWfoA6j1wD3vmEBvW0hfEOozogG8jpIDqPksgZy16KmFHKYjyQporHsiBx4gqGr9Cg==",
                "kKNbpAx8TzyfHoffKtG1kQKg4x5O+vaa+LQfPh3YQHLK8Z3Tn/1RRPgHI7NxrKzxdxRYCG5AF6ThyllZ6UWsDQ=="
            ]
        }
        return transaction

    def transaction_operations(self, tx_hash):
        transaction_operations = {
            "_embedded": {
                "records": [
                {
                    "_links": {},
                    "id": "34980756279271425",
                    "paging_token": "34980756279271425",
                    "source_account": "GDBNKZDZMEKXOH3HLWLKFMM7ARN2XVPHWZ7DWBBEV3UXTIGXBTRGJLHF",
                    "type": "create_account",
                    "type_i": 0,
                    "created_at": "2018-03-28T08:34:22Z",
                    "transaction_hash": "4c239561b64f2353819452073f2ec7f62a5ad66f533868f89f7af862584cdee9",
                    "starting_balance": "10.0000000",
                    "funder": "GDBNKZDZMEKXOH3HLWLKFMM7ARN2XVPHWZ7DWBBEV3UXTIGXBTRGJLHF",
                    "account": "GAULEK4CU7IYZTFVKA4EG3RQLKB7LCSYX2WI46C2KXLDUJGQTSH2JWTD"
                },
                {
                    "_links": {},
                    "id": "34980756279271430",
                    "paging_token": "34980756279271430",
                    "source_account": "GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI",
                    "type": "payment",
                    "type_i": 1,
                    "created_at": "2018-03-28T08:34:22Z",
                    "transaction_hash": "4c239561b64f2353819452073f2ec7f62a5ad66f533868f89f7af862584cdee9",
                    "asset_type": "credit_alphanum4",
                    "asset_code": "RNTK",
                    "asset_issuer": "GAKGRSAWXQBPU4GNGHUBFV5QNKMN5BDJ7AA5DNHLZGQG6VPO52WU5TQD",
                    "from": "GDHH7XOUKIWA2NTMGBRD3P245P7SV2DAANU2RIONBAH6DGDLR5WISZZI",
                    "to": "GAULEK4CU7IYZTFVKA4EG3RQLKB7LCSYX2WI46C2KXLDUJGQTSH2JWTD",
                    "amount": "20.0000000"
                }]
            }
        }
        return transaction_operations
