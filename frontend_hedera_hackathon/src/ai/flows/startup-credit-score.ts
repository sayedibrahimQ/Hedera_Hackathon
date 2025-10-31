'use server';

/**
 * @fileOverview An AI agent for assessing a startup's credit score based on uploaded documents.
 *
 * - assessStartupCreditScore - A function that handles the credit score assessment process.
 * - AssessStartupCreditScoreInput - The input type for the assessStartupCreditScore function.
 * - AssessStartupCreditScoreOutput - The return type for the assessStartupCreditScore function.
 */

import {ai} from '@/ai/genkit';
import {z} from 'genkit';

const AssessStartupCreditScoreInputSchema = z.object({
  companyRegistrationDataUri: z
    .string()
    .describe(
      "The company registration document, as a data URI that must include a MIME type and use Base64 encoding. Expected format: 'data:<mimetype>;base64,<encoded_data>'."
    ),
  businessPlanDataUri: z
    .string()
    .describe(
      "The business plan document, as a data URI that must include a MIME type and use Base64 encoding. Expected format: 'data:<mimetype>;base64,<encoded_data>'."
    ),
  financialReportDataUri: z
    .string()
    .describe(
      "The financial report document, as a data URI that must include a MIME type and use Base64 encoding. Expected format: 'data:<mimetype>;base64,<encoded_data>'."
    ),
  industryType: z.string().describe('The industry type of the startup.'),
  yearsInOperation: z.number().describe('The number of years the startup has been in operation.'),
  monthlyRevenueRange: z.string().describe('The monthly revenue range of the startup.'),
  teamSize: z.number().describe('The number of people in the team.'),
  goalsForNext12Months: z.string().describe('The goals for the startup in the next 12 months.'),
});
export type AssessStartupCreditScoreInput = z.infer<typeof AssessStartupCreditScoreInputSchema>;

const AssessStartupCreditScoreOutputSchema = z.object({
  creditScore: z.number().describe('The credit score of the startup, ranging from 0 to 100.'),
  scoreExplanation: z.string().describe('An explanation of the factors contributing to the credit score.'),
});
export type AssessStartupCreditScoreOutput = z.infer<typeof AssessStartupCreditScoreOutputSchema>;

export async function assessStartupCreditScore(input: AssessStartupCreditScoreInput): Promise<AssessStartupCreditScoreOutput> {
  return assessStartupCreditScoreFlow(input);
}

const prompt = ai.definePrompt({
  name: 'assessStartupCreditScorePrompt',
  input: {schema: AssessStartupCreditScoreInputSchema},
  output: {schema: AssessStartupCreditScoreOutputSchema},
  prompt: `You are an expert financial analyst specializing in assessing the creditworthiness of startups.

You will analyze the provided documents and information to determine a credit score for the startup, ranging from 0 to 100. A higher score indicates a stronger credit profile.

Consider the following factors:
- Information extracted from Company Registration Document:  {{media url=companyRegistrationDataUri}}
- Information extracted from Business Plan: {{media url=businessPlanDataUri}}
- Information extracted from Financial Report: {{media url=financialReportDataUri}}
- Industry Type: {{{industryType}}}
- Years in Operation: {{{yearsInOperation}}}
- Monthly Revenue Range: {{{monthlyRevenueRange}}}
- Team Size: {{{teamSize}}}
- Goals for Next 12 Months: {{{goalsForNext12Months}}}

Provide a credit score and a detailed explanation of the factors that influenced your assessment.
`,
});

const assessStartupCreditScoreFlow = ai.defineFlow(
  {
    name: 'assessStartupCreditScoreFlow',
    inputSchema: AssessStartupCreditScoreInputSchema,
    outputSchema: AssessStartupCreditScoreOutputSchema,
  },
  async input => {
    const {output} = await prompt(input);
    return output!;
  }
);
