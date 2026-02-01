import { motion } from 'framer-motion'
import {
  Shield,
  AlertTriangle,
  Activity,
  TrendingUp,
  Users,
  Clock
} from 'lucide-react'

function KPICards({ stats }) {
  const cards = [
    {
      title: 'Total Requests',
      value: stats?.total_requests?.toLocaleString() || '0',
      icon: Activity,
      color: 'text-info',
      bgColor: 'bg-info/10'
    },
    {
      title: 'Active Attacks',
      value: stats?.attack_count?.toLocaleString() || '0',
      icon: AlertTriangle,
      color: 'text-critical',
      bgColor: 'bg-critical/10'
    },
    {
      title: 'Attack Rate',
      value: `${stats?.attack_rate?.toFixed(1) || '0'}%`,
      icon: TrendingUp,
      color: 'text-warning',
      bgColor: 'bg-warning/10'
    },
    {
      title: 'System Status',
      value: 'Active',
      icon: Shield,
      color: 'text-success',
      bgColor: 'bg-success/10'
    }
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {cards.map((card, index) => (
        <motion.div
          key={card.title}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.1 }}
          className="card"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-muted text-sm">{card.title}</p>
              <p className="text-2xl font-bold text-foreground mt-1">
                {card.value}
              </p>
            </div>
            <div className={`p-3 rounded-lg ${card.bgColor}`}>
              <card.icon className={`h-6 w-6 ${card.color}`} />
            </div>
          </div>
        </motion.div>
      ))}
    </div>
  )
}

export default KPICards