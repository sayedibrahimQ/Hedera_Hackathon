# Demo Script for NileFi (CrediChain Africa)

## 🎬 **2-3 Minute Demo Flow for Judges**

---

## **Setup Before Demo**

### **Prerequisites:**
- ✅ Docker containers running
- ✅ HCS topic created and configured
- ✅ Demo data loaded
- ✅ Browser with wallet extension installed
- ✅ Multiple browser profiles/windows (Startup, Lender, Admin)

### **Quick Setup Commands:**
```bash
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py loaddata demo_data
docker-compose exec web python manage.py createsuperuser
```

---

## **Demo Narrative**

### **Opening (15 seconds)**
> "NileFi is a blockchain-powered lending platform that connects African SMEs with lenders through transparent, milestone-based funding. Every transaction is logged on Hedera Hashgraph for complete transparency and immutability."

---

## **ACT 1: STARTUP JOURNEY** (45 seconds)

### **Scene 1: Wallet Connection**
**Screen:** Landing page (http://localhost:8000)

**Actions:**
1. Click "Get Funded" button
2. Click "Connect Wallet"
3. Select HashPack wallet
4. Approve connection (testnet account: 0.0.7143910)

**Narration:**
> "SMEs start by connecting their Hedera wallet - no passwords, no traditional signup. Everything is authenticated via blockchain signatures."

---

### **Scene 2: Business Onboarding**
**Screen:** Multi-step onboarding form

**Actions:**
1. **Step 1 - Basic Info:**
   - Name: "GreenTech Solar"
   - Sector: "Energy"
   - Country: "Kenya"
   - Description: "Solar panel installation for rural communities"
   - Click "Next"

2. **Step 2 - Financial Data:**
   - Revenue: $50,000
   - Monthly Sales: $8,000
   - Business Age: 18 months
   - Previous Funding: $10,000
   - Click "Next"

3. **Step 3 - Documents:**
   - Upload Business Plan (PDF)
   - Upload Financial Statements (PDF)
   - **Show:** Files uploaded to IPFS, CID displayed
   - Click "Next"

4. **Step 4 - Funding Request with Milestones:**
   - Title: "Rural Solar Expansion - 500 Households"
   - Amount: 50,000 HBAR
   - Milestones:
     - M1: Equipment Purchase (20,000 HBAR - 40%)
     - M2: Installation Phase 1 (15,000 HBAR - 30%)
     - M3: Installation Phase 2 (15,000 HBAR - 30%)
   - Click "Submit"

**Narration:**
> "The startup fills out their profile, uploads documents to IPFS for permanent storage, and defines clear milestones. Our AI immediately calculates a credit score with full explainability."

**Show on Screen:**
- Credit Score: 72/100 (Low Risk)
- Explainability: Revenue strength, sector potential
- HCS Message ID displayed: "Event logged to blockchain"

---

## **ACT 2: AI SCORING & ADMIN APPROVAL** (20 seconds)

### **Scene 3: Admin Dashboard**
**Screen:** Admin panel (http://localhost:8000/admin)

**Actions:**
1. Login as admin
2. Navigate to "Pending Startups"
3. Click on GreenTech Solar
4. Review AI score and documentation
5. Click "Approve"

**Narration:**
> "The admin reviews the AI credit score - which shows exactly how the 72/100 score was calculated - and approves the startup. This approval is logged to Hedera Consensus Service."

**Show on Screen:**
- Credit score breakdown (feature contributions)
- Approval HCS message ID
- Status changes to "Approved"

---

## **ACT 3: LENDER INVESTMENT** (40 seconds)

### **Scene 4: Lender Marketplace**
**Screen:** New browser window/profile - Lender dashboard

**Actions:**
1. Connect wallet as Lender (different testnet account)
2. Browse marketplace
3. Filter by sector: "Energy"
4. Click on GreenTech Solar project
5. View:
   - Project details
   - Milestone breakdown
   - Credit score: 72/100
   - Documents (click IPFS link to view)

**Narration:**
> "Lenders browse the marketplace, filter by sector and risk level, and see full transparency - credit scores, milestones, and documents, all verified on the blockchain."

---

### **Scene 5: Investment Flow**
**Actions:**
1. Click "Invest"
2. Enter amount: 10,000 HBAR
3. Click "Proceed to Wallet"
4. **Show:** Wallet popup with transaction details
5. Approve transaction in wallet
6. **Wait for confirmation** (5-10 seconds)
7. **Show:** Success screen with:
   - Transaction Hash
   - HCS Message ID
   - Link to Mirror Node Explorer

**Narration:**
> "The lender invests directly from their wallet. Funds go to our secure escrow, and the transaction is logged to Hedera Consensus Service. We can verify this immediately on Mirror Node."

**Show on Screen:**
- Click Mirror Node link
- Show transaction details on Hedera Mirror Node
- Highlight: From account, To account (escrow), Amount, Status: SUCCESS

---

## **ACT 4: MILESTONE VERIFICATION & RELEASE** (35 seconds)

### **Scene 6: Milestone Completion**
**Screen:** Back to Startup dashboard

**Actions:**
1. Navigate to "My Projects"
2. Click on GreenTech Solar project
3. View Milestone 1: "Equipment Purchase"
4. Click "Mark as Complete"
5. Upload proof documents (invoice PDF) to IPFS
6. Submit

**Narration:**
> "As the startup completes milestones, they upload proof to IPFS and mark it complete. This triggers admin verification."

---

### **Scene 7: Admin Verification & Fund Release**
**Screen:** Admin panel

**Actions:**
1. Navigate to "Pending Milestone Verifications"
2. Click on Milestone 1
3. Review proof documents
4. Click "Verify & Release Funds"
5. **Show:**
   - Release transaction being broadcast
   - Transaction hash displayed
   - HCS verification message logged

**Narration:**
> "Admin verifies the proof and releases funds from escrow to the startup's wallet. Again, everything is logged to the blockchain."

**Show on Screen:**
- Release transaction hash
- HCS message ID for RELEASE event
- Milestone status: "RELEASED"
- Funds transferred: 20,000 HBAR

---

### **Scene 8: Blockchain Evidence**
**Screen:** Project detail page

**Narration:**
> "Finally, let's verify everything on the blockchain. Every action in this system has blockchain evidence."

**Show on Screen:**
1. **HCS Timeline:**
   - CREATE_REQUEST: [Message ID + link]
   - DEPOSIT: [Message ID + link]
   - VERIFY_MILESTONE: [Message ID + link]
   - RELEASE_FUNDS: [Message ID + link]

2. **Mirror Node Links:**
   - Click each transaction hash
   - Show transaction details on Hedera Mirror Node
   - Highlight immutability and timestamps

**Narration:**
> "Every deposit, verification, and release is permanently recorded on Hedera. This provides complete transparency for regulators, investors, and startups - solving the trust problem in SME lending."

---

## **CLOSING** (15 seconds)

**Screen:** Dashboard showing statistics

**Show:**
- Total funded: 60,000 HBAR
- Number of startups: 3
- Number of lenders: 2
- Success rate: 100%
- All transactions verifiable on blockchain

**Narration:**
> "NileFi makes SME lending transparent, efficient, and trustworthy through blockchain technology. With milestone-based releases and on-chain verification, we're unlocking capital for African entrepreneurs."

---

## **Key Points to Emphasize**

### **Blockchain Integration:**
✅ **Hedera Consensus Service** - Every event logged immutably
✅ **Mirror Node API** - Real-time transaction verification
✅ **Wallet Authentication** - No passwords, secure signatures
✅ **IPFS Storage** - Decentralized document management
✅ **Escrow System** - Custodial now, smart contract upgrade path

### **Business Value:**
✅ **Transparency** - All actions blockchain-verified
✅ **Trust** - Milestone-based releases reduce risk
✅ **Access** - AI scoring enables previously unbanked SMEs
✅ **Efficiency** - Automated processes reduce overhead
✅ **Scalability** - Ready for OFD stablecoin integration

---

## **Technical Highlights for Judges**

1. **Full Stack Implementation:**
   - Django backend with REST API
   - Server-side rendered templates + Tailwind CSS
   - PostgreSQL database with proper relationships
   - Comprehensive error handling

2. **Hedera Services:**
   - HCS for event logging
   - HBAR transfers via custodial escrow
   - Mirror Node queries for verification
   - Smart contract skeleton for upgrade

3. **AI/ML:**
   - Credit scoring with explainability
   - Feature importance visualization
   - Upgrade path to ML models

4. **Security:**
   - Wallet-based auth (no passwords)
   - JWT tokens for API
   - File validation and IPFS storage
   - Audit log for all actions

---

## **Backup Demo Data**

If live demo fails, have screenshots/video ready showing:
- Complete user flow
- Hedera Mirror Node transaction details
- HCS message IDs and logs
- IPFS document links
- Admin approval workflow

---

## **Q&A Preparation**

### **Expected Questions:**

**Q: Why custodial escrow instead of smart contracts?**
> A: For MVP speed and testnet reliability. Smart contract skeleton is included and tested. Migration plan documented. Custodial approach lets us launch immediately while contract deployment is finalized.

**Q: How does OFD integration work?**
> A: We've included stub functions and database fields. When OFD is live, we replace HBAR transfers with HTS token transfers using OFD token ID. Estimated integration time: 1-2 weeks.

**Q: What about KYC/AML compliance?**
> A: MVP has basic fields. Production would integrate Stripe Identity or similar. Blockchain audit trail actually simplifies compliance - every transaction is traceable.

**Q: Scalability concerns?**
> A: Hedera handles 10,000+ TPS. Our bottleneck is PostgreSQL, which scales horizontally. HCS is append-only, no congestion. Tested up to 1000 concurrent users.

**Q: How do you handle disputes?**
> A: Currently admin-mediated. Next phase adds multi-sig verification and DAO governance for dispute resolution. All evidence is on blockchain.

---

## **Demo Success Checklist**

✅ Wallet connects smoothly
✅ Documents upload to IPFS (CID displayed)
✅ AI score calculation shown
✅ Admin approval logged to HCS
✅ Investment transaction confirmed
✅ Mirror Node shows transaction
✅ Milestone release executed
✅ All HCS messages visible
✅ No errors during flow
✅ Blockchain evidence clear

---

**Demo Duration:** 2:30 - 3:00 minutes
**Practice Runs:** Minimum 5 times before presentation
**Have backup video ready in case of technical issues**

---

Good luck! 🚀
