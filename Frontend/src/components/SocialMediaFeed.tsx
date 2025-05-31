"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { fetchSocialMediaData } from "@/services/disasterApi"

interface Post {
  id: string
  text: string
  imageUrl?: string
  source: string
  timestamp: string
}

interface SocialMediaFeedProps {
  location: string
}

const SocialMediaFeed: React.FC<SocialMediaFeedProps> = ({ location }) => {
  const [posts, setPosts] = useState<Post[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  useEffect(() => {
    const loadSocialMedia = async () => {
      setIsLoading(true)
      try {
        const socialData = await fetchSocialMediaData(location)
        setPosts(socialData)
        setLastUpdated(new Date())
      } catch (error) {
        console.error("Failed to load social media data:", error)
        setPosts([])
      } finally {
        setIsLoading(false)
      }
    }

    loadSocialMedia()

    // Refresh social media every 5 minutes
    const interval = setInterval(loadSocialMedia, 5 * 60 * 1000)

    return () => clearInterval(interval)
  }, [location])

  return (
    <div>
      <h2>Social Media Feed - {location}</h2>
      {isLoading ? (
        <p>Loading social media posts...</p>
      ) : (
        <>
          {lastUpdated && <p>Last updated: {lastUpdated.toLocaleTimeString()}</p>}
          {posts.length > 0 ? (
            <ul>
              {posts.map((post) => (
                <li key={post.id}>
                  <p>{post.text}</p>
                  {post.imageUrl && (
                    <img
                      src={post.imageUrl || "/placeholder.svg"}
                      alt="Social media post"
                      style={{ maxWidth: "200px" }}
                    />
                  )}
                  <p>Source: {post.source}</p>
                  <p>Timestamp: {post.timestamp}</p>
                </li>
              ))}
            </ul>
          ) : (
            <p>No social media posts found for this location.</p>
          )}
        </>
      )}
    </div>
  )
}

export default SocialMediaFeed
