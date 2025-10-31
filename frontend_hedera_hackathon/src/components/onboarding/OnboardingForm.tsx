'use client';

import { useState } from 'react';
import { useForm, type SubmitHandler } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  OnboardingQuestionnaireSchema,
  type OnboardingQuestionnaireData,
} from '@/lib/schemas';
import { fileToDataUri } from '@/lib/utils';
import { getCreditScore } from '@/app/onboarding/actions';

import { CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { ArrowLeft, ArrowRight, CheckCircle, PartyPopper } from 'lucide-react';
import { WelcomeStep } from './WelcomeStep';
import { DocumentUploadStep } from './DocumentUploadStep';
import { QuestionnaireStep } from './QuestionnaireStep';
import { CreditScoringStep } from './CreditScoringStep';
import { useRouter } from 'next/navigation';
import { Form } from '@/components/ui/form';

type FileState = {
  companyRegistration: File | null;
  businessPlan: File | null;
  financialReport: File | null;
};

type AIScoreState = {
  loading: boolean;
  score: number | null;
  explanation: string | null;
  error: string | null;
};

const TOTAL_STEPS = 4;

export function OnboardingForm() {
  const [step, setStep] = useState(1);
  const router = useRouter();

  const [files, setFiles] = useState<FileState>({
    companyRegistration: null,
    businessPlan: null,
    financialReport: null,
  });

  const [aiScore, setAiScore] = useState<AIScoreState>({
    loading: false,
    score: null,
    explanation: null,
    error: null,
  });

  const form = useForm<OnboardingQuestionnaireData>({
    resolver: zodResolver(OnboardingQuestionnaireSchema),
    mode: 'onChange',
  });

  const handleNextStep = async () => {
    let isValid = true;
    if (step === 2) {
      // Document validation
      if (!files.companyRegistration || !files.businessPlan || !files.financialReport) {
        alert("Please upload all three required documents.");
        isValid = false;
      }
    }
    if (step === 3) {
      // Questionnaire validation
      isValid = await form.trigger();
    }
    if (isValid) {
      setStep((prev) => prev + 1);
    }
  };

  const handlePrevStep = () => {
    setStep((prev) => prev - 1);
  };

  const handleAssessCreditScore: SubmitHandler<OnboardingQuestionnaireData> = async (data) => {
    if (!files.companyRegistration || !files.businessPlan || !files.financialReport) {
      setAiScore({ ...aiScore, error: "Missing one or more documents." });
      return;
    }
    
    setStep((prev) => prev + 1);
    setAiScore({ loading: true, score: null, explanation: null, error: null });

    try {
      const [companyRegistrationDataUri, businessPlanDataUri, financialReportDataUri] = await Promise.all([
        fileToDataUri(files.companyRegistration),
        fileToDataUri(files.businessPlan),
        fileToDataUri(files.financialReport),
      ]);

      const aiInput = {
        ...data,
        companyRegistrationDataUri,
        businessPlanDataUri,
        financialReportDataUri,
      };

      const result = await getCreditScore(aiInput);

      if (result.success && result.data) {
        setAiScore({ loading: false, score: result.data.creditScore, explanation: result.data.scoreExplanation, error: null });
      } else {
        setAiScore({ loading: false, score: null, explanation: null, error: result.error || 'An unknown error occurred.' });
      }

    } catch (error) {
      setAiScore({ loading: false, score: null, explanation: null, error: 'Failed to process files for scoring.' });
    }
  };

  const progress = (step / TOTAL_STEPS) * 100;

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleAssessCreditScore)} className="overflow-hidden">
        <div className="p-6 border-b">
          <Progress value={progress} className="w-full" />
          <p className="text-sm text-center mt-2 text-muted-foreground">Step {step} of {TOTAL_STEPS}</p>
        </div>

        <CardContent className="p-8 min-h-[400px] flex items-center justify-center">
          {step === 1 && <WelcomeStep />}
          {step === 2 && <DocumentUploadStep files={files} setFiles={setFiles} />}
          {step === 3 && <QuestionnaireStep />}
          {step === 4 && <CreditScoringStep aiScore={aiScore} />}
        </CardContent>

        <CardFooter className="flex justify-between p-6 bg-muted/30 border-t">
          {step > 1 && step < TOTAL_STEPS + 1 ? (
            <Button type="button" variant="outline" onClick={handlePrevStep}>
              <ArrowLeft className="mr-2 h-4 w-4" /> Previous
            </Button>
          ) : <div />}

          {step < 3 && (
            <Button type="button" onClick={handleNextStep}>
              Next <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          )}
          
          {step === 3 && (
            <Button type="submit" disabled={aiScore.loading}>
              {aiScore.loading ? "Assessing..." : "Assess Credit Score"} <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          )}

          {step === 4 && aiScore.score !== null && (
              <Button type="button" onClick={() => router.push('/dashboard/startup')}>
                  Go to Dashboard <PartyPopper className="ml-2 h-4 w-4" />
              </Button>
          )}

          {step === TOTAL_STEPS && aiScore.score === null && aiScore.error === null && (
               <p className="text-sm text-muted-foreground">Submit the form to see your score.</p>
          )}
        </CardFooter>
      </form>
    </Form>
  );
}
