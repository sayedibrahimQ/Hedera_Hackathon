'use client';

import { useToast } from '@/hooks/use-toast';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Check, X } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { useMockData } from '@/hooks/use-mock-data';

export default function AdminPage() {
    const { toast } = useToast();
    const { projects, updateProject, updateMilestoneStatus } = useMockData();

    // Milestones that startups marked as complete and need admin verification
    const milestonesToVerify = projects
        .flatMap(p => 
            p.milestones
                .filter(m => m.status === 'Verified') // 'Verified' means 'Awaiting Admin Verification'
                .map(m => ({ ...m, projectId: p.id, projectName: p.title, startup: p.title.split(' - ')[0] }))
        );

    // Projects that have been submitted but are not yet live for funding
    const pendingProjects = projects.filter(p => p.status === 'Pending Approval');

    const handleVerifyMilestone = (projectId: string, milestoneId: number) => {
        const milestone = milestonesToVerify.find(m => m.projectId === projectId && m.id === milestoneId);
        if (milestone) {
            updateMilestoneStatus(projectId, milestoneId, 'Released');
            toast({
                title: "Milestone Verified!",
                description: `Funds for "${milestone.name}" in project "${milestone.projectName}" have been released.`,
            })
        }
    }
    
    const handleRejectMilestone = (projectId: string, milestoneId: number) => {
        const milestone = milestonesToVerify.find(m => m.projectId === projectId && m.id === milestoneId);
         if (milestone) {
            // Revert status to 'Pending' so the startup can re-submit
            updateMilestoneStatus(projectId, milestoneId, 'Pending');
            toast({
                variant: "destructive",
                title: "Milestone Rejected",
                description: `Milestone "${milestone.name}" in project "${milestone.projectName}" has been rejected.`,
            })
        }
    }

    const handleApproveProject = (projectId: string) => {
        const project = pendingProjects.find(p => p.id === projectId);
        if (project) {
            updateProject(projectId, { status: 'Funding' });
            toast({
                title: "Project Approved",
                description: `"${project.title}" is now live and can be funded by investors.`,
            });
        }
    }

    const handleRejectProject = (projectId: string) => {
        const project = pendingProjects.find(p => p.id === projectId);
        if (project) {
            // For this simulation, we'll just remove the project
            // In a real app, you might set a 'Rejected' status
            updateProject(projectId, { status: 'Rejected' });
            toast({
                variant: "destructive",
                title: "Project Rejected",
                description: `"${project.title}" has been rejected and will not be listed.`,
            });
        }
    }
    
  return (
    <div className="space-y-8">
       <div>
        <h1 className="text-3xl font-bold text-primary tracking-tight">Admin Dashboard</h1>
        <p className="text-muted-foreground">Review submissions, approve projects, and verify milestones.</p>
      </div>

      <Tabs defaultValue="milestones">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="milestones">Milestone Verification</TabsTrigger>
          <TabsTrigger value="projects">Project Approval</TabsTrigger>
        </TabsList>
        <TabsContent value="milestones">
            <Card>
                <CardHeader>
                    <CardTitle>Pending Milestone Verifications</CardTitle>
                    <CardDescription>These milestones have been marked as complete by startups and are awaiting your verification to release funds.</CardDescription>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Startup</TableHead>
                                <TableHead>Project</TableHead>
                                <TableHead>Milestone</TableHead>
                                <TableHead>Proof</TableHead>
                                <TableHead className="text-right">Action</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {milestonesToVerify.length > 0 ? milestonesToVerify.map(m => (
                                <TableRow key={`${m.projectId}-${m.id}`}>
                                    <TableCell className="font-medium">{m.startup}</TableCell>
                                    <TableCell>{m.projectName}</TableCell>
                                    <TableCell>{m.name}</TableCell>
                                    <TableCell>
                                        <Button variant="link" className="p-0 h-auto">View Proof</Button>
                                    </TableCell>
                                    <TableCell className="text-right">
                                        <Button variant="ghost" size="icon" className="text-destructive hover:text-destructive" onClick={() => handleRejectMilestone(m.projectId, m.id)}>
                                            <X className="h-4 w-4" />
                                        </Button>
                                        <Button variant="ghost" size="icon" className="text-green-600 hover:text-green-600" onClick={() => handleVerifyMilestone(m.projectId, m.id)}>
                                            <Check className="h-4 w-4" />
                                        </Button>
                                    </TableCell>
                                </TableRow>
                            )) : (
                                <TableRow>
                                    <TableCell colSpan={5} className="h-24 text-center">
                                        No milestones are currently awaiting verification.
                                    </TableCell>
                                </TableRow>
                            )}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>
        </TabsContent>
        <TabsContent value="projects">
            <Card>
                <CardHeader>
                    <CardTitle>Pending Project Approvals</CardTitle>
                    <CardDescription>These projects have been submitted by startups and are awaiting your approval to be listed for funding.</CardDescription>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Project Title</TableHead>
                                <TableHead>Requested Amount</TableHead>
                                <TableHead>Industry</TableHead>
                                <TableHead>Documents</TableHead>
                                <TableHead className="text-right">Action</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {pendingProjects.length > 0 ? pendingProjects.map(p => (
                                <TableRow key={p.id}>
                                    <TableCell className="font-medium">{p.title}</TableCell>
                                    <TableCell>${p.requestedAmount.toLocaleString()}</TableCell>
                                    <TableCell><Badge variant="outline">{p.title.split(' - ')[0].includes('EcoHarvest') ? 'AgriTech' : 'Logistics'}</Badge></TableCell>
                                    <TableCell>
                                        <Button variant="link" className="p-0 h-auto">View Docs</Button>
                                    </TableCell>
                                    <TableCell className="text-right">
                                        <Button variant="ghost" size="icon" className="text-destructive hover:text-destructive" onClick={() => handleRejectProject(p.id)}>
                                            <X className="h-4 w-4" />
                                        </Button>
                                        <Button variant="ghost" size="icon" className="text-green-600 hover:text-green-600" onClick={() => handleApproveProject(p.id)}>
                                            <Check className="h-4 w-4" />
                                        </Button>
                                    </TableCell>
                                </TableRow>
                            )) : (
                                <TableRow>
                                    <TableCell colSpan={5} className="h-24 text-center">
                                        No projects are currently awaiting approval.
                                    </TableCell>
                                </TableRow>
                            )}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
