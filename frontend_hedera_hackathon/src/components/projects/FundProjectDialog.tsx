'use client';

import { useState } from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import { Loader2, Wallet } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '../ui/alert';
import { useMockData, type Project, type Milestone } from '@/hooks/use-mock-data';

type FundProjectDialogProps = {
  isOpen: boolean;
  onOpenChange: (isOpen: boolean) => void;
  project: Project;
  availableMilestones: Milestone[];
  account: string | null;
  connectWallet: () => Promise<void>;
};

export function FundProjectDialog({
  isOpen,
  onOpenChange,
  project,
  availableMilestones,
  account,
  connectWallet,
}: FundProjectDialogProps) {
  const { toast } = useToast();
  const { fundProject } = useMockData();
  const [selectedMilestoneId, setSelectedMilestoneId] = useState<string>(
    availableMilestones[0]?.id.toString() || ''
  );
  const [amount, setAmount] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const selectedMilestone = project.milestones.find(
    (m) => m.id.toString() === selectedMilestoneId
  );
  const milestoneTargetAmount = selectedMilestone ? project.requestedAmount * (selectedMilestone.percentage / 100) : 0;


  const handleFundProject = async () => {
    if (!selectedMilestoneId || !amount) {
      toast({
        variant: 'destructive',
        title: 'Missing Information',
        description: 'Please select a milestone and enter an amount.',
      });
      return;
    }
    
    setIsLoading(true);

    // Simulate blockchain transaction
    await new Promise((resolve) => setTimeout(resolve, 2000));
    
    const fundedAmount = parseFloat(amount);
    fundProject(project.id, fundedAmount, selectedMilestone?.name || 'Unknown Milestone');

    setIsLoading(false);
    onOpenChange(false);
    
    toast({
      title: 'Funding Successful!',
      description: `Your contribution of $${amount} to "${selectedMilestone?.name}" is being processed on the Hedera network.`,
    });

    // Reset form
    setAmount('');
  };

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Fund "{project.title}"</DialogTitle>
          <DialogDescription>
            Support this project by funding a specific milestone. Your funds will be held in escrow and released upon milestone completion.
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="milestone" className="text-right">
              Milestone
            </Label>
            <Select
              value={selectedMilestoneId}
              onValueChange={setSelectedMilestoneId}
            >
              <SelectTrigger className="col-span-3">
                <SelectValue placeholder="Select a milestone" />
              </SelectTrigger>
              <SelectContent>
                {availableMilestones.map((milestone) => (
                  <SelectItem key={milestone.id} value={milestone.id.toString()}>
                    {milestone.name} ({milestone.percentage}%)
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="amount" className="text-right">
              Amount (USD)
            </Label>
            <Input
              id="amount"
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder={`Target: $${milestoneTargetAmount.toLocaleString()}`}
              className="col-span-3"
            />
          </div>
           {!account && (
              <Alert variant="destructive" className="col-span-4">
                  <Wallet className="h-4 w-4" />
                  <AlertTitle>Wallet Not Connected</AlertTitle>
                  <AlertDescription>
                      Please connect your wallet to fund this project.
                  </AlertDescription>
              </Alert>
          )}
        </div>
        <DialogFooter>
          <Button type="button" variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
          {account ? (
            <Button type="submit" onClick={handleFundProject} disabled={isLoading || !amount || !selectedMilestoneId}>
                {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                {isLoading ? 'Processing...' : 'Fund Milestone'}
            </Button>
          ) : (
             <Button type="button" onClick={connectWallet}>
                <Wallet className="mr-2 h-4 w-4" />
                Connect Wallet
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
