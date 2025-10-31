import { Rocket } from 'lucide-react';

export function WelcomeStep() {
  return (
    <div className="text-center max-w-lg mx-auto">
        <div className="flex justify-center mb-6">
            <div className="bg-primary/10 rounded-full p-4">
                <Rocket className="w-12 h-12 text-primary" />
            </div>
        </div>
      <h2 className="text-3xl font-bold text-primary mb-4">
        Tell us about your startup.
      </h2>
      <p className="text-muted-foreground">
        Welcome to NileFi! In just a few steps, you can create your startup profile, get a credibility score, and start requesting funding from our network of investors.
      </p>
    </div>
  );
}
