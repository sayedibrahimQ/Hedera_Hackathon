'use client';

import { createContext, useContext, useState, ReactNode } from 'react';
import {
    projects as initialProjects,
    fundedProjects as initialFundedProjects,
    fundDistributionData as initialFundDistributionData,
    loanData as initialLoanData,
    industryTypes as staticIndustryTypes,
    revenueRanges as staticRevenueRanges,
} from '@/lib/data';
import { format } from 'date-fns';

// Types from data.ts
export type Milestone = typeof initialProjects[0]['milestones'][0];
export type Project = typeof initialProjects[0];
export type FundedProject = typeof initialFundedProjects[0];
export type FundDistributionDataItem = typeof initialFundDistributionData[0];
export type LoanData = typeof initialLoanData;

interface MockDataContextType {
    projects: Project[];
    fundedProjects: FundedProject[];
    fundDistributionData: FundDistributionDataItem[];
    loanData: LoanData;
    industryTypes: string[];
    revenueRanges: string[];
    updateProject: (projectId: string, updates: Partial<Project>) => void;
    updateMilestoneStatus: (projectId: string, milestoneId: number, newStatus: Milestone['status']) => void;
    fundProject: (projectId: string, amount: number, milestoneName: string) => void;
    makeLoanRepayment: (repaymentId: number) => void;
}

const MockDataContext = createContext<MockDataContextType | undefined>(undefined);

export const MockDataProvider = ({ children }: { children: ReactNode }) => {
    const [projects, setProjects] = useState<Project[]>(initialProjects);
    const [fundedProjects, setFundedProjects] = useState<FundedProject[]>(initialFundedProjects);
    const [fundDistributionData, setFundDistributionData] = useState<FundDistributionDataItem[]>(initialFundDistributionData);
    const [loanData, setLoanData] = useState<LoanData>(initialLoanData);

    const industryTypes = staticIndustryTypes;
    const revenueRanges = staticRevenueRanges;

    const updateProject = (projectId: string, updates: Partial<Project>) => {
        setProjects(prev => prev.map(p => (p.id === projectId ? { ...p, ...updates } : p)));
    };

    const updateMilestoneStatus = (projectId: string, milestoneId: number, newStatus: Milestone['status']) => {
        setProjects(prev =>
            prev.map(p =>
                p.id === projectId
                    ? {
                        ...p,
                        milestones: p.milestones.map(m =>
                            m.id === milestoneId ? { ...m, status: newStatus } : m
                        ),
                    }
                    : p
            )
        );
    };

    const fundProject = (projectId: string, amount: number, milestoneName: string) => {
        let updatedProject: Project | undefined;
    
        // 1. Update Projects state
        setProjects(currentProjects => {
            const newProjects = currentProjects.map(p => {
                if (p.id === projectId) {
                    const newFundedAmount = p.fundedAmount + amount;
                    const isCompleted = newFundedAmount >= p.requestedAmount;
                    updatedProject = {
                        ...p,
                        fundedAmount: newFundedAmount,
                        status: isCompleted ? 'Completed' : p.status,
                        transactionHistory: [
                            ...p.transactionHistory,
                            {
                                id: `tx-${Date.now()}`,
                                milestone: milestoneName,
                                amount: amount,
                                date: format(new Date(), 'yyyy-MM-dd'),
                                hash: `0.0.98765@${Math.floor(Date.now() / 1000)}.${Math.floor(Math.random() * 1000000000)}`
                            }
                        ]
                    };
                    return updatedProject;
                }
                return p;
            });
            return newProjects;
        });
    
        if (!updatedProject) {
            return;
        }
    
        // 2. Update Funded Projects list (for investor dashboard)
        setFundedProjects(prevFunded => {
            const finalUpdatedProject = updatedProject!;
            const existingFundedProject = prevFunded.find(fp => finalUpdatedProject.title.toLowerCase().includes(fp.project.toLowerCase()));
    
            if (existingFundedProject) {
                return prevFunded.map(fp =>
                    fp.id === existingFundedProject.id
                        ? {
                            ...fp,
                            totalInvested: fp.totalInvested + amount,
                            lastPayment: format(new Date(), 'yyyy-MM-dd'),
                            progress: Math.min(100, Math.round((finalUpdatedProject.fundedAmount / finalUpdatedProject.requestedAmount) * 100)),
                            status: finalUpdatedProject.status === 'Completed' ? 'Completed' : 'Active',
                          }
                        : fp
                );
            } else {
                return [
                    ...prevFunded,
                    {
                        id: `funded-${Date.now()}`,
                        project: finalUpdatedProject.title.split(' - ')[0],
                        totalInvested: amount,
                        progress: Math.min(100, Math.round((finalUpdatedProject.fundedAmount / finalUpdatedProject.requestedAmount) * 100)),
                        lastPayment: format(new Date(), 'yyyy-MM-dd'),
                        status: 'Active',
                    },
                ];
            }
        });
    
        // 3. Update Fund Distribution chart data
        setFundDistributionData(prevDistribution => {
            const finalUpdatedProject = updatedProject!;
            const projectIndustry = industryTypes.find(ind => 
                finalUpdatedProject.title.toLowerCase().includes(ind.split(' ')[0].toLowerCase().replace('&',''))
            ) || 'Other';

            const existingIndustry = prevDistribution.find(fd => fd.name === projectIndustry);
    
            if (existingIndustry) {
                return prevDistribution.map(fd =>
                    fd.name === projectIndustry
                        ? { ...fd, value: fd.value + amount }
                        : fd
                );
            } else {
                return [...prevDistribution, { name: projectIndustry as FundDistributionDataItem['name'], value: amount, fill: 'hsl(var(--chart-5))' }];
            }
        });
    };
    
    const makeLoanRepayment = (repaymentId: number) => {
        setLoanData(prev => ({
            ...prev,
            repaymentSchedule: prev.repaymentSchedule.map(r =>
                r.id === repaymentId ? { ...r, status: 'Paid' } : r
            )
        }));
    };

    const value = {
        projects,
        fundedProjects,
        fundDistributionData,
        loanData,
        industryTypes,
        revenueRanges,
        updateProject,
        updateMilestoneStatus,
        fundProject,
        makeLoanRepayment,
    };

    return (
        <MockDataContext.Provider value={value}>
            {children}
        </MockDataContext.Provider>
    );
};

export const useMockData = () => {
    const context = useContext(MockDataContext);
    if (context === undefined) {
        throw new Error('useMockData must be used within a MockDataProvider');
    }
    return context;
};
