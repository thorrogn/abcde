"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { fetchAllDisasters, checkApiHealth } from "@/services/disasterApi"

const AlertsFeed: React.FC = () => {
  const [alerts, setAlerts] = useState([])
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isConnected, setIsConnected] = useState(true)
  const [retryCount, setRetryCount] = useState(0)
  const MAX_RETRIES = 3

  useEffect(() => {
    loadDisasters()

    const intervalId = setInterval(() => {
      loadDisasters()
    }, 60000) // Refresh every minute

    return () => clearInterval(intervalId)
  }, [])

  const loadDisasters = async () => {
    setIsLoading(true)
    try {
      // Check API health first
      const isHealthy = await checkApiHealth()
      setIsConnected(isHealthy)
      if (!isHealthy) {
        throw new Error("Backend API is not responding")
      }

      const disasters = await fetchAllDisasters()
      setAlerts(disasters)
      setLastUpdated(new Date())
      console.log("Loaded disasters:", disasters.length)
      setRetryCount(0) // Reset retry count on success
    } catch (error) {
      console.error("Failed to load disasters:", error)
      setIsConnected(false)
      // Retry mechanism
      if (retryCount < MAX_RETRIES) {
        console.log(`Retrying in ${retryCount + 1 * 5} seconds...`)
        setTimeout(
          () => {
            setRetryCount(retryCount + 1)
            loadDisasters()
          },
          (retryCount + 1) * 5000,
        ) // Exponential backoff
      } else {
        console.error("Max retries reached. Giving up.")
        // Optionally display a persistent error message to the user
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div>
      <h2>Alerts Feed</h2>
      {!isConnected && (
        <div style={{ color: "red" }}>
          <p>
            Not Connected to Backend API. Retrying... ({retryCount}/{MAX_RETRIES})
          </p>
        </div>
      )}
      {isLoading ? (
        <p>Loading alerts...</p>
      ) : (
        <>
          {alerts.length > 0 ? (
            <ul>
              {alerts.map((alert: any) => (
                <li key={alert.id}>
                  <strong>{alert.title}</strong> - {alert.description}
                </li>
              ))}
            </ul>
          ) : (
            <p>No alerts to display.</p>
          )}
          {lastUpdated && <p>Last updated: {lastUpdated.toLocaleTimeString()}</p>}
        </>
      )}
    </div>
  )
}

export default AlertsFeed
