
# NileFi

NileFi is a real estate tokenization and investment platform built with Django and Hedera Hashgraph.

## Features

* **Real Estate Tokenization:** Tokenize real estate assets on the Hedera network as Non-Fungible Tokens (NFTs).
* **Fractional Ownership:** Invest in fractional ownership of real estate assets.
* **Rental Agreements:** Create and manage rental agreements on the Hedera network.
* **Crowdfunding:** Raise funds for real estate projects through a crowdfunding platform.

## Getting Started

### Prerequisites

* Python 3.11
* Poetry
* A Hedera testnet account

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/nilefi.git
   ```
2. Install the dependencies:
   ```bash
   poetry install
   ```
3. Set up your Hedera testnet account:
   - Create a `.env` file in the `nilefi` directory.
   - Add the following environment variables to the `.env` file:
     ```
     HEDERA_ACCOUNT_ID="your-account-id"
     HEDERA_PRIVATE_KEY="your-private-key"
     TREASURY_ACCOUNT_ID="your-treasury-account-id"
     TREASURY_PRIVATE_KEY="your-treasury-private-key"
     ```
   **Note:** The `TREASURY_ACCOUNT_ID` and `TREASURY_PRIVATE_KEY` are used for creating and managing tokens. This should be a separate account from your personal account.

4. Run the database migrations:
   ```bash
   poetry run python manage.py migrate
   ```
5. Start the development server:
   ```bash
   poetry run python manage.py runserver
   ```

## API Endpoints

* `api/accounts/`: User registration, login, and profile management.
* `api/blockchain/`: Blockchain-related operations.
    *   `POST /api/blockchain/tokenize/`: Tokenize a real estate asset.
        *   **Body:**
            ```json
            {
                "asset_id": "unique-asset-identifier",
                "token_name": "My Real Estate Token",
                "token_symbol": "MRET"
            }
            ```
    *   `POST /api/blockchain/rental-agreements/`: Create a rental agreement.
        *   **Body:**
            ```json
            {
                "tenant_id": "hedera-tenant-account-id",
                "landlord_id": "hedera-landlord-account-id",
                "rent_amount": 1000
            }
            ```
* `api/funding/`: Crowdfunding operations, such as creating funding requests and investing in projects.
