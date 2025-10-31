'use client';

import { NileFiLogo } from '@/components/common/NileFiLogo';
import { Button } from '@/components/ui/button';
import {
  SidebarProvider,
  Sidebar,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarHeader,
  SidebarFooter,
  SidebarTrigger,
  SidebarInset,
  useSidebar,
} from '@/components/ui/sidebar';
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from '@/components/ui/dropdown-menu';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Bell, LayoutGrid, LifeBuoy, LogOut, Rocket, User, Wallet } from 'lucide-react';
import Link from 'next/link';
import { useState, useEffect, createContext, useContext } from 'react';
import { useToast } from '@/hooks/use-toast';
import { MockDataProvider } from '@/hooks/use-mock-data';

function HeaderContent() {
    const { isMobile } = useSidebar();
    
    return (
        <header className="flex h-16 items-center justify-between gap-4 border-b bg-card px-4 md:px-6 sticky top-0 z-30">
            <div className="flex items-center gap-2">
                <SidebarTrigger className="md:hidden" />
                <div className='hidden md:block'>
                  <h1 className="font-semibold text-lg">Dashboard</h1>
                </div>
            </div>
            <div className="flex items-center gap-4">
                <Button variant="ghost" size="icon">
                    <Bell className="h-5 w-5" />
                    <span className="sr-only">Notifications</span>
                </Button>
                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                        <Button variant="ghost" className="relative h-9 w-9 rounded-full">
                            <Avatar className="h-9 w-9">
                                <AvatarImage src="https://picsum.photos/seed/nilefi-user/40/40" alt="@investor" />
                                <AvatarFallback>IN</AvatarFallback>
                            </Avatar>
                        </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent className="w-56" align="end">
                        <DropdownMenuLabel>
                            <p>Welcome, Investor</p>
                            <p className="text-xs font-normal text-muted-foreground">investor@example.com</p>
                        </DropdownMenuLabel>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem>
                            <User className="mr-2 h-4 w-4" />
                            <span>Profile</span>
                        </DropdownMenuItem>
                        <DropdownMenuItem>
                            <LifeBuoy className="mr-2 h-4 w-4" />
                            <span>Support</span>
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        <DropdownMenuItem>
                            <LogOut className="mr-2 h-4 w-4" />
                            <span>Log out</span>
                        </DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
            </div>
        </header>
    );
}

type DashboardContextType = {
    account: string | null;
    connectWallet: () => Promise<void>;
};

const DashboardContext = createContext<DashboardContextType | undefined>(undefined);

export function useDashboard() {
    const context = useContext(DashboardContext);
    if (!context) {
        throw new Error('useDashboard must be used within a DashboardLayout');
    }
    return context;
}

declare global {
  interface Window {
    ethereum: any;
  }
}

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
    const [account, setAccount] = useState<string | null>(null);
    const { toast } = useToast();

    const HEDERA_TESTNET_CONFIG = {
        chainId: '0x128', // 296
        chainName: 'Hedera Testnet',
        nativeCurrency: {
            name: 'HBAR',
            symbol: 'HBAR',
            decimals: 18,
        },
        rpcUrls: ['https://testnet.hashio.io/api'],
        blockExplorerUrls: ['https://hashscan.io/testnet/'],
    };

    const connectWallet = async () => {
        if (typeof window.ethereum === 'undefined') {
            toast({
                variant: 'destructive',
                title: 'MetaMask not installed',
                description: 'Please install MetaMask to connect your wallet.',
            });
            return;
        }

        try {
            const accounts = await window.ethereum.request({ method: 'eth_requestAccounts' });
            if (accounts.length > 0) {
                setAccount(accounts[0]);
                await switchToHederaTestnet();
                 toast({
                    title: 'Wallet Connected',
                    description: `Connected with account: ${accounts[0].substring(0, 6)}...${accounts[0].substring(accounts[0].length - 4)}`,
                });
            }
        } catch (error: any) {
            console.error("Error connecting to MetaMask", error);
            toast({
                variant: 'destructive',
                title: 'Connection Failed',
                description: error.message || 'Could not connect to MetaMask.',
            });
        }
    };
    
    const switchToHederaTestnet = async () => {
        try {
            await window.ethereum.request({
                method: 'wallet_switchEthereumChain',
                params: [{ chainId: HEDERA_TESTNET_CONFIG.chainId }],
            });
        } catch (switchError: any) {
            // This error code indicates that the chain has not been added to MetaMask.
            if (switchError.code === 4902) {
                try {
                    await window.ethereum.request({
                        method: 'wallet_addEthereumChain',
                        params: [HEDERA_TESTNET_CONFIG],
                    });
                } catch (addError) {
                    console.error('Failed to add Hedera Testnet', addError);
                    toast({
                        variant: 'destructive',
                        title: 'Network Error',
                        description: 'Failed to add Hedera Testnet to MetaMask.',
                    });
                }
            } else {
                console.error('Failed to switch to Hedera Testnet', switchError);
                 toast({
                    variant: 'destructive',
                    title: 'Network Error',
                    description: 'Failed to switch to Hedera Testnet.',
                });
            }
        }
    };


    const disconnectWallet = () => {
        setAccount(null);
        toast({
            title: 'Wallet Disconnected',
            description: 'Your wallet has been successfully disconnected.',
        });
    };

    const renderWalletButton = () => {
        if (account) {
            return (
                <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                         <Button className="w-full justify-start gap-2">
                            <Wallet className="h-4 w-4" />
                            <span className="group-data-[collapsible=icon]:hidden truncate">
                                {`${account.substring(0, 6)}...${account.substring(account.length - 4)}`}
                            </span>
                        </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent className="w-48" align="end">
                        <DropdownMenuItem onClick={disconnectWallet}>
                            <LogOut className="mr-2 h-4 w-4" />
                            <span>Disconnect</span>
                        </DropdownMenuItem>
                    </DropdownMenuContent>
                </DropdownMenu>
            );
        }

        return (
            <Button className="w-full justify-start gap-2" onClick={connectWallet}>
                <Wallet className="h-4 w-4" />
                <span className="group-data-[collapsible=icon]:hidden">Connect Wallet</span>
            </Button>
        );
    }
    
    return (
        <MockDataProvider>
            <DashboardContext.Provider value={{ account, connectWallet }}>
                <SidebarProvider>
                    <Sidebar variant="inset" side="left" collapsible="icon">
                        <SidebarHeader>
                            <NileFiLogo />
                        </SidebarHeader>
                        <SidebarMenu>
                            <SidebarMenuItem>
                                <SidebarMenuButton asChild tooltip="Investor View">
                                    <Link href="/dashboard/investor">
                                        <LayoutGrid />
                                        <span>Investor View</span>
                                    </Link>
                                </SidebarMenuButton>
                            </SidebarMenuItem>
                            <SidebarMenuItem>
                                <SidebarMenuButton asChild tooltip="Startup View">
                                    <Link href="/dashboard/startup">
                                        <Rocket />
                                        <span>Startup View</span>
                                    </Link>
                                </SidebarMenuButton>
                            </SidebarMenuItem>
                        </SidebarMenu>
                        <SidebarFooter className="mt-auto">
                            {renderWalletButton()}
                        </SidebarFooter>
                    </Sidebar>
                    <SidebarInset>
                        <HeaderContent/>
                        <main className="p-4 md:p-6 lg:p-8">
                            {children}
                        </main>
                    </SidebarInset>
                </SidebarProvider>
            </DashboardContext.Provider>
        </MockDataProvider>
    )
}
