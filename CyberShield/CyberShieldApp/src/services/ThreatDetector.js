import { KNOWN_PHISHING_DOMAINS, SCAM_KEYWORDS, SCAM_PATTERNS } from '../data/threatDatabase';

export function scanText(text) {
  if (!text || typeof text !== 'string') {
    return { isThreat: false, score: 0, riskLevel: 'LOW', threats: [] };
  }

  const lowerText = text.toLowerCase();
  const threats = [];
  let score = 0;

  // 1. Check Regex Patterns
  (SCAM_PATTERNS || []).forEach((item) => {
    if (item.pattern.test(lowerText)) {
      score += 30;
      threats.push({
        type: item.type,
        description: item.description,
      });
    }
  });

  // 2. Check Scam Keywords
  const matchedKeywords = (SCAM_KEYWORDS || []).filter((kw) =>
    lowerText.includes(kw.toLowerCase())
  );

  if (matchedKeywords.length > 0) {
    score += matchedKeywords.length * 10;
    if (threats.length === 0) {
      threats.push({
        type: 'SUSPICIOUS_CONTENT',
        description: `Contains high-risk scam keywords: ${matchedKeywords.slice(0, 3).join(', ')}`,
      });
    }
  }

  // 3. Check for Suspicious Links in text
  const urlRegex = /(https?:\/\/[^\s]+)/g;
  const urls = text.match(urlRegex);
  if (urls) {
    urls.forEach((url) => {
      const isKnownPhishing = (KNOWN_PHISHING_DOMAINS || []).some((domain) =>
        url.toLowerCase().includes(domain)
      );
      if (isKnownPhishing) {
        score += 40;
        threats.push({
          type: 'PHISHING_URL',
          description: `Contains known malicious domain in link: ${url}`,
        });
      }
    });
  }

  // Cap score at 100
  const finalScore = Math.min(score, 100);
  const riskLevel = finalScore >= 60 ? 'HIGH' : finalScore >= 30 ? 'MEDIUM' : 'LOW';

  return {
    isThreat: finalScore >= 30,
    score: finalScore,
    riskLevel,
    threats,
  };
}

export function scanURL(url) {
  if (!url || typeof url !== 'string') {
    return { isThreat: false, score: 0, riskLevel: 'LOW', threats: [] };
  }

  const lowerUrl = url.toLowerCase();
  const threats = [];
  let score = 0;

  // Check known phishing list
  const isKnown = (KNOWN_PHISHING_DOMAINS || []).some((domain) =>
    lowerUrl.includes(domain)
  );

  if (isKnown) {
    score += 80;
    threats.push({
      type: 'KNOWN_PHISHING',
      description: 'This domain is listed on global phishing blacklists.',
    });
  }

  // Check for HTTP vs HTTPS
  if (lowerUrl.startsWith('http://')) {
    score += 20;
    threats.push({
      type: 'INSECURE_HTTP',
      description: 'URL uses unencrypted HTTP instead of secure HTTPS.',
    });
  }

  // Check for suspicious TLDs
  if (/\.(xyz|top|site|cc|info|biz|club|work|link)$/i.test(lowerUrl)) {
    score += 25;
    threats.push({
      type: 'HIGH_RISK_TLD',
      description: 'Domain uses a high-risk top-level domain frequently used in scams.',
    });
  }

  const finalScore = Math.min(score, 100);
  const riskLevel = finalScore >= 60 ? 'HIGH' : finalScore >= 30 ? 'MEDIUM' : 'LOW';

  return {
    isThreat: finalScore >= 30,
    score: finalScore,
    riskLevel,
    threats,
  };
}

export default {
  scanText,
  scanURL,
};