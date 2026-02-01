import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { motion } from 'framer-motion'
import {
  ArrowLeft,
  AlertTriangle,
  Shield,
  Clock,
  MapPin,
  Code,
  ExternalLink
} from 'lucide-react'

function AttackDetails() {
  const { id } = useParams()

  const { data: attack, isLoading, error } = useQuery({
    queryKey: ['attack', id],
    queryFn: async () => {
      const response = await axios.get(`/api/dashboard/attacks/${id}`)
      return response.data
    }
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    )
  }

  if (error || !attack) {
    return (
      <div className="text-center py-12">
        <AlertTriangle className="h-12 w-12 text-critical mx-auto mb-4" />
        <h2 className="text-xl font-semibold text-foreground mb-2">Attack Not Found</h2>
        <p className="text-muted mb-4">The requested attack details could not be found.</p>
        <Link to="/dashboard" className="btn-primary">
          Back to Dashboard
        </Link>
      </div>
    )
  }

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical': return 'text-critical bg-critical/10 border-critical/30'
      case 'high': return 'text-warning bg-warning/10 border-warning/30'
      case 'medium': return 'text-accent bg-accent/10 border-accent/30'
      default: return 'text-info bg-info/10 border-info/30'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-4">
        <Link
          to="/dashboard"
          className="p-2 rounded-md text-muted hover:text-foreground hover:bg-surface/50 transition-colors"
        >
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-foreground">Attack Details</h1>
          <p className="text-muted">ID: {attack.id}</p>
        </div>
      </div>

      {/* Attack Overview */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card"
      >
        <div className="flex items-start justify-between mb-6">
          <div>
            <h2 className="text-xl font-semibold text-foreground mb-2">
              {attack.attack_type.toUpperCase()} Attack
            </h2>
            <p className="text-muted">{attack.explanation}</p>
          </div>
          <div className={`px-4 py-2 rounded-lg border font-medium ${getSeverityColor(attack.severity)}`}>
            {attack.severity.toUpperCase()}
          </div>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="bg-surface/50 p-4 rounded-md">
            <div className="flex items-center space-x-2 mb-2">
              <Shield className="h-4 w-4 text-primary" />
              <span className="text-sm font-medium text-muted">Confidence</span>
            </div>
            <div className="text-2xl font-bold text-foreground">
              {(attack.confidence * 100).toFixed(1)}%
            </div>
          </div>

          <div className="bg-surface/50 p-4 rounded-md">
            <div className="flex items-center space-x-2 mb-2">
              <AlertTriangle className="h-4 w-4 text-critical" />
              <span className="text-sm font-medium text-muted">Risk Score</span>
            </div>
            <div className="text-2xl font-bold text-foreground">
              {attack.risk_score.toFixed(1)}
            </div>
          </div>

          <div className="bg-surface/50 p-4 rounded-md">
            <div className="flex items-center space-x-2 mb-2">
              <Clock className="h-4 w-4 text-info" />
              <span className="text-sm font-medium text-muted">Timestamp</span>
            </div>
            <div className="text-sm text-foreground">
              {new Date(attack.timestamp).toLocaleString()}
            </div>
          </div>

          <div className="bg-surface/50 p-4 rounded-md">
            <div className="flex items-center space-x-2 mb-2">
              <MapPin className="h-4 w-4 text-accent" />
              <span className="text-sm font-medium text-muted">IP Address</span>
            </div>
            <div className="text-sm text-foreground font-mono">
              {attack.request_details?.ip_address || 'Unknown'}
            </div>
          </div>
        </div>
      </motion.div>

      {/* Request Details */}
      {attack.request_details && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="card"
        >
          <h3 className="text-lg font-semibold text-foreground mb-4">Request Details</h3>
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-muted mb-1">Method</label>
              <div className="font-mono text-foreground bg-surface/50 p-2 rounded">
                {attack.request_details.method}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-muted mb-1">Path</label>
              <div className="font-mono text-foreground bg-surface/50 p-2 rounded break-all">
                {attack.request_details.path}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-muted mb-1">User Agent</label>
              <div className="text-sm text-foreground bg-surface/50 p-2 rounded break-all">
                {attack.request_details.user_agent || 'Not provided'}
              </div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Payload */}
      {attack.payload && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="card"
        >
          <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center">
            <Code className="h-5 w-5 mr-2" />
            Malicious Payload
          </h3>
          <div className="bg-surface/50 p-4 rounded-md">
            <pre className="text-sm text-foreground font-mono whitespace-pre-wrap break-all">
              {attack.payload}
            </pre>
          </div>
        </motion.div>
      )}

      {/* Mitigation Suggestions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="card"
      >
        <h3 className="text-lg font-semibold text-foreground mb-4">Suggested Mitigation</h3>
        <div className="space-y-3">
          {getMitigationSuggestions(attack.attack_type).map((suggestion, index) => (
            <div key={index} className="flex items-start space-x-3">
              <div className="w-2 h-2 bg-primary rounded-full mt-2 flex-shrink-0"></div>
              <p className="text-foreground">{suggestion}</p>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  )
}

function getMitigationSuggestions(attackType) {
  const suggestions = {
    sqli: [
      "Use parameterized queries or prepared statements",
      "Implement input validation and sanitization",
      "Use ORM libraries that handle SQL escaping",
      "Limit database user privileges",
      "Implement Web Application Firewall (WAF)"
    ],
    xss: [
      "Implement Content Security Policy (CSP)",
      "Use proper output encoding for user input",
      "Validate and sanitize all user inputs",
      "Use framework-provided XSS protection",
      "Implement input length limits"
    ],
    path_traversal: [
      "Validate and sanitize file paths",
      "Use allowlists for file access",
      "Implement proper path canonicalization",
      "Avoid direct file system access from user input",
      "Use chroot jails or containers"
    ],
    brute_force: [
      "Implement account lockout policies",
      "Use CAPTCHA for failed login attempts",
      "Implement progressive delays",
      "Monitor for unusual login patterns",
      "Use multi-factor authentication"
    ],
    rate_abuse: [
      "Implement rate limiting middleware",
      "Use Redis for distributed rate limiting",
      "Implement request throttling",
      "Monitor API usage patterns",
      "Use API gateways with built-in protection"
    ]
  }

  return suggestions[attackType] || [
    "Implement comprehensive input validation",
    "Use security headers (CSP, HSTS, etc.)",
    "Regular security audits and penetration testing",
    "Keep dependencies updated",
    "Implement proper logging and monitoring"
  ]
}

export default AttackDetails