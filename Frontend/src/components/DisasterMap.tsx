"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { GoogleMap, LoadScript, Marker, InfoWindow } from "@react-google-maps/api"
import { fetchAllDisasters, fetchWeatherData, checkApiHealth } from "@/services/disasterApi"

interface Disaster {
  id: string
  type: string
  location: {
    latitude: number
    longitude: number
  }
  description: string
}

interface WeatherData {
  temperature: number
  humidity: number
  description: string
}

const DisasterMap: React.FC = () => {
  const [location, setLocation] = useState({ lat: 40.7128, lng: -74.006 }) // Default to New York
  const [zoom, setZoom] = useState(10)
  const [disasters, setDisasters] = useState<Disaster[]>([])
  const [weatherData, setWeatherData] = useState<WeatherData | null>(null)
  const [selectedDisaster, setSelectedDisaster] = useState<Disaster | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const mapStyles = {
    height: "600px",
    width: "100%",
  }

  useEffect(() => {
    loadData()
  }, [location])

  const loadData = async () => {
    setIsLoading(true)
    try {
      console.log("Loading map data for location:", location)

      // Check API health first
      const isHealthy = await checkApiHealth()
      if (!isHealthy) {
        console.warn("Backend API is not responding, using fallback data")
      }

      // Load disasters and weather data
      const [disasterData, weather] = await Promise.all([
        fetchAllDisasters(),
        fetchWeatherData(location.lat, location.lng),
      ])

      setDisasters(disasterData.slice(0, 10)) // Show top 10 disasters
      setWeatherData(weather)

      console.log("Map data loaded - Disasters:", disasterData.length, "Weather:", weather)
    } catch (error) {
      console.error("Error loading map data:", error)
      // Set empty data on error
      setDisasters([])
      setWeatherData(null)
    } finally {
      setIsLoading(false)
    }
  }

  const onMarkerClick = (disaster: Disaster) => {
    setSelectedDisaster(disaster)
  }

  return (
    <div>
      {isLoading ? (
        <div>Loading...</div>
      ) : (
        <LoadScript googleMapsApiKey={process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY || ""}>
          <GoogleMap mapContainerStyle={mapStyles} zoom={zoom} center={location}>
            {disasters.map((disaster) => (
              <Marker
                key={disaster.id}
                position={{ lat: disaster.location.latitude, lng: disaster.location.longitude }}
                onClick={() => onMarkerClick(disaster)}
              />
            ))}
            {selectedDisaster && (
              <InfoWindow
                position={{ lat: selectedDisaster.location.latitude, lng: selectedDisaster.location.longitude }}
                onCloseClick={() => setSelectedDisaster(null)}
              >
                <div>
                  <h3>{selectedDisaster.type}</h3>
                  <p>{selectedDisaster.description}</p>
                </div>
              </InfoWindow>
            )}
          </GoogleMap>
        </LoadScript>
      )}
      {weatherData && (
        <div>
          <p>Temperature: {weatherData.temperature}°C</p>
          <p>Humidity: {weatherData.humidity}%</p>
          <p>Weather: {weatherData.description}</p>
        </div>
      )}
    </div>
  )
}

export default DisasterMap
