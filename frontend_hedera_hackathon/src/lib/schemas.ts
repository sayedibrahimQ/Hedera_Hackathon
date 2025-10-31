import * as z from 'zod';

export const OnboardingQuestionnaireSchema = z.object({
  industryType: z.string({ required_error: "Industry type is required." }).min(1, "Industry type is required."),
  yearsInOperation: z.coerce.number({ required_error: "Years in operation are required." }).min(0, "Years must be a non-negative number."),
  monthlyRevenueRange: z.string({ required_error: "Monthly revenue is required." }).min(1, "Monthly revenue is required."),
  teamSize: z.coerce.number({ required_error: "Team size is required." }).min(1, "Team size must be at least 1."),
  goalsForNext12Months: z.string({ required_error: "Goals are required." }).min(20, "Please provide more details about your goals (min 20 characters).").max(500, "Goals must be 500 characters or less."),
});

export type OnboardingQuestionnaireData = z.infer<typeof OnboardingQuestionnaireSchema>;
