import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Shield, Zap, Eye, Lock } from 'lucide-react'

function Landing() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-surface to-background">
      {/* Hero Section */}
      <div className="relative overflow-hidden">
        {/* Animated background grid */}
        <div className="absolute inset-0 opacity-20">
          <div className="absolute inset-0" style={{
            backgroundImage: `
              linear-gradient(rgba(0, 212, 255, 0.1) 1px, transparent 1px),
              linear-gradient(90deg, rgba(0, 212, 255, 0.1) 1px, transparent 1px)
            `,
            backgroundSize: '50px 50px'
          }} />
        </div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-16">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
              className="inline-block mb-8"
            >
              <Shield className="h-20 w-20 text-primary mx-auto" />
            </motion.div>

            <h1 className="text-4xl md:text-6xl font-bold text-foreground mb-6">
              Sentinel<span className="text-primary">X</span>
            </h1>

            <p className="text-xl md:text-2xl text-muted mb-8 max-w-3xl mx-auto">
              Real-time web attack detection and visualization platform.
              Protect your applications with advanced security monitoring.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/dashboard"
                className="btn-primary text-lg px-8 py-3"
              >
                Access Dashboard
              </Link>
              <Link
                to="/login"
                className="btn-secondary text-lg px-8 py-3"
              >
                Login
              </Link>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Features Section */}
      <div className="py-16 bg-surface/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-foreground mb-4">
              Advanced Security Features
            </h2>
            <p className="text-muted text-lg">
              Comprehensive protection against modern web threats
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="card text-center"
            >
              <Zap className="h-12 w-12 text-primary mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-foreground mb-2">
                Real-time Detection
              </h3>
              <p className="text-muted">
                Instant analysis of HTTP requests with advanced pattern matching
                and anomaly detection algorithms.
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="card text-center"
            >
              <Eye className="h-12 w-12 text-primary mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-foreground mb-2">
                Live Visualization
              </h3>
              <p className="text-muted">
                Interactive dashboards with real-time attack feeds, geographic
                mapping, and time-series analytics.
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              className="card text-center"
            >
              <Lock className="h-12 w-12 text-primary mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-foreground mb-2">
                Risk Scoring
              </h3>
              <p className="text-muted">
                Intelligent risk assessment combining attack confidence,
                frequency, and historical IP behavior.
              </p>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8 text-center">
            <motion.div
              initial={{ opacity: 0, scale: 0.5 }}
              whileInView={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5 }}
              className="card"
            >
              <div className="text-3xl font-bold text-primary mb-2">10K+</div>
              <div className="text-muted">Requests Analyzed</div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, scale: 0.5 }}
              whileInView={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="card"
            >
              <div className="text-3xl font-bold text-critical mb-2">500+</div>
              <div className="text-muted">Attacks Blocked</div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, scale: 0.5 }}
              whileInView={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="card"
            >
              <div className="text-3xl font-bold text-warning mb-2">99.9%</div>
              <div className="text-muted">Detection Rate</div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, scale: 0.5 }}
              whileInView={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              className="card"
            >
              <div className="text-3xl font-bold text-success mb-2">&lt;1ms</div>
              <div className="text-muted">Response Time</div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Landing