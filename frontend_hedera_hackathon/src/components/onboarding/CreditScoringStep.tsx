'use client';

import { useEffect, useState } from 'react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { Loader2, AlertTriangle, CheckCircle } from 'lucide-react';

type AIScoreState = {
  loading: boolean;
  score: number | null;
  explanation: string | null;
  error: string | null;
};

type CreditScoringStepProps = {
  aiScore: AIScoreState;
};

export function CreditScoringStep({ aiScore }: CreditScoringStepProps) {
  const { loading, score, explanation, error } = aiScore;
  const [animatedScore, setAnimatedScore] = useState(0);

  useEffect(() => {
    if (score !== null) {
      const duration = 2000;
      const startTime = Date.now();
      const animate = () => {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        setAnimatedScore(Math.floor(progress * score));
        if (progress < 1) {
          requestAnimationFrame(animate);
        }
      };
      requestAnimationFrame(animate);
    }
  }, [score]);

  const getScoreColor = (s: number) => {
    if (s < 40) return 'bg-destructive';
    if (s < 70) return 'bg-secondary';
    return 'bg-green-500';
  };

  return (
    <div className="w-full max-w-2xl mx-auto text-center">
      <h2 className="text-3xl font-bold text-primary mb-2">Credibility Score</h2>
      <p className="text-muted-foreground mb-8">Your credibility score helps investors trust you.</p>

      {loading && (
        <div className="flex flex-col items-center justify-center">
          <Loader2 className="w-12 h-12 text-primary animate-spin mb-4" />
          <p className="text-lg font-semibold">Analyzing your documents...</p>
          <p className="text-muted-foreground">This may take a moment.</p>
        </div>
      )}

      {error && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Scoring Failed</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {score !== null && (
        <div className="space-y-6">
            <div className="relative h-32 w-32 mx-auto">
                 <svg className="h-full w-full" width="36" height="36" viewBox="0 0 36 36" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="18" cy="18" r="16" fill="none" className="stroke-current text-gray-200 dark:text-gray-700" strokeWidth="2"></circle>
                    <circle cx="18" cy="18" r="16" fill="none" className={`stroke-current ${getScoreColor(score).replace('bg-','text-')}`} strokeWidth="2" strokeDasharray={`${animatedScore}, 100`} strokeLinecap="round" transform="rotate(-90 18 18)"></circle>
                </svg>
                <div className="absolute top-1/2 start-1/2 transform -translate-y-1/2 -translate-x-1/2">
                    <span className="text-center text-3xl font-bold text-gray-800 dark:text-white">{animatedScore}</span>
                </div>
            </div>
            
          <Alert>
            <CheckCircle className="h-4 w-4" />
            <AlertTitle>Analysis Complete</AlertTitle>
            <AlertDescription>
              <p className="font-semibold mb-2">Based on our analysis, your startup has a credit score of {score}.</p>
              <p>{explanation}</p>
            </AlertDescription>
          </Alert>
        </div>
      )}
    </div>
  );
}
