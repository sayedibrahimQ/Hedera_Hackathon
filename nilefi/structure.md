nilefi_backend/
│
├── manage.py
├── requirements.txt
│
├── nilefi/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/
│   ├── accounts/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── services.py
│   │
│   ├── funding/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── services.py
│   │
│   ├── blockchain/
│   │   ├── hedera_client.py        # Initialize Hedera client
│   │   ├── contracts.py            # Escrow + milestone smart contract logic
│   │   ├── wallet_utils.py         # Wallet creation, balances
│   │   ├── ofd_integration.py      # NEW → OFD minting, redemption, transfers
│   │   ├── transactions.py
│   │   └── constants.py
│   │
│   ├── analytics/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── utils.py
│   │
│   └── common/
│       ├── utils.py
│       ├── mixins.py
│       └── exceptions.py
│
├── media/
└── scripts/
    ├── deploy_contracts.py
    └── setup_ofd_connection.py