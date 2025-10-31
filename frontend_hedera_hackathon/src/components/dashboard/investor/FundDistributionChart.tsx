'use client';

import { Pie, PieChart } from "recharts"

import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
} from "@/components/ui/chart"
import type { FundDistributionDataItem } from "@/hooks/use-mock-data";

const chartConfig = {
  value: {
    label: "Funds",
  },
  'Financial Tech': {
    label: "FinTech",
    color: "hsl(var(--chart-1))",
  },
  'Agriculture Tech': {
    label: "AgriTech",
    color: "hsl(var(--chart-2))",
  },
  'Healthcare Tech': {
    label: "HealthTech",
    color: "hsl(var(--chart-3))",
  },
  'Logistics & Supply Chain': {
    label: "Logistics",
    color: "hsl(var(--chart-4))",
  },
  'E-commerce': {
    label: "E-commerce",
    color: "hsl(var(--chart-5))",
  },
  'Education Tech': {
    label: "EduTech",
    color: "hsl(var(--chart-1))",
  },
  'Renewable Energy': {
    label: "Energy",
    color: "hsl(var(--chart-2))",
  },
  'Other': {
    label: "Other",
    color: "hsl(var(--chart-3))",
  }
} satisfies { [key: string]: { label: string; color: string } } & { value: { label: string } };

type FundDistributionChartProps = {
    data: FundDistributionDataItem[];
}

export function FundDistributionChart({ data }: FundDistributionChartProps) {
  const chartData = data.map(item => ({
    ...item,
    fill: chartConfig[item.name as keyof typeof chartConfig]?.color || 'hsl(var(--muted))'
  }))

  return (
      <ChartContainer
        config={chartConfig as any}
        className="mx-auto aspect-square h-[250px]"
      >
        <PieChart>
          <ChartTooltip
            cursor={false}
            content={<ChartTooltipContent hideLabel />}
          />
          <Pie
            data={chartData}
            dataKey="value"
            nameKey="name"
            innerRadius={60}
            strokeWidth={5}
          >
          </Pie>
        </PieChart>
      </ChartContainer>
  )
}
