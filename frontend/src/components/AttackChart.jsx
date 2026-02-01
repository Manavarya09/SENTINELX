import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts'
import { TrendingUp } from 'lucide-react'

function AttackChart() {
  const { data: timeline, isLoading } = useQuery({
    queryKey: ['attack-timeline'],
    queryFn: async () => {
      const response = await axios.get('/api/dashboard/timeline')
      return response.data
    },
    refetchInterval: 60000, // Refresh every minute
  })

  if (isLoading) {
    return (
      <div className="card">
        <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center">
          <TrendingUp className="h-5 w-5 mr-2" />
          Attack Timeline
        </h3>
        <div className="h-64 flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      </div>
    )
  }

  const chartData = timeline?.timeline?.map(point => ({
    time: new Date(point.timestamp).toLocaleTimeString(),
    attacks: point.attacks
  })) || []

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center">
        <TrendingUp className="h-5 w-5 mr-2" />
        Attack Timeline (Last 24h)
      </h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis
              dataKey="time"
              stroke="#9CA3AF"
              fontSize={12}
            />
            <YAxis
              stroke="#9CA3AF"
              fontSize={12}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#1F2937',
                border: '1px solid #374151',
                borderRadius: '6px'
              }}
              labelStyle={{ color: '#F3F4F6' }}
            />
            <Line
              type="monotone"
              dataKey="attacks"
              stroke="#00D4FF"
              strokeWidth={2}
              dot={{ fill: '#00D4FF', strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6, stroke: '#00D4FF', strokeWidth: 2 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

export default AttackChart