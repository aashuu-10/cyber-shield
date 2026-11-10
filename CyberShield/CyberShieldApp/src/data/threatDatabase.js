export const KNOWN_PHISHING_DOMAINS = [
  'sbi-verify.xyz',
  'hdfc-netbanking.online',
  'icici-kyc.site',
  'paytm-cashback.top',
  'free-iphone-winner.com',
  'kbc-lottery-winner.info',
  'electricity-bill-pay.org',
  'aadhaar-pan-link.net',
  'work-from-home-earn.biz',
  'telegram-task-jobs.cc',
];

export const SCAM_KEYWORDS = [
  'blocked', 'suspended', 'kyc', 'otp', 'winner', 'lottery',
  'congratulations', 'claim prize', 'urgent', 'immediately',
  'account closed', 'update pan', 'electricity disconnection',
  'part time job', 'daily earn', 'task completed', 'crypto profit',
  'telegram group', 'invest small', 'double money',
];

export const SCAM_PATTERNS = [
  {
    pattern: /account.*(blocked|suspended|deactivated)/i,
    type: 'BANK_SCAM',
    description: 'Fake warning about account suspension to trigger panic.',
  },
  {
    pattern: /(kyc|pan|aadhaar).*(update|link|verify)/i,
    type: 'KYC_PHISHING',
    description: 'Fraudulent request to collect sensitive personal documents.',
  },
  {
    pattern: /(won|winner|lottery|prize).*(₹|\$|lakh|crore|000)/i,
    type: 'LOTTERY_SCAM',
    description: 'False claims of winning prizes to extort advance fees.',
  },
  {
    pattern: /(part time|work from home|daily income).*(₹|\$|earn)/i,
    type: 'JOB_FRAUD',
    description: 'Fake job offer asking for upfront investment or tasks.',
  },
  {
    pattern: /(otp|pin|cvv).*(share|tell|verify|send)/i,
    type: 'CREDENTIAL_THEFT',
    description: 'Attempt to steal security credentials or payment PINs.',
  },
];