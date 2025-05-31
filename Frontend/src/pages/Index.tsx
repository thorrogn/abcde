"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { AlertTriangle, MapPin } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import LocationSelector from "@/components/LocationSelector"
import ApiStatus from "@/components/ApiStatus"

interface Location {
  latitude: number
  longitude: number
  address: string
}

const IndexPage: React.FC = () => {
  const [userLocation, setUserLocation] = useState<Location | null>(null)
  const [isLoadingLocation, setIsLoadingLocation] = useState(false)
  const [locationError, setLocationError] = useState<string | null>(null)

  const getCurrentLocation = () => {
    setIsLoadingLocation(true)
    setLocationError(null)

    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords

          // Reverse geocoding to get the address
          fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${latitude}&lon=${longitude}`)
            .then((response) => response.json())
            .then((data) => {
              const address = data.display_name
              setUserLocation({ latitude, longitude, address })
              setIsLoadingLocation(false)
            })
            .catch((error) => {
              console.error("Error fetching address:", error)
              setLocationError("Failed to fetch address. Please try again.")
              setIsLoadingLocation(false)
            })
        },
        (error) => {
          console.error("Error getting location:", error)
          let errorMessage = "Failed to get location. Please try again."
          switch (error.code) {
            case error.PERMISSION_DENIED:
              errorMessage = "Location access denied. Please enable it in your browser settings."
              break
            case error.POSITION_UNAVAILABLE:
              errorMessage = "Location information unavailable. Please try again later."
              break
            case error.TIMEOUT:
              errorMessage = "Location request timed out. Please try again."
              break
          }
          setLocationError(errorMessage)
          setIsLoadingLocation(false)
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 0,
        },
      )
    } else {
      setLocationError("Geolocation is not supported by your browser.")
      setIsLoadingLocation(false)
    }
  }

  useEffect(() => {
    // Attempt to get location on mount (optional)
    // getCurrentLocation();
  }, [])

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-lg border-b-4 border-red-500">
        <div className="container mx-auto px-4 py-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-red-500 rounded-lg">
                <AlertTriangle className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-2xl md:text-3xl font-bold text-gray-900">Disaster Information Hub</h1>
                <p className="text-gray-600">Real-time alerts and emergency information</p>
              </div>
            </div>

            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-4">
                <LocationSelector onLocationSelect={setUserLocation} currentLocation={userLocation} />
                <Button onClick={getCurrentLocation} disabled={isLoadingLocation} variant="outline" size="sm">
                  <MapPin className="h-4 w-4 mr-2" />
                  {isLoadingLocation ? "Detecting..." : "My Location"}
                </Button>
              </div>

              <ApiStatus />
            </div>
          </div>

          {userLocation && (
            <div className="mt-4 p-3 bg-blue-50 rounded-lg">
              <div className="flex items-center gap-2">
                <MapPin className="h-4 w-4 text-blue-600" />
                <span className="text-sm font-medium text-blue-900">Monitoring: {userLocation.address}</span>
                <Badge variant="secondary" className="ml-2">
                  Active
                </Badge>
              </div>
            </div>
          )}
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        {locationError && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
            <strong className="font-bold">Error!</strong>
            <span className="block sm:inline">{locationError}</span>
          </div>
        )}
        {/* Add content here */}
      </main>
    </div>
  )
}

export default IndexPage
