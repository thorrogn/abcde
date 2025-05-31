"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { CheckCircle, XCircle, AlertCircle, RefreshCw } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { checkApiHealth, fetchSystemStatus } from "@/services/disasterApi"

const ApiStatus: React.FC = () => {
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null)
  const [systemStatus, setSystemStatus] = useState<any>(null)
  const [isChecking, setIsChecking] = useState(false)
  const [lastCheck, setLastCheck] = useState<Date | null>(null)

  const checkStatus = async () => {
    setIsChecking(true)
    try {
      const [health, status] = await Promise.all([checkApiHealth(), fetchSystemStatus()])

      setIsHealthy(health)
      setSystemStatus(status)
      setLastCheck(new Date())
    } catch (error) {
      console.error("Status check failed:", error)
      setIsHealthy(false)
      setSystemStatus(null)
    } finally {
      setIsChecking(false)
    }
  }

  useEffect(() => {
    checkStatus()

    // Check status every 30 seconds
    const interval = setInterval(checkStatus, 30000)

    return () => clearInterval(interval)
  }, [])

  const getStatusIcon = () => {
    if (isChecking) {
      return <RefreshCw className="h-4 w-4 animate-spin" />
    }

    if (isHealthy === null) {
      return <AlertCircle className="h-4 w-4 text-yellow-500" />
    }

    return isHealthy ? <CheckCircle className="h-4 w-4 text-green-500" /> : <XCircle className="h-4 w-4 text-red-500" />
  }

  const getStatusText = () => {
    if (isChecking) return "Checking..."
    if (isHealthy === null) return "Unknown"
    return isHealthy ? "Connected" : "Disconnected"
  }

  const getStatusVariant = () => {
    if (isChecking || isHealthy === null) return "secondary"
    return isHealthy ? "default" : "destructive"
  }

  return (
    <div className="flex items-center gap-2 text-sm">
      <div className="flex items-center gap-1">
        {getStatusIcon()}
        <span className="font-medium">API Status:</span>
      </div>

      <Badge variant={getStatusVariant()}>{getStatusText()}</Badge>

      {systemStatus && (
        <div className="hidden md:flex items-center gap-2 text-xs text-gray-600">
          <span>•</span>
          <span>{systemStatus.total_disasters} disasters</span>
          <span>•</span>
          <span>Weather: {systemStatus.weather_available ? "Available" : "Unavailable"}</span>
        </div>
      )}

      {lastCheck && <div className="text-xs text-gray-500">Last check: {lastCheck.toLocaleTimeString()}</div>}

      <Button onClick={checkStatus} disabled={isChecking} size="sm" variant="ghost" className="h-6 w-6 p-0">
        <RefreshCw className={`h-3 w-3 ${isChecking ? "animate-spin" : ""}`} />
      </Button>
    </div>
  )
}

export default ApiStatus
