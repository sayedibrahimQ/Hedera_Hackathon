'use client';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Progress } from '@/components/ui/progress';
import { MoreHorizontal, PlusCircle } from 'lucide-react';
import Link from 'next/link';

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useMockData } from '@/hooks/use-mock-data';
import { useToast } from '@/hooks/use-toast';


export default function StartupDashboard() {
  const { projects, updateMilestoneStatus } = useMockData();
  const { toast } = useToast();
  // In a real app, this would be filtered by the logged-in user's ID
  const userProjects = projects.slice(0, 2); 

  const handleMarkComplete = (projectId: string, milestoneId: number, milestoneName: string) => {
    updateMilestoneStatus(projectId, milestoneId, 'Verified');
    toast({
        title: "Milestone Submitted",
        description: `"${milestoneName}" has been submitted for verification.`
    })
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold text-primary tracking-tight">Your Funding Requests</h2>
          <p className="text-muted-foreground">Manage your projects and track their funding progress.</p>
        </div>
        <Button asChild>
          <Link href="/onboarding">
            <PlusCircle className="mr-2 h-4 w-4" />
            Create Funding Request
          </Link>
        </Button>
      </div>

      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Project</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Requested</TableHead>
                <TableHead>Funded</TableHead>
                <TableHead>Next Milestone</TableHead>
                <TableHead><span className="sr-only">Actions</span></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {userProjects.map((project) => {
                const fundedPercentage = (project.fundedAmount / project.requestedAmount) * 100;
                const nextMilestone = project.milestones.find(m => m.status === 'Pending');

                return (
                  <TableRow key={project.id}>
                    <TableCell className="font-medium">
                        <Link href={`/projects/${project.id}`} className="hover:underline">
                            {project.title}
                        </Link>
                    </TableCell>
                    <TableCell>
                      <Badge variant={project.status === 'Completed' ? 'outline' : 'default'}>{project.status}</Badge>
                    </TableCell>
                    <TableCell>${project.requestedAmount.toLocaleString()}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <span>${project.fundedAmount.toLocaleString()}</span>
                        <Progress value={fundedPercentage} className="w-20 h-2" />
                      </div>
                    </TableCell>
                    <TableCell>
                      {nextMilestone ? nextMilestone.name : (project.status === 'Completed' ? 'All completed' : 'Awaiting verification')}
                    </TableCell>
                     <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button aria-haspopup="true" size="icon" variant="ghost">
                            <MoreHorizontal className="h-4 w-4" />
                            <span className="sr-only">Toggle menu</span>
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuLabel>Actions</DropdownMenuLabel>
                          <DropdownMenuItem asChild>
                            <Link href={`/projects/${project.id}`}>View Details</Link>
                          </DropdownMenuItem>
                          <DropdownMenuItem disabled>Edit Request</DropdownMenuItem>
                           {nextMilestone && (
                            <DropdownMenuItem onClick={() => handleMarkComplete(project.id, nextMilestone.id, nextMilestone.name)}>
                                Mark Milestone Complete
                            </DropdownMenuItem>
                           )}
                          {project.status === 'Completed' && (
                            <>
                              <DropdownMenuSeparator />
                              <DropdownMenuItem asChild>
                                <Link href="/dashboard/startup/repayments">Manage Repayments</Link>
                              </DropdownMenuItem>
                            </>
                          )}
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
