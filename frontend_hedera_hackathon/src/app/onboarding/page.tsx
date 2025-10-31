import { OnboardingForm } from '@/components/onboarding/OnboardingForm';
import { NileFiLogo } from '@/components/common/NileFiLogo';
import Link from 'next/link';
import { Card } from '@/components/ui/card';

export default function OnboardingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/10 via-background to-background flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-4xl">
        <div className="flex justify-center mb-6">
          <Link href="/">
            <NileFiLogo />
          </Link>
        </div>
        <Card className="shadow-2xl">
          <OnboardingForm />
        </Card>
      </div>
    </div>
  );
}
