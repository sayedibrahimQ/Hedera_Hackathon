'use server';

import { assessStartupCreditScore, type AssessStartupCreditScoreInput } from '@/ai/flows/startup-credit-score';

export async function getCreditScore(input: AssessStartupCreditScoreInput) {
  try {
    const result = await assessStartupCreditScore(input);
    return { success: true, data: result };
  } catch (error) {
    console.error("Error assessing credit score:", error);
    // In a real app, you might want to log this error more robustly
    return { success: false, error: "Failed to assess credit score. The AI model may be temporarily unavailable. Please try again later." };
  }
}
