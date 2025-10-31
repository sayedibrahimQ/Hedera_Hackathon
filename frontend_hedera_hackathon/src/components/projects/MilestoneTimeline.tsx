import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { Check, Circle, CircleCheck, CircleDollarSign, Loader } from 'lucide-react';
import type { Milestone } from '@/hooks/use-mock-data';


type MilestoneTimelineProps = {
  milestones: Milestone[];
  onMarkComplete?: (milestoneId: number, milestoneName: string) => void;
};

const statusConfig = {
  Pending: { icon: Circle, color: 'text-muted-foreground', badge: 'outline', buttonText: 'Mark Complete' },
  Verified: { icon: CircleCheck, color: 'text-blue-500', badge: 'default', buttonText: 'Awaiting Verification' },
  Released: { icon: CircleDollarSign, color: 'text-green-600', badge: 'secondary', buttonText: 'Completed' },
};

export function MilestoneTimeline({ milestones, onMarkComplete }: MilestoneTimelineProps) {
  return (
    <div className="space-y-8">
      {milestones.map((milestone, index) => {
        const config = statusConfig[milestone.status];
        const isLast = index === milestones.length - 1;
        const canMarkComplete = milestone.status === 'Pending' && onMarkComplete;

        return (
          <div key={milestone.id} className="flex gap-4 sm:gap-6">
            <div className="flex flex-col items-center">
              <config.icon className={cn("h-8 w-8 shrink-0", config.color)} />
              {!isLast && <div className="w-px flex-1 bg-border my-2" />}
            </div>
            <div className="flex-1 pb-8">
              <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <p className="font-semibold text-lg">{milestone.name}</p>
                  <p className="text-sm text-muted-foreground">
                    {milestone.percentage}% of total fund | Due: {milestone.expectedDate}
                  </p>
                </div>
                <div className="flex items-center gap-4 mt-2 sm:mt-0">
                  <Badge variant={config.badge as any} className={cn(
                    milestone.status === 'Released' && 'bg-green-100 text-green-800 border-green-200',
                    milestone.status === 'Verified' && 'bg-blue-100 text-blue-800 border-blue-200',
                  )}>
                    {milestone.status}
                  </Badge>
                  {onMarkComplete && (
                    <Button 
                      size="sm" 
                      variant={canMarkComplete ? "outline" : "ghost"} 
                      disabled={!canMarkComplete}
                      onClick={() => onMarkComplete(milestone.id, milestone.name)}
                    >
                      {config.buttonText}
                    </Button>
                  )}
                </div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
