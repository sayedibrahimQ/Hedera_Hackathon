'use client';

import { useEffect, useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { ArrowRight, Target } from 'lucide-react';
import Link from 'next/link';
import { FundDistributionChart } from '@/components/dashboard/investor/FundDistributionChart';
import { Skeleton } from '@/components/ui/skeleton';
import { FundProjectDialog } from '@/components/projects/FundProjectDialog';
import { useDashboard } from '../layout';
import { useMockData, type Project } from '@/hooks/use-mock-data';

function ProjectCardSkeleton() {
    return (
        <Card className="flex flex-col">
            <CardHeader>
                <Skeleton className="h-6 w-3/4" />
                <Skeleton className="h-4 w-full mt-2" />
                <Skeleton className="h-4 w-5/6 mt-1" />
            </CardHeader>
            <CardContent className="flex-grow space-y-4">
                 <div className="flex items-center justify-between">
                    <Skeleton className="h-4 w-1/4" />
                    <Skeleton className="h-4 w-1/3" />
                </div>
                 <div className="space-y-2">
                    <Skeleton className="h-2 w-full" />
                </div>
                 <div className="flex items-center gap-2">
                    <Skeleton className="h-5 w-5 rounded-full" />
                    <Skeleton className="h-4 w-1/3" />
                </div>
            </CardContent>
            <CardFooter>
                <Skeleton className="h-10 w-full" />
            </CardFooter>
        </Card>
    )
}


export default function InvestorDashboard() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const { account, connectWallet } = useDashboard();
  const { projects, fundedProjects, fundDistributionData } = useMockData();
  const [availableProjects, setAvailableProjects] = useState<Project[]>([]);


  useEffect(() => {
    async function fetchProjects() {
      try {
        setLoading(true);
        // Simulate network delay
        await new Promise(resolve => setTimeout(resolve, 500));
        setAvailableProjects(projects.filter(p => p.status === 'Funding'));
      } catch (err: any) {
        setError(err.message || "Failed to fetch projects.");
        console.error(err);
      } finally {
        setLoading(false);
      }
    }

    fetchProjects();
  }, [projects]);

  const handleFundNow = (project: Project) => {
    setSelectedProject(project);
  }

  const pendingMilestones = selectedProject?.milestones.filter(m => m.status === 'Pending' || m.status === 'Verified');

  return (
    <>
    {selectedProject && (
        <FundProjectDialog
            isOpen={!!selectedProject}
            onOpenChange={(isOpen) => {
                if (!isOpen) {
                    setSelectedProject(null);
                }
            }}
            project={selectedProject}
            availableMilestones={pendingMilestones || []}
            account={account}
            connectWallet={connectWallet}
        />
    )}
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold text-primary tracking-tight">Available Projects</h2>
        <p className="text-muted-foreground">Discover and fund the next wave of innovation.</p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {loading ? (
            Array.from({ length: 3 }).map((_, i) => <ProjectCardSkeleton key={i} />)
        ) : error ? (
            <div className="md:col-span-2 lg:col-span-3 text-center text-destructive">
                <p>{error}</p>
            </div>
        ) : availableProjects.length > 0 ? (
          availableProjects.map((project) => (
            <Card key={project.id} className="flex flex-col">
              <CardHeader>
                <Link href={`/projects/${project.id}`} className="hover:underline">
                    <CardTitle>{project.title}</CardTitle>
                </Link>
                <CardDescription className="line-clamp-2">{project.description}</CardDescription>
              </CardHeader>
              <CardContent className="flex-grow space-y-4">
                <div className="flex items-center justify-between">
                    <span className="text-sm text-muted-foreground">Requested</span>
                    <span className="font-semibold">${project.requestedAmount.toLocaleString()}</span>
                </div>
                <div className="space-y-1">
                  <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Funded</span>
                      <span>{((project.fundedAmount / project.requestedAmount) * 100).toFixed(0)}%</span>
                  </div>
                  <Progress value={(project.fundedAmount / project.requestedAmount) * 100} />
                </div>
                 <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <Target className="h-4 w-4" />
                      <span>{project.milestones.length} Milestones</span>
                  </div>
              </CardContent>
              <CardFooter>
                <Button className="w-full bg-accent hover:bg-accent/90 text-accent-foreground" onClick={() => handleFundNow(project)}>
                  Fund Now <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </CardFooter>
            </Card>
          ))
        ) : (
            <div className="md:col-span-2 lg:col-span-3 text-center text-muted-foreground py-12">
                <h3 className="text-xl font-semibold">No Projects Available</h3>
                <p>Check back later for new investment opportunities.</p>
            </div>
        )}
      </div>

      <div className="grid gap-8 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Your Funded Projects</CardTitle>
            <CardDescription>Track the progress of your investments.</CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Project</TableHead>
                  <TableHead className="text-right">Total Invested</TableHead>
                  <TableHead>Progress</TableHead>
                  <TableHead>Last Payment</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {fundedProjects.length > 0 ? fundedProjects.map((investment) => (
                  <TableRow key={investment.id}>
                    <TableCell className="font-medium">{investment.project}</TableCell>
                    <TableCell className="text-right">${investment.totalInvested.toLocaleString()}</TableCell>
                    <TableCell>
                      <Progress value={investment.progress} className="w-24" />
                    </TableCell>
                    <TableCell>{investment.lastPayment}</TableCell>
                    <TableCell>
                      <Badge variant={investment.status === 'Completed' ? 'secondary' : 'default'} className={investment.status === 'Completed' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'}>{investment.status}</Badge>
                    </TableCell>
                  </TableRow>
                )) : (
                     <TableRow>
                        <TableCell colSpan={5} className="h-24 text-center">
                            You haven't funded any projects yet.
                        </TableCell>
                    </TableRow>
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>
        <Card>
            <CardHeader>
                <CardTitle>Fund Distribution</CardTitle>
                <CardDescription>Your investment portfolio by industry.</CardDescription>
            </CardHeader>
            <CardContent>
                <FundDistributionChart data={fundDistributionData} />
            </CardContent>
        </Card>
      </div>
    </div>
    </>
  );
}
