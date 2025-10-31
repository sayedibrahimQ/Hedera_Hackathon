'use client';

import { useState, useEffect } from 'react';
import { notFound, useRouter } from 'next/navigation';
import Image from 'next/image';
import Link from 'next/link';
import { PlaceHolderImages } from '@/lib/placeholder-images';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { MilestoneTimeline } from '@/components/projects/MilestoneTimeline';
import { DollarSign, FileText, ExternalLink, Loader2 } from 'lucide-react';
import { HederaBadge } from '@/components/common/HederaBadge';
import { FundProjectDialog } from '@/components/projects/FundProjectDialog';
import { api } from '@/lib/api';
import { format } from 'date-fns';
import { useDashboard } from '@/app/dashboard/layout';
import { useMockData } from '@/hooks/use-mock-data';
import { useToast } from '@/hooks/use-toast';

type Transaction = {
  transaction_id: string;
  consensus_timestamp: string;
  result: string;
  transfers: { account: string; amount: number; is_approval: boolean }[];
};

type FormattedTransaction = {
  id: string;
  milestone: string;
  amount: number;
  date: string;
  hash: string;
};

export default function ProjectDetailsPage({ params }: { params: { id: string } }) {
  const { projects, updateMilestoneStatus } = useMockData();
  const project = projects.find((p) => p.id === params.id);
  
  const bannerImage = PlaceHolderImages[0];
  const [isFundDialogOpen, setIsFundDialogOpen] = useState(false);
  const [transactions, setTransactions] = useState<FormattedTransaction[]>(project?.transactionHistory || []);
  const [isLoadingTx, setIsLoadingTx] = useState(false);
  const { account, connectWallet } = useDashboard();
  const { toast } = useToast();
  const router = useRouter();


  useEffect(() => {
    const fetchTransactions = async () => {
      if (!project || project.transactionHistory.length === 0) return;

      setIsLoadingTx(true);
      try {
        const liveTxs = await Promise.all(
          project.transactionHistory.map(async (tx) => {
            // The hash from mock data needs to be converted to a format the mirror node API accepts
            const hederaTxId = tx.hash.replace('...', '').replace('0.0.', '0.0.').replace('@', '-');
            const { transactions: apiTransactions } = await api.hedera.get<{transactions: Transaction[]}>(`/transactions/${hederaTxId}`);
            
            if (apiTransactions && apiTransactions.length > 0) {
              const liveTx = apiTransactions[0];
              const transfer = liveTx.transfers.find(t => t.amount > 0); // Find the credit transaction
              return {
                id: liveTx.transaction_id,
                milestone: tx.milestone, // Milestone info isn't on-chain, so we use mock data
                amount: transfer ? transfer.amount / 100_000_000 : tx.amount, // Convert from tinybar
                date: format(new Date(parseInt(liveTx.consensus_timestamp.split('.')[0]) * 1000), 'yyyy-MM-dd'),
                hash: liveTx.transaction_id,
              };
            }
            return tx; // Fallback to mock tx if API fails
          })
        );
        setTransactions(liveTxs);
      } catch (error) {
        console.error("Failed to fetch live transactions:", error);
        // In case of error, we just stick with the mock data
        if(project) setTransactions(project.transactionHistory);
      } finally {
        setIsLoadingTx(false);
      }
    };

    fetchTransactions();
  }, [project]);


  if (!project) {
    // Give a chance for data to load
    if (projects.length > 0) notFound();
    return <div className="flex justify-center items-center h-64"><Loader2 className="h-8 w-8 animate-spin" /></div>;
  }
  
  if (project.status === 'Rejected') {
      toast({
          variant: 'destructive',
          title: 'Project Not Found',
          description: 'This project is no longer listed on the platform.'
      })
      router.push('/dashboard/investor');
      return null;
  }

  const handleMarkComplete = (milestoneId: number, milestoneName: string) => {
    updateMilestoneStatus(project.id, milestoneId, 'Verified');
     toast({
        title: "Milestone Submitted",
        description: `"${milestoneName}" has been submitted for verification.`
    })
  }

  const fundedPercentage = (project.fundedAmount / project.requestedAmount) * 100;
  const pendingMilestones = project.milestones.filter(m => m.status === 'Pending' || m.status === 'Verified');


  return (
    <>
    <FundProjectDialog
        isOpen={isFundDialogOpen}
        onOpenChange={setIsFundDialogOpen}
        project={project}
        availableMilestones={pendingMilestones}
        account={account}
        connectWallet={connectWallet}
      />
    <div className="space-y-8">
      <Card className="overflow-hidden">
        <div className="relative h-48 w-full md:h-64">
          <Image
            src={bannerImage.imageUrl}
            alt={project.title}
            fill
            className="object-cover"
            data-ai-hint={bannerImage.imageHint}
          />
          <div className="absolute inset-0 bg-black/50" />
          <div className="absolute inset-0 flex flex-col justify-end p-6">
            <h1 className="text-3xl md:text-4xl font-bold text-white font-headline">{project.title}</h1>
            <p className="text-lg text-white/90 max-w-3xl">{project.description}</p>
          </div>
        </div>
        <div className="p-6 border-t grid md:grid-cols-3 gap-6">
          <div className="md:col-span-2 space-y-4">
             <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Funded</span>
                    <span className="font-semibold">${project.fundedAmount.toLocaleString()} / ${project.requestedAmount.toLocaleString()}</span>
                </div>
                <Progress value={fundedPercentage} />
              </div>
          </div>
          <div className="flex items-center justify-end">
            <Button size="lg" className="bg-accent hover:bg-accent/90 text-accent-foreground" onClick={() => setIsFundDialogOpen(true)} disabled={project.status !== 'Funding'}>
                <DollarSign className="mr-2 h-5 w-5" /> {project.status === 'Funding' ? 'Fund Milestone' : project.status}
            </Button>
          </div>
        </div>
      </Card>

      <Tabs defaultValue="milestones">
        <TabsList>
          <TabsTrigger value="milestones">Milestones</TabsTrigger>
          <TabsTrigger value="documents">Documents</TabsTrigger>
          <TabsTrigger value="history">Transaction History</TabsTrigger>
        </TabsList>
        <TabsContent value="milestones">
          <Card>
            <CardHeader>
              <CardTitle>Project Milestones</CardTitle>
            </CardHeader>
            <CardContent>
              <MilestoneTimeline milestones={project.milestones} onMarkComplete={handleMarkComplete} />
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="documents">
          <Card>
            <CardHeader>
              <CardTitle>Project Documents</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    {project.documents.map((doc, index) => (
                        <a key={index} href={doc.url} target="_blank" rel="noopener noreferrer" className="block">
                            <Card className="hover:border-primary hover:bg-primary/5 transition-all">
                                <CardContent className="p-4 flex items-center gap-4">
                                    <FileText className="h-8 w-8 text-primary"/>
                                    <span className="font-medium truncate">{doc.name}</span>
                                </CardContent>
                            </Card>
                        </a>
                    ))}
                </div>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="history">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                Transaction History
                {isLoadingTx && <Loader2 className="h-5 w-5 animate-spin text-primary" />}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Milestone</TableHead>
                    <TableHead>Amount (HBAR)</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead className='w-[40%]'>Hedera Transaction ID</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {transactions.length > 0 ? transactions.map((tx) => (
                    <TableRow key={tx.id}>
                      <TableCell>{tx.milestone}</TableCell>
                      <TableCell>{tx.amount.toLocaleString()}</TableCell>
                      <TableCell>{tx.date}</TableCell>
                      <TableCell>
                        <Link href={`https://hashscan.io/testnet/transaction/${tx.hash}`} target='_blank' rel="noopener noreferrer" className="font-mono text-xs flex items-center gap-1 hover:underline text-accent">
                          {tx.hash}
                          <ExternalLink className="h-3 w-3" />
                        </Link>
                      </TableCell>
                    </TableRow>
                  )) : (
                     <TableRow>
                        <TableCell colSpan={4} className="h-24 text-center">
                            No transactions found for this project yet.
                        </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
              <div className="flex justify-end pt-4">
                  <HederaBadge />
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
    </>
  );
}
