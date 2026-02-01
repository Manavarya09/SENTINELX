import { useState } from 'react'
import { motion } from 'framer-motion'
import { Settings as SettingsIcon, Shield, AlertTriangle, Clock } from 'lucide-react'

function Settings() {
  const [settings, setSettings] = useState({
    bruteForceThreshold: 5,
    rateLimitWindow: 60,
    rateLimitMaxRequests: 100,
    enableAlerts: true,
    enableML: false,
    alertEmail: ''
  })

  const handleChange = (key, value) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }))
  }

  const handleSave = () => {
    // In a real app, this would save to backend
    console.log('Saving settings:', settings)
    // Show success message
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Settings</h1>
        <p className="text-muted">Configure SentinelX security parameters</p>
      </div>

      {/* Security Thresholds */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="card"
      >
        <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center">
          <Shield className="h-5 w-5 mr-2 text-primary" />
          Security Thresholds
        </h3>

        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Brute Force Threshold
            </label>
            <p className="text-sm text-muted mb-3">
              Number of failed login attempts before blocking an IP
            </p>
            <input
              type="range"
              min="3"
              max="20"
              value={settings.bruteForceThreshold}
              onChange={(e) => handleChange('bruteForceThreshold', parseInt(e.target.value))}
              className="w-full h-2 bg-surface rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-sm text-muted mt-1">
              <span>3</span>
              <span className="font-medium text-primary">{settings.bruteForceThreshold}</span>
              <span>20</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Rate Limit Window (seconds)
            </label>
            <p className="text-sm text-muted mb-3">
              Time window for rate limiting
            </p>
            <input
              type="range"
              min="30"
              max="300"
              step="30"
              value={settings.rateLimitWindow}
              onChange={(e) => handleChange('rateLimitWindow', parseInt(e.target.value))}
              className="w-full h-2 bg-surface rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-sm text-muted mt-1">
              <span>30s</span>
              <span className="font-medium text-primary">{settings.rateLimitWindow}s</span>
              <span>300s</span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Max Requests per Window
            </label>
            <p className="text-sm text-muted mb-3">
              Maximum number of requests allowed in the rate limit window
            </p>
            <input
              type="range"
              min="50"
              max="1000"
              step="50"
              value={settings.rateLimitMaxRequests}
              onChange={(e) => handleChange('rateLimitMaxRequests', parseInt(e.target.value))}
              className="w-full h-2 bg-surface rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-sm text-muted mt-1">
              <span>50</span>
              <span className="font-medium text-primary">{settings.rateLimitMaxRequests}</span>
              <span>1000</span>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Alert Settings */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="card"
      >
        <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center">
          <AlertTriangle className="h-5 w-5 mr-2 text-warning" />
          Alert Configuration
        </h3>

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-foreground">Enable Real-time Alerts</label>
              <p className="text-sm text-muted">Receive immediate notifications for security events</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.enableAlerts}
                onChange={(e) => handleChange('enableAlerts', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-surface peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/25 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-foreground mb-2">
              Alert Email
            </label>
            <input
              type="email"
              value={settings.alertEmail}
              onChange={(e) => handleChange('alertEmail', e.target.value)}
              placeholder="admin@example.com"
              className="input w-full"
            />
          </div>
        </div>
      </motion.div>

      {/* Advanced Settings */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="card"
      >
        <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center">
          <SettingsIcon className="h-5 w-5 mr-2 text-accent" />
          Advanced Settings
        </h3>

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-foreground">Enable ML Anomaly Detection</label>
              <p className="text-sm text-muted">Use machine learning for advanced threat detection</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={settings.enableML}
                onChange={(e) => handleChange('enableML', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-surface peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-primary/25 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
            </label>
          </div>

          {settings.enableML && (
            <div className="bg-surface/50 p-4 rounded-md">
              <p className="text-sm text-muted mb-2">ML Configuration</p>
              <p className="text-xs text-muted">
                Machine learning features require additional setup and training data.
                Contact your system administrator for configuration.
              </p>
            </div>
          )}
        </div>
      </motion.div>

      {/* Save Button */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="flex justify-end"
      >
        <button
          onClick={handleSave}
          className="btn-primary px-8 py-2"
        >
          Save Settings
        </button>
      </motion.div>
    </div>
  )
}

export default Settings