// Backend API base URL - adjust this based on your deployment
const API_BASE_URL = "http://localhost:5000/api"

export interface DisasterEvent {
  id: string
  type: string
  severity: string
  title: string
  description: string
  location: string
  coordinates?: { lat: number; lng: number }
  timestamp: string
  source: string
  url?: string
}

export interface WeatherData {
  temperature: number
  humidity: number
  windSpeed: number
  conditions: string
  pressure?: number
  visibility?: number
}

export interface ApiResponse<T> {
  success: boolean
  data: T
  count?: number
  last_updated?: string
  error?: string
}

// Generic API request function with error handling\
const apiRequest = async <T>(endpoint: string, options?: RequestInit)
: Promise<T> =>
{
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
      ...options,
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()

    if (!data.success) {
      throw new Error(data.error || "API request failed")
    }

    return data.data;
  } catch (error) {
    console.error(`API request failed for ${endpoint}:`, error)
    throw error
  }
}

// Health check
export const checkApiHealth = async (): Promise<boolean> => {
  try {
    const response = await fetch(`${API_BASE_URL}/health`)
    return response.ok
  } catch (error) {
    console.error("Health check failed:", error)
    return false
  }
}

// Fetch GDACS disasters
export const fetchGDACSDisasters = async (): Promise<DisasterEvent[]> => {
  try {
    console.log("Fetching GDACS disasters from backend...")
    const data = await apiRequest<DisasterEvent[]>("/gdacs")
    console.log("GDACS disasters fetched:", data.length)
    return data
  } catch (error) {
    console.error("Failed to fetch GDACS disasters:", error)
    return []
  }
}

// Fetch ReliefWeb disasters
export const fetchReliefWebDisasters = async (): Promise<DisasterEvent[]> => {
  try {
    console.log("Fetching ReliefWeb disasters from backend...")
    const data = await apiRequest<DisasterEvent[]>("/reliefweb")
    console.log("ReliefWeb disasters fetched:", data.length)
    return data
  } catch (error) {
    console.error("Failed to fetch ReliefWeb disasters:", error)
    return []
  }
}

// Fetch all disasters (combined from all sources)
export const fetchAllDisasters = async (): Promise<DisasterEvent[]> => {
  try {
    console.log("Fetching all disasters from backend...")
    const data = await apiRequest<DisasterEvent[]>("/disasters")
    console.log("All disasters fetched:", data.length)
    return data
  } catch (error) {
    console.error("Failed to fetch all disasters:", error)

    // Fallback: try to fetch from individual sources
    try {
      const [gdacs, reliefweb] = await Promise.all([fetchGDACSDisasters(), fetchReliefWebDisasters()])

      const combined = [...gdacs, ...reliefweb]
      console.log("Fallback: Combined disasters from individual sources:", combined.length)
      return combined
    } catch (fallbackError) {
      console.error("Fallback also failed:", fallbackError)
      return []
    }
  }
}

// Fetch weather data
export const fetchWeatherData = async (lat?: number, lng?: number): Promise<WeatherData | null> => {
  try {
    const params = new URLSearchParams()
    if (lat !== undefined && lng !== undefined) {
      params.append("lat", lat.toString())
      params.append("lng", lng.toString())
    }

    const endpoint = `/weather${params.toString() ? `?${params.toString()}` : ""}`
    console.log(`Fetching weather data from backend: ${endpoint}`)

    const data = await apiRequest<WeatherData>(endpoint)
    console.log("Weather data fetched:", data)
    return data
  } catch (error) {
    console.error("Failed to fetch weather data:", error)
    return null
  }
}

// Fetch system status
export const fetchSystemStatus = async () => {
  try {
    console.log("Fetching system status...")
    const data = await apiRequest<any>("/status")
    console.log("System status:", data)
    return data
  } catch (error) {
    console.error("Failed to fetch system status:", error)
    return null
  }
}

// Mock news data (since we don't have a real news API integrated)
export const fetchNewsData = async (location: { lat: number; lng: number; address: string }) => {
  // Simulate API delay
  await new Promise((resolve) => setTimeout(resolve, 1000))

  return [
    {
      id: "news-1",
      title: "Emergency Response Teams Deployed to Flood-Affected Areas",
      summary: "Local authorities have mobilized emergency response teams following recent flooding in the region.",
      url: "#",
      source: "Emergency News",
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
      location: location.address,
    },
    {
      id: "news-2",
      title: "Weather Alert: Heavy Rainfall Expected",
      summary: "Meteorological department issues warning for heavy rainfall in the next 24 hours.",
      url: "#",
      source: "Weather Service",
      timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(), // 4 hours ago
      location: location.address,
    },
    {
      id: "news-3",
      title: "Disaster Preparedness Workshop Scheduled",
      summary: "Community disaster preparedness workshop to be held this weekend.",
      url: "#",
      source: "Community News",
      timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(), // 6 hours ago
      location: location.address,
    },
  ]
}

// Mock social media data
export const fetchSocialMediaData = async (location: { lat: number; lng: number; address: string }) => {
  // Simulate API delay
  await new Promise((resolve) => setTimeout(resolve, 800))

  return [
    {
      id: "social-1",
      platform: "Twitter",
      username: "@EmergencyAlert",
      content: `🚨 ALERT: Monitoring weather conditions in ${location.address}. Stay safe and follow official guidelines.`,
      timestamp: new Date(Date.now() - 30 * 60 * 1000).toISOString(), // 30 minutes ago
      verified: true,
      engagement: { likes: 45, shares: 23, comments: 12 },
    },
    {
      id: "social-2",
      platform: "Facebook",
      username: "Local Emergency Services",
      content:
        "Emergency shelters are available for those affected by recent weather conditions. Contact us for assistance.",
      timestamp: new Date(Date.now() - 1 * 60 * 60 * 1000).toISOString(), // 1 hour ago
      verified: true,
      engagement: { likes: 78, shares: 34, comments: 19 },
    },
    {
      id: "social-3",
      platform: "Twitter",
      username: "@WeatherUpdate",
      content: "Current conditions show improvement, but residents should remain cautious. Updates every hour.",
      timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
      verified: false,
      engagement: { likes: 23, shares: 8, comments: 5 },
    },
  ]
}

// Export API configuration for debugging
export const getApiConfig = () => ({
  baseUrl: API_BASE_URL,
  endpoints: {
    health: "/health",
    gdacs: "/gdacs",
    reliefweb: "/reliefweb",
    disasters: "/disasters",
    weather: "/weather",
    status: "/status",
  },
})
