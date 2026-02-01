import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import {
  Shield,
  AlertTriangle,
  Activity,
  Globe,
  TrendingUp,
  Clock
} from 'lucide-react'
import AttackFeed from '../components/AttackFeed'
import KPICards from '../components/KPICards'
import AttackChart from '../components/AttackChart'
import WorldMap from '../components/WorldMap'
import AttackDistribution from '../components/AttackDistribution'
import { useAuth } from '../hooks/useAuth'

function Dashboard() {
  const { user } = useAuth()
  const [liveData, setLiveData] = useState(null)

  // Fetch dashboard stats
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['dashboard-stats'],
    queryFn: async () => {
      const response = await axios.get('/api/dashboard/stats')
      return response.data
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  })

  // Fetch recent attacks
  const { data: attacks, isLoading: attacksLoading } = useQuery({
    queryKey: ['recent-attacks'],
    queryFn: async () => {
      const response = await axios.get('/api/dashboard/attacks/recent')
      return response.data
    },
    refetchInterval: 10000, // Refresh every 10 seconds
  })

  // WebSocket connection for live updates
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/live')

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      setLiveData(data)
    }

    ws.onclose = () => {
      console.log('WebSocket connection closed')
    }

    return () => {
      ws.close()
    }
  }, [])

  if (statsLoading || attacksLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Security Dashboard</h1>
          <p className="text-muted">Real-time attack monitoring and analysis</p>
        </div>
        <div className="flex items-center space-x-2 text-sm text-muted">
          <Clock className="h-4 w-4" />
          <span>Last updated: {new Date().toLocaleTimeString()}</span>
        </div>
      </div>

      {/* Live Update Indicator */}
      {liveData && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-primary/10 border border-primary/20 rounded-lg p-4"
        >
          <div className="flex items-center space-x-2">
            <Activity className="h-5 w-5 text-primary animate-pulse" />
            <span className="text-primary font-medium">Live Update:</span>
            <span className="text-foreground">
              {liveData.type === 'attack_detected'
                ? `New ${liveData.data.attack_type} attack detected`
                : 'Statistics updated'
              }
            </span>
          </div>
        </motion.div>
      )}

      {/* KPI Cards */}
      <KPICards stats={stats} />

      {/* Charts Row */}
      <div className="grid lg:grid-cols-2 gap-6">
        <AttackChart />
        <AttackDistribution stats={stats} />
      </div>

      {/* Map and Feed Row */}
      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <WorldMap />
        </div>
        <div>
          <AttackFeed attacks={attacks} />
        </div>
      </div>

      {/* Recent Alerts */}
      {stats?.recent_alerts && stats.recent_alerts.length > 0 && (
        <div className="card">
          <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center">
            <AlertTriangle className="h-5 w-5 mr-2 text-warning" />
            Recent Security Alerts
          </h3>
          <div className="space-y-3">
            {stats.recent_alerts.map((alert, index) => (
              <motion.div
                key={alert.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-center justify-between p-3 bg-surface/50 rounded-md"
              >
                <div>
                  <p className="font-medium text-foreground">{alert.title}</p>
                  <p className="text-sm text-muted">{alert.created_at}</p>
                </div>
                <div className={`px-2 py-1 rounded text-xs font-medium ${
                  alert.severity === 'critical' ? 'bg-critical/20 text-critical' :
                  alert.severity === 'high' ? 'bg-warning/20 text-warning' :
                  'bg-info/20 text-info'
                }`}>
                  {alert.severity}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard