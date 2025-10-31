'use client';

import { useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { ArrowLeft, CreditCard, DollarSign, Calendar, Info, Loader2 } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import Link from 'next/link';
import { useMockData } from '@/hooks/use-mock-data';

export default function RepaymentsPage() {
  const { toast } = useToast();
  const { loanData, makeLoanRepayment } = useMockData();
  const [payingId, setPayingId] = useState<number | null>(null);

  const totalRepaid = loanData.repaymentSchedule
    .filter(r => r.status === 'Paid')
    .reduce((acc, r) => acc + r.amount, 0);

  const nextPayment = loanData.repaymentSchedule.find(r => r.status === 'Due');

  const handleMakePayment = async (repaymentId: number) => {
    setPayingId(repaymentId);
    
    // Simulate payment processing
    await new Promise(resolve => setTimeout(resolve, 1500));

    makeLoanRepayment(repaymentId);

    toast({
      title: 'Payment Successful',
      description: `Payment for installment #${repaymentId} has been processed.`,
    });
    setPayingId(null);
  }

  const getStatusBadge = (status: 'Paid' | 'Due' | 'Overdue') => {
    switch (status) {
      case 'Paid':
        return <Badge variant="secondary" className="bg-green-100 text-green-800">Paid</Badge>;
      case 'Due':
        return <Badge variant="default" className="bg-blue-100 text-blue-800">Due</Badge>;
      case 'Overdue':
        return <Badge variant="destructive">Overdue</Badge>;
    }
  }

  return (
    <div className="space-y-8">
       <div>
         <Button asChild variant="ghost" className="mb-4">
           <Link href="/dashboard/startup">
              <ArrowLeft className="mr-2 h-4 w-4" /> Back to Dashboard
            </Link>
          </Button>
        <h1 className="text-3xl font-bold text-primary tracking-tight">Loan Repayment</h1>
        <p className="text-muted-foreground">Manage and track your repayment schedule for "{loanData.projectName}".</p>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Loan Amount</CardTitle>
                <DollarSign className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
                <div className="text-2xl font-bold">${loanData.totalAmount.toLocaleString()}</div>
                <p className="text-xs text-muted-foreground">Total principal funded</p>
            </CardContent>
        </Card>
        <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Amount Repaid</CardTitle>
                <Info className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
                <div className="text-2xl font-bold">${totalRepaid.toLocaleString()}</div>
                <p className="text-xs text-muted-foreground">{((totalRepaid / loanData.totalAmount) * 100).toFixed(0)}% of total</p>
            </CardContent>
        </Card>
        <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Next Payment Due</CardTitle>
                <Calendar className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
                <div className="text-2xl font-bold">{nextPayment ? `$${nextPayment.amount.toLocaleString()}` : 'N/A'}</div>
                <p className="text-xs text-muted-foreground">
                    {nextPayment ? `Due on ${nextPayment.dueDate}` : 'All payments complete!'}
                </p>
            </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
            <CardTitle>Repayment Schedule</CardTitle>
            <CardDescription>This is the schedule for your loan repayments. Payments are made in HBAR equivalent.</CardDescription>
        </CardHeader>
        <CardContent>
            <Table>
                <TableHeader>
                    <TableRow>
                        <TableHead>Installment</TableHead>
                        <TableHead>Due Date</TableHead>
                        <TableHead>Amount</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead className="text-right">Action</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {loanData.repaymentSchedule.map(repayment => (
                        <TableRow key={repayment.id}>
                            <TableCell className="font-medium">Installment #{repayment.id}</TableCell>
                            <TableCell>{repayment.dueDate}</TableCell>
                            <TableCell>${repayment.amount.toLocaleString()}</TableCell>
                            <TableCell>{getStatusBadge(repayment.status)}</TableCell>
                            <TableCell className="text-right">
                                {repayment.status === 'Due' || repayment.status === 'Overdue' ? (
                                    <Button size="sm" onClick={() => handleMakePayment(repayment.id)} disabled={payingId === repayment.id}>
                                        {payingId === repayment.id ? (
                                            <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Processing...</>
                                        ) : (
                                            <><CreditCard className="mr-2 h-4 w-4" /> Make Payment</>
                                        )}
                                    </Button>
                                ) : (
                                    <span className="text-xs text-muted-foreground">No action needed</span>
                                )}
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </CardContent>
      </Card>
    </div>
  );
}
