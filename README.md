# NileFi — Decentralized SME Funding on Hedera

NileFi is a blockchain-powered platform that enables transparent, milestone-based funding for small and medium enterprises (SMEs) in Africa.
Built using Django, Tailwind CSS, and the Hedera SDK, NileFi ensures transparency, automation, and trust between startups and investors.

## Overview

NileFi connects investors and businesses through an on-chain funding system.
Funds are held in Hedera smart escrow contracts and released only when verified milestones are completed.

Core MVP Flow

Startup creates a funding request with milestones.

Investor funds the project (escrow contract on Hedera).

Milestones are verified by a trusted entity or AI system.

Smart contract releases funds automatically.

All transactions are visible on the Hedera network for full transparency.

# Tech Stack
Layer	Technology
Backend	Django + Django REST Framework
Frontend	Django Templates + Tailwind CSS
Blockchain	Hedera SDK (Python)
Database	PostgreSQL
Wallet Integration	HashPack / Blade Wallet
Optional AI	Credit Scoring & Startup Risk Analysis
# Key Features

- Smart Escrow Contracts – Automates secure milestone-based payments.

- Transparent Funding Requests – Startups submit structured project proposals.

- Investor Dashboard – Monitor project progress and fund flow.

- AI Credit Scoring (Optional) – Evaluate startup risk based on business data.

- Regional Focus – Tailored for African & Egyptian SMEs.

- Modern UI – Built with Tailwind for clean, responsive design.

# Installation & Setup
1. Clone the repository
git clone https://github.com/<your-username>/nilefi.git
cd nilefi

2. Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

3. Install dependencies
pip install -r requirements.txt

4. Run Tailwind
python manage.py tailwind install
python manage.py tailwind start

5. Run the Django server
python manage.py migrate
python manage.py runserver


Then visit: http://127.0.0.1:8000

# Project Structure
nilefi/
│
├── core/                # Main Django app (models, views, URLs)
├── theme/               # Tailwind integration
├── templates/           # Django templates (HTML pages)
│   ├── index.html
│   ├── dashboard_business.html
│   ├── dashboard_investor.html
│   ├── project_detail.html
│   ├── credit_scoring.html
│
├── static/              # Compiled Tailwind assets
├── manage.py
└── requirements.txt

# Core Pages
Page	Description
/	Landing Page
/register	Signup with wallet
/dashboard/business	Create & track funding requests
/dashboard/investor	View & fund startups
/project/<id>	Project details and milestones
/credit-scoring	Startup data collection for AI Scoring
🪙 Smart Contract Flow

Investor funds a project → Hedera escrow smart contract holds funds.

Business marks milestone as complete → verification process starts.

Once verified, funds are released automatically to the business wallet.

Transactions are visible through the Hedera Mirror Node API.

# Future Enhancements

DAO-based investor pools

Decentralized reputation system

Real-time Hedera mirror node dashboard

AI-powered credit score visualization

# Contributors

Sayed Ibrahim — Backend & Hedera Integration

Frontend Team — Django Templates + Tailwind UI

AI Team — Credit Scoring & Analytics

# Hackathon Submission

Built for Hedera x DoraHacks Hackathon 2025
Category: DeFi / AI for Financial Inclusion
Focus: Blockchain-backed SME Funding in Africa
