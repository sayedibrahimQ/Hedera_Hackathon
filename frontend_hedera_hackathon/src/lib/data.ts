export const projects = [
  {
    id: 'proj-agritech-01',
    title: 'EcoHarvest - AI-Powered Crop Monitoring',
    description: 'A revolutionary platform using AI and drone imagery to help farmers in the Nile Delta optimize irrigation and predict yields, increasing efficiency by up to 40%.',
    requestedAmount: 50000,
    fundedAmount: 15000,
    status: 'Funding',
    milestones: [
      { id: 1, name: 'Platform Beta Launch', percentage: 30, expectedDate: '2024-08-15', status: 'Released' },
      { id: 2, name: 'Onboard 50 Farmers', percentage: 40, expectedDate: '2024-10-01', status: 'Pending' },
      { id: 3, name: 'Reach 1000 Hectares Monitored', percentage: 30, expectedDate: '2024-12-20', status: 'Pending' },
    ],
    documents: [
      { name: 'Company Registration.pdf', url: '#' },
      { name: 'Business Plan.pdf', url: '#' },
      { name: 'Financials_Q2_2024.pdf', url: '#' },
    ],
    transactionHistory: [
      { id: 'tx-01', milestone: 'Platform Beta Launch', amount: 15000, date: '2024-06-25', hash: '0.0.12345@1721234567.123456789' },
    ]
  },
  {
    id: 'proj-fintech-02',
    title: 'CairoPay - Mobile Wallet for SMEs',
    description: 'A seamless mobile payment solution for small and medium enterprises in Egypt, offering low transaction fees and integration with local banks.',
    requestedAmount: 75000,
    fundedAmount: 75000,
    status: 'Completed',
     milestones: [
      { id: 1, name: 'App Development Complete', percentage: 40, expectedDate: '2024-03-01', status: 'Released' },
      { id: 2, name: 'Acquire Banking License', percentage: 20, expectedDate: '2024-05-10', status: 'Released' },
      { id: 3, name: '1,000 Active Users', percentage: 40, expectedDate: '2024-07-20', status: 'Released' },
    ],
    documents: [],
    transactionHistory: [],
  },
  {
    id: 'proj-health-03',
    title: 'AfyaConnect - Telemedicine for Rural Areas',
    description: 'Connecting patients in remote African villages with doctors via a low-bandwidth mobile application. Aiming to bridge the healthcare gap.',
    requestedAmount: 100000,
    fundedAmount: 20000,
    status: 'Funding',
     milestones: [
      { id: 1, name: 'Prototype Development', percentage: 20, expectedDate: '2024-09-01', status: 'Verified' },
      { id: 2, name: 'Pilot Program in 3 Villages', percentage: 50, expectedDate: '2024-11-15', status: 'Pending' },
      { id: 3, name: 'Secure Partnership with NGO', percentage: 30, expectedDate: '2025-01-30', status: 'Pending' },
    ],
    documents: [],
    transactionHistory: [],
  },
   {
    id: 'proj-logistics-04',
    title: 'NileDash - Last-Mile Delivery Network',
    description: 'Building an efficient, decentralized last-mile delivery network for urban areas in Egypt, powered by local couriers.',
    requestedAmount: 40000,
    fundedAmount: 0,
    status: 'Pending Approval',
     milestones: [
      { id: 1, name: 'Courier App MVP', percentage: 50, expectedDate: '2024-10-15', status: 'Pending' },
      { id: 2, name: 'Launch in Cairo', percentage: 50, expectedDate: '2025-01-01', status: 'Pending' },
    ],
    documents: [
       { name: 'NileDash_Pitch_Deck.pdf', url: '#' },
       { name: 'Incorporation_Docs.pdf', url: '#' },
    ],
    transactionHistory: [],
  },
];

export const fundedProjects = [
    {
        id: 'funded-01',
        project: 'EcoHarvest',
        totalInvested: 5000,
        progress: 30,
        lastPayment: '2024-06-25',
        status: 'Active',
    },
    {
        id: 'funded-02',
        project: 'CairoPay',
        totalInvested: 20000,
        progress: 100,
        lastPayment: '2024-07-20',
        status: 'Completed',
    }
]

export const fundDistributionData = [
  { name: 'Financial Tech', value: 20000, fill: 'var(--color-chart-1)' },
  { name: 'Agriculture Tech', value: 5000, fill: 'var(--color-chart-2)' },
  { name: 'Healthcare Tech', value: 0, fill: 'var(--color-chart-3)' },
  { name: 'Logistics & Supply Chain', value: 0, fill: 'var(--color-chart-4)' },
  { name: 'E-commerce', value: 0, fill: 'var(--color-chart-5)' },
  { name: 'Education Tech', value: 0, fill: 'var(--color-chart-1)' },
  { name: 'Renewable Energy', value: 0, fill: 'var(--color-chart-2)' },
  { name: 'Other', value: 0, fill: 'var(--color-chart-3)' },
];

export const revenueRanges = [
    "Pre-revenue",
    "$1 - $1,000",
    "$1,001 - $5,000",
    "$5,001 - $25,000",
    "$25,001 - $100,000",
    "$100,001+",
];

export const industryTypes = [
    "Agriculture Tech",
    "Financial Tech",
    "Healthcare Tech",
    "E-commerce",
    "Education Tech",
    "Logistics & Supply Chain",
    "Renewable Energy",
    "Other",
]

export const loanData = {
    projectId: 'proj-fintech-02',
    projectName: 'CairoPay - Mobile Wallet for SMEs',
    totalAmount: 75000,
    repaymentSchedule: [
        { id: 1, dueDate: '2024-08-20', amount: 6250, status: 'Paid' },
        { id: 2, dueDate: '2024-09-20', amount: 6250, status: 'Paid' },
        { id: 3, dueDate: '2024-10-20', amount: 6250, status: 'Due' },
        { id: 4, dueDate: '2024-11-20', amount: 6250, status: 'Due' },
        { id: 5, dueDate: '2024-12-20', amount: 6250, status: 'Due' },
        { id: 6, dueDate: '2025-01-20', amount: 6250, status: 'Due' },
        { id: 7, dueDate: '2025-02-20', amount: 6250, status: 'Due' },
        { id: 8, dueDate: '2025-03-20', amount: 6250, status: 'Due' },
        { id: 9, dueDate: '2025-04-20', amount: 6250, status: 'Due' },
        { id: 10, dueDate: '2025-05-20', amount: 6250, status: 'Due' },
        { id: 11, dueDate: '2025-06-20', amount: 6250, status: 'Due' },
        { id: 12, dueDate: '2025-07-20', amount: 6250, status: 'Due' },
    ] as { id: number; dueDate: string; amount: number; status: 'Paid' | 'Due' | 'Overdue' }[],
};
