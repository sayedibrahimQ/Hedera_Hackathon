# 🌍 NileFi — Decentralized SME Credit Scoring & Lending Platform

## 🏦 Overview
**NileFi** is a decentralized finance (DeFi) platform built on **Hedera Hashgraph**, designed to help **Small and Medium Enterprises (SMEs)** in Africa and Egypt access fair, transparent, and verifiable credit.  
It leverages **on-chain credit scoring**, **wallet-based identity**, and **decentralized document verification** to connect SMEs with trusted lenders securely.

---

## 🚀 Core Mission
Enable financial inclusion by providing a **transparent and decentralized credit ecosystem** where:
- SMEs can prove business credibility through verifiable data.
- Lenders can make informed lending decisions based on on-chain records.
- Both parties benefit from trustless smart contracts and immutable scoring history.

---

## 🧩 Key Features

### 🔐 Wallet-Based Authentication
- Users sign in with their **Hedera wallet** (no passwords required).
- Signature verification using **hedera-sdk-python** ensures identity ownership.
- Session-based login for web templates using Django.

### 🧾 On-Chain Credit Scoring
- Credit score is calculated from verified data: revenue, repayment history, loan success.
- Stored as a **non-transferable on-chain token (soulbound credit token)** in the SME’s wallet.
- Immutable record ensures lender confidence.

### 💸 Decentralized Lending Workflow
- Lenders can browse SMEs, review profiles, and offer loans through smart contracts.
- Each loan is tokenized and recorded using **Hedera Token Service (HTS)**.
- Consensus timestamps verify transaction integrity.

### 📄 Verifiable Documents (IPFS Integration)
- Business registration, revenue proofs, and tax docs are uploaded and stored on **IPFS**.
- Hash references are written to Hedera for permanent auditability.
- Eliminates document tampering and centralized data risk.

### 💰 Transparent Repayment Tracking
- Each repayment is logged on-chain with **Hedera Consensus Service (HCS)**.
- Smart contracts can automatically update SME credit score based on timely repayments.

---

## 🏗️ System Architecture

### 1️⃣ Frontend
- Built with **Django Templates** + **Tailwind CSS** for rapid iteration and a clean UI.
- Wallet connect and message signing handled in **JavaScript**.
- Supports both SME and Lender dashboards.

### 2️⃣ Backend
- **Django (Python)** backend for user/session management, profile updates, and loan coordination.
- **Hedera SDK (hedera-sdk-python)** for on-chain logic and wallet authentication.
- Uses **PostgreSQL** or **SQLite** for off-chain profile storage.

### 3️⃣ Blockchain Components
| Component | Purpose |
|------------|----------|
| **Hedera Token Service (HTS)** | Issue credit tokens and represent loans. |
| **Hedera Consensus Service (HCS)** | Log repayment and agreement events immutably. |
| **Hedera Smart Contract Service (HSCS)** | Manage lending agreements and enforce conditions. |
| **IPFS** | Store SME documents and proofs securely. |

---

## ⚙️ Authentication Flow

1. SME/Lender visits **Login Page**.
2. Selects role (SME or Lender).
3. Signs a verification message using their **Hedera Wallet**.
4. Django backend verifies the signature with **PublicKey.verify()**.
5. User session is created, redirecting to role-based dashboard.

---

## 🧠 Data Flow

**SME Side:**
1. Registers wallet → fills company data → uploads documents.
2. Credit score generated → stored as on-chain token.
3. Requests loan offers → lender reviews → contract initialized.

**Lender Side:**
1. Logs in via wallet.
2. Browses verified SMEs with credit score and document proofs.
3. Offers loan → transaction recorded on Hedera.
4. Receives repayments transparently.

---

## 🪙 Tech Stack

| Layer | Technology |
|-------|-------------|
| Frontend | Django Templates, Tailwind CSS, JavaScript |
| Backend | Django, Python |
| Blockchain | Hedera SDK (Python) |
| Smart Contracts | Hedera Smart Contract Service |
| Storage | IPFS (for docs), PostgreSQL (off-chain data) |
| Auth | Wallet-based (PublicKey.verify) |
| Tokenization | Hedera Token Service (Credit & Loan Tokens) |

---

## 📊 Example MVP Flow
**SME Onboarding → Credit Scoring → Loan Offer → On-Chain Record**

1. SME logs in → uploads data → receives a score.  
2. Lender views SMEs → selects one → initiates a loan.  
3. Loan details written to Hedera → repayments tracked automatically.  
4. Credit score updates dynamically on successful repayments.  

---

## 💼 Business Model

| Stakeholder | Benefit |
|--------------|----------|
| **SME** | Gains access to fair credit and immutable reputation. |
| **Lender** | Accesses verified businesses with transparent repayment data. |
| **Platform** | Earns small transaction or service fees on each verified loan or score generation. |

---

## 🌐 Future Enhancements
- Integration with **OracleFreeDollar (OFD)** for decentralized collateral.
- Launch **mobile dApp** using Flutter or React Native.
- Implement **AI-based risk scoring model** for enhanced accuracy.
- Expand to North Africa and pan-African SME ecosystems.

---

## 🏁 Hackathon Goals
1. Demonstrate a full **wallet-authenticated lending flow** using Hedera SDK.  
2. Show **on-chain credit score generation** and retrieval.  
3. Integrate IPFS document verification.  
4. Provide **end-to-end transparency** for SMEs and lenders.  

---

## 👥 Team Roles (example)
| Role | Responsibility |
|------|----------------|
| Backend | Django + Hedera SDK integration |
| Frontend | Django Templates + Tailwind UI |
| Blockchain | Smart contract & token logic |
| Data/AI | Credit score model integration |
| Project Lead | Business logic & presentation |

---

## 🧩 Directory Structure

