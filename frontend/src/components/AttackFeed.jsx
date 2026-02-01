import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { ExternalLink, MapPin, Clock } from 'lucide-react'

function AttackFeed({ attacks }) {
  if (!attacks || attacks.length === 0) {
    return (
      <div className="card">
        <h3 className="text-lg font-semibold text-foreground mb-4">Recent Attacks</h3>
        <div className="text-center text-muted py-8">
          No recent attacks detected
        </div>
      </div>
    )
  }

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'bg-critical/20 text-critical border-critical/30'
      case 'high': return 'bg-warning/20 text-warning border-warning/30'
      case 'medium': return 'bg-accent/20 text-accent border-accent/30'
      default: return 'bg-info/20 text-info border-info/30'
    }
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-foreground mb-4">Recent Attacks</h3>
      <div className="space-y-3 max-h-96 overflow-y-auto">
        {attacks.map((attack, index) => (
          <motion.div
            key={attack.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.05 }}
            className="p-3 bg-surface/50 rounded-md border border-border hover:border-primary/30 transition-colors"
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex-1">
                <div className="flex items-center space-x-2 mb-1">
                  <span className="font-medium text-foreground text-sm">
                    {attack.attack_type.toUpperCase()}
                  </span>
                  <span className={`px-2 py-0.5 rounded text-xs font-medium border ${getSeverityColor(attack.severity)}`}>
                    {attack.severity}
                  </span>
                </div>
                <p className="text-xs text-muted truncate">
                  {attack.explanation}
                </p>
              </div>
              <Link
                to={`/attacks/${attack.id}`}
                className="text-primary hover:text-primary/80 ml-2"
              >
                <ExternalLink className="h-4 w-4" />
              </Link>
            </div>
            <div className="flex items-center justify-between text-xs text-muted">
              <div className="flex items-center space-x-1">
                <Clock className="h-3 w-3" />
                <span>{new Date(attack.timestamp).toLocaleTimeString()}</span>
              </div>
              <div className="flex items-center space-x-1">
                <span>Risk: {attack.risk_score.toFixed(1)}</span>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  )
}

export default AttackFeed