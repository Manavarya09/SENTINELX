import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend
} from 'recharts'
import { PieChart as PieChartIcon } from 'lucide-react'

function AttackDistribution({ stats }) {
  const data = stats?.by_type ? Object.entries(stats.by_type).map(([type, count]) => ({
    name: type.toUpperCase(),
    value: count,
    color: getAttackTypeColor(type)
  })) : []

  function getAttackTypeColor(type) {
    const colors = {
      sqli: '#EF4444',
      xss: '#F59E0B',
      path_traversal: '#8B5CF6',
      brute_force: '#06B6D4',
      rate_abuse: '#10B981',
      anomaly: '#F97316'
    }
    return colors[type] || '#6B7280'
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center">
        <PieChartIcon className="h-5 w-5 mr-2" />
        Attack Distribution
      </h3>
      {data.length > 0 ? (
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={40}
                outerRadius={80}
                paddingAngle={5}
                dataKey="value"
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1F2937',
                  border: '1px solid #374151',
                  borderRadius: '6px'
                }}
                labelStyle={{ color: '#F3F4F6' }}
              />
              <Legend
                wrapperStyle={{ color: '#F3F4F6' }}
                iconType="circle"
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="h-64 flex items-center justify-center text-muted">
          No attack data available
        </div>
      )}
    </div>
  )
}

export default AttackDistribution