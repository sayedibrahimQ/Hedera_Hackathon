import { NileFiLogo } from '@/components/common/NileFiLogo';
import { HederaBadge } from '@/components/common/HederaBadge';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { ArrowRight, FileText, Target, TrendingUp, ShieldCheck, Zap, Globe, GaugeCircle, BarChart, Rocket } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AnimatedGridBackground } from '@/components/common/AnimatedGridBackground';
import { Badge } from '@/components/ui/badge';

const FeatureCard = ({ icon, title, description, className }: { icon: React.ReactNode, title: string, description: string, className?: string }) => (
    <Card className={`text-center bg-card/80 backdrop-blur-sm shadow-lg animate-fade-in-up ${className}`}>
        <CardContent className="p-8 flex flex-col items-center">
            <div className="bg-primary/10 p-4 rounded-full mb-6 ring-2 ring-primary/10">
                {icon}
            </div>
            <h3 className="text-xl font-semibold mb-2">{title}</h3>
            <p className="text-foreground/70">{description}</p>
        </CardContent>
    </Card>
);

const HowItWorksCard = ({ icon, title, description, step, className }: { icon: React.ReactNode, title: string, description: string, step: number, className?: string }) => (
     <Card className={`text-center shadow-md animate-fade-in-up ${className}`}>
        <CardContent className="p-6">
            <div className="flex flex-col items-center">
                <div className="bg-primary/10 p-3 rounded-full mb-4 ring-2 ring-primary/20">
                   {icon}
                </div>
                <h3 className="text-xl font-semibold mb-2">{step}. {title}</h3>
                <p className="text-foreground/70 text-sm">{description}</p>
            </div>
        </CardContent>
    </Card>
);

const VisionCard = ({ icon, title, description, className }: { icon: React.ReactNode, title: string, description: string, className?: string }) => (
    <div className={`p-6 bg-card/50 rounded-lg shadow-md animate-fade-in-up ${className}`}>
        <h3 className="text-xl font-semibold mb-2 flex items-center gap-3">{icon}{title}</h3>
        <p className="text-foreground/70">{description}</p>
    </div>
);


export default function Home() {
  return (
    <div className="flex flex-col min-h-screen bg-background">
      <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-14 max-w-screen-2xl items-center justify-between">
          <NileFiLogo />
          <nav className="hidden md:flex items-center gap-4">
             <Button asChild size="sm" className="bg-accent hover:bg-accent/90 text-accent-foreground shadow-sm transition-transform hover:scale-105">
                <Link href="/dashboard/investor">Investor Portal</Link>
            </Button>
            <Button asChild size="sm" variant="outline" className="border-primary text-primary hover:bg-primary/5 hover:text-primary shadow-sm transition-transform hover:scale-105">
                <Link href="/onboarding">Startup Onboarding</Link>
            </Button>
          </nav>
        </div>
      </header>
      <main className="flex-1">
        <section className="relative w-full pt-20 pb-20 md:pt-32 md:pb-24 overflow-hidden">
            <AnimatedGridBackground />
            <div className="container mx-auto px-4 text-center relative z-10">
                <div className="animate-fade-in-up">
                    <h1 className="text-4xl md:text-6xl font-bold text-primary font-headline tracking-tight">
                        Funding Verified. Trust Built on Hedera.
                    </h1>
                    <p className="mt-6 text-lg md:text-xl text-foreground/80 max-w-3xl mx-auto">
                        NileFi is a decentralized financing platform enabling secure, milestone-based funding between investors and African SMEs, bridging the gap between Web2 businesses and Web3 finance.
                    </p>
                    <div className="mt-8 flex flex-col sm:flex-row justify-center gap-4">
                        <Button asChild size="lg" className="bg-accent hover:bg-accent/90 text-accent-foreground shadow-md transition-transform hover:scale-105">
                            <Link href="/dashboard/investor">I’m an Investor <ArrowRight className="ml-2" /></Link>
                        </Button>
                        <Button asChild size="lg" variant="outline" className="border-primary text-primary hover:bg-primary/5 hover:text-primary shadow-sm transition-transform hover:scale-105">
                            <Link href="/onboarding">I’m a Startup <ArrowRight className="ml-2" /></Link>
                        </Button>
                    </div>
                </div>
            </div>
        </section>
        
        <section className="py-20 bg-muted/30">
          <div className="container mx-auto px-4">
            <div className="text-center max-w-3xl mx-auto animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
              <h2 className="text-3xl md:text-4xl font-bold text-center text-primary font-headline mb-4">
                The Trust Deficit in SME Funding
              </h2>
              <p className="text-lg text-foreground/70">
                Traditional SME loans are slow, demand heavy documentation, and expose both investors and businesses to significant risks like fund misuse, lack of progress monitoring, and high operational costs due to intermediaries.
              </p>
            </div>
          </div>
        </section>

        <section className="py-20">
            <div className="container mx-auto px-4">
                 <div className="text-center max-w-3xl mx-auto animate-fade-in-up" style={{ animationDelay: '0s' }}>
                    <h2 className="text-3xl md:text-4xl font-bold text-center text-primary font-headline mb-12">
                        NileFi: Automated Trust & Transparency
                    </h2>
                </div>
                <div className="grid md:grid-cols-3 gap-8">
                    <FeatureCard icon={<ShieldCheck className="w-10 h-10 text-primary" />} title="Milestone-Based Escrow" description="Funds are locked in a Hedera smart contract and released automatically only when predefined milestones are verifiably met, eliminating misuse." className="[animation-delay:0.2s]" />
                    <FeatureCard icon={<Zap className="w-10 h-10 text-primary" />} title="Low-Cost & Fast" description="Leveraging Hedera Hashgraph, we dramatically reduce transaction costs and settlement times compared to traditional banking systems." className="[animation-delay:0.4s]"/>
                    <FeatureCard icon={<Globe className="w-10 h-10 text-primary" />} title="Financial Inclusion" description="We provide a gateway for global investors to securely fund African SMEs, and for businesses to access capital they couldn't before." className="[animation-delay:0.6s]"/>
                </div>
            </div>
        </section>

         <section className="py-20 bg-muted/30">
            <div className="container mx-auto px-4">
                 <div className="text-center max-w-3xl mx-auto animate-fade-in-up" style={{ animationDelay: '0s' }}>
                    <h2 className="text-3xl md:text-4xl font-bold text-center text-primary font-headline mb-12">
                        How It Works
                    </h2>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                    <HowItWorksCard icon={<FileText className="w-8 h-8 text-primary" />} title="Request" description="SMEs create detailed funding requests with clear milestones and documentation." step={1} className="[animation-delay:0.2s]" />
                    <HowItWorksCard icon={<GaugeCircle className="w-8 h-8 text-primary" />} title="Verify" description="NileFi offers premium KYC services, and investors review credibility before committing funds." step={2} className="[animation-delay:0.4s]" />
                    <HowItWorksCard icon={<Target className="w-8 h-8 text-primary" />} title="Fund" description="Investors fund specific milestones, with capital held in a secure Hedera smart contract escrow." step={3} className="[animation-delay:0.6s]" />
                    <HowItWorksCard icon={<TrendingUp className="w-8 h-8 text-primary" />} title="Release" description="Funds are auto-released from escrow as milestones are completed and verified." step={4} className="[animation-delay:0.8s]" />
                </div>
            </div>
        </section>

        <section className="py-20">
            <div className="container mx-auto px-4">
                <div className="text-center max-w-3xl mx-auto animate-fade-in-up" style={{ animationDelay: '0s' }}>
                    <h2 className="text-3xl md:text-4xl font-bold text-center text-primary font-headline mb-12">
                        A Transparent Business Model
                    </h2>
                </div>
                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
                    <Card className="animate-fade-in-up [animation-delay:0.2s]">
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2"><Badge variant="secondary">Main</Badge>Transaction Fees</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-foreground/70">A small 2-3% fee is levied on each funded transaction, ensuring a scalable and transparent revenue stream as the platform grows.</p>
                        </CardContent>
                    </Card>
                     <Card className="animate-fade-in-up [animation-delay:0.4s]">
                        <CardHeader>
                            <CardTitle>Premium Verification</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-foreground/70">SMEs can pay for enhanced "verified" badges, increasing platform trust and providing an additional revenue stream for NileFi.</p>
                        </CardContent>
                    </Card>
                     <Card className="animate-fade-in-up [animation-delay:0.6s]">
                        <CardHeader>
                            <CardTitle>Data & Analytics</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-foreground/70">Aggregated, anonymized performance data is offered to B2B clients like VCs and banks for a subscription fee.</p>
                        </CardContent>
                    </Card>
                     <Card className="animate-fade-in-up [animation-delay:0.8s]">
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2"><Badge variant="outline">Future</Badge>Enterprise API</CardTitle>
                        </CardHeader>
                        <CardContent>
                            <p className="text-foreground/70">A white-label API for other fintechs to integrate our Hedera-based escrow functionality into their own systems.</p>
                        </CardContent>
                    </Card>
                </div>
            </div>
        </section>

         <section className="py-20 bg-muted/30">
          <div className="container mx-auto px-4">
             <div className="text-center max-w-3xl mx-auto animate-fade-in-up" style={{ animationDelay: '0s' }}>
              <h2 className="text-3xl md:text-4xl font-bold text-center text-primary font-headline mb-4">
                Why NileFi is Positioned for Africa
              </h2>
              <p className="text-lg text-foreground/70 mb-12">
                We're not just building a platform; we're building a new economic bridge tailored for the African continent's unique landscape.
              </p>
            </div>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                 <VisionCard icon={<BarChart/>} title="Significant SME Gap" description="Small and Medium-sized Enterprises constitute 90% of African businesses, yet a majority lack access to traditional loans. NileFi opens a new door for them." className="[animation-delay:0.2s]" />
                 <VisionCard icon={<ShieldCheck/>} title="Addressing the Trust Deficit" description="Investors often hesitate due to a perceived lack of transparency. Our automated trust mechanisms and milestone-based control mitigate risk and build confidence." className="[animation-delay:0.4s]" />
                 <VisionCard icon={<TrendingUp/>} title="Rising Digital Adoption" description="Countries like Egypt, Kenya, and Nigeria show robust digital wallet adoption, creating a fertile ground for seamless integration with our platform." className="[animation-delay:0.6s]" />
            </div>
          </div>
        </section>

        <section className="py-20 bg-primary text-primary-foreground">
          <div className="container mx-auto px-4 text-center">
              <div className="max-w-3xl mx-auto animate-fade-in-up">
                <Rocket className="w-12 h-12 mx-auto mb-4" />
                <h2 className="text-3xl md:text-4xl font-bold font-headline mb-4">
                  Our Long-Term Vision
                </h2>
                <p className="text-lg md:text-xl text-primary-foreground/80">
                  To become Africa’s decentralized trust infrastructure for funding — built on Hedera. We are starting with SME financing, but our roadmap includes tokenized micro-investments and a full DeFi ecosystem for African startups.
                </p>
                 <div className="mt-8 flex justify-center">
                    <Button asChild size="lg" variant="secondary" className="shadow-md transition-transform hover:scale-105">
                        <Link href="/onboarding">Join the Future of Funding <ArrowRight className="ml-2" /></Link>
                    </Button>
                </div>
              </div>
          </div>
        </section>

      </main>
      <footer className="py-6 border-t border-border/40">
        <div className="container mx-auto px-4 flex flex-col sm:flex-row justify-between items-center gap-4">
           <p className="text-sm text-muted-foreground">&copy; {new Date().getFullYear()} NileFi. All rights reserved.</p>
          <HederaBadge />
        </div>
      </footer>
    </div>
  );
}
