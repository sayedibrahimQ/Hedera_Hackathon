'use client';

import { useFormContext } from 'react-hook-form';
import { type OnboardingQuestionnaireData } from '@/lib/schemas';
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { useMockData } from '@/hooks/use-mock-data';

export function QuestionnaireStep() {
  const form = useFormContext<OnboardingQuestionnaireData>();
  const { industryTypes, revenueRanges } = useMockData();
  
  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold text-primary mb-2">Startup Details</h2>
        <p className="text-muted-foreground">This information helps investors evaluate your potential.</p>
      </div>
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <FormField
            control={form.control}
            name="industryType"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Industry Type</FormLabel>
                <Select onValueChange={field.onChange} value={field.value}>
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder="Select an industry" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    {industryTypes.map(type => (
                      <SelectItem key={type} value={type}>{type}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="yearsInOperation"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Years in Operation</FormLabel>
                <FormControl>
                  <Input type="number" placeholder="e.g., 2" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <FormField
            control={form.control}
            name="monthlyRevenueRange"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Monthly Revenue Range (USD)</FormLabel>
                 <Select onValueChange={field.onChange} value={field.value}>
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder="Select a revenue range" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    {revenueRanges.map(range => (
                      <SelectItem key={range} value={range}>{range}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={form.control}
            name="teamSize"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Team Size</FormLabel>
                <FormControl>
                  <Input type="number" placeholder="e.g., 10" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>
        <FormField
          control={form.control}
          name="goalsForNext12Months"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Goals for Next 12 Months</FormLabel>
              <FormControl>
                <Textarea placeholder="e.g., Launch V2, expand to a new market, hire 5 engineers..." {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      </div>
    </div>
  );
}
