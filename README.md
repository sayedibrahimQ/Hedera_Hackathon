
# NileFi

## Real Estate Tokenization and Rental Management Platform

NileFi is a decentralized platform that leverages the Hedera Hashgraph network to revolutionize the real estate industry. It enables property owners to tokenize their assets, representing them as digital tokens on the blockchain. This opens up new avenues for fractional ownership, simplified property transfers, and transparent rental management.

## Key Features

- **Real Estate Tokenization:** Convert real estate assets into digital tokens on the Hedera network.
- **Fractional Ownership:** Enable multiple investors to co-own a single property.
- **Decentralized Rental Management:** Automate rent collection and agreement enforcement through smart contracts.
- **Secure and Transparent:** Leverage the security and transparency of the Hedera Hashgraph network.

## Getting Started

### Prerequisites

- Python 3.10+
- Poetry
- Docker
- Docker Compose

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/nilefi.git
   ```

2. **Install dependencies:**

   ```bash
   poetry install
   ```

3. **Set up environment variables:**

   Create a `.env` file in the root directory and add the following:

   ```
   SECRET_KEY=your-secret-key
   DEBUG=True
   DATABASE_URL=psql://user:password@db/nilefi
   HEDERA_ACCOUNT_ID=your-hedera-account-id
   HEDERA_PRIVATE_KEY=your-hedera-private-key
   ```

4. **Run database migrations:**

   ```bash
   poetry run python manage.py migrate
   ```

5. **Start the development server:**

   ```bash
   poetry run python manage.py runserver
   ```

## API Endpoints

The following API endpoints are available:

- **`POST /api/blockchain/accounts/`**: Create a new Hedera account.
- **`POST /api/blockchain/tokenize/`**: Tokenize a real estate asset.
- **`POST /api/blockchain/rental-agreements/`**: Create a rental agreement.
- **`GET /api/users/`**: Retrieve a list of users.
- **`POST /api/users/`**: Create a new user.

## Smart Contracts

The smart contracts for the NileFi platform are located in the `contracts` directory. They are written in Solidity and compiled using the Hardhat development environment.

### `NileFi.sol`

This contract manages the tokenization of real estate assets and the creation of rental agreements.

## OFD Integration

The NileFi platform integrates with the Open Finance Data (OFD) API to retrieve property data and verify ownership. The OFD integration code is located in the `nilefi/apps/blockchain/ofd_integration.py` file.

## Hedera Integration

The NileFi platform uses the Hedera Python SDK to interact with the Hedera network. The Hedera integration code is located in the `nilefi/apps/blockchain/wallet_utils.py` and `nilefi/apps/blockchain/transactions.py` files.
