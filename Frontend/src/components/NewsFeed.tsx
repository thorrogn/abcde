"use client"

import type React from "react"
import { useState, useEffect } from "react"
import { fetchNewsData } from "@/services/disasterApi"

interface NewsItem {
  title: string
  description: string
  url: string
  urlToImage: string
  publishedAt: string
  source: {
    name: string
  }
}

interface NewsFeedProps {
  location: string
}

const NewsFeed: React.FC<NewsFeedProps> = ({ location }) => {
  const [news, setNews] = useState<NewsItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  useEffect(() => {
    const loadNews = async () => {
      setIsLoading(true)
      try {
        const newsData = await fetchNewsData(location)
        setNews(newsData)
        setLastUpdated(new Date())
      } catch (error) {
        console.error("Failed to load news:", error)
        setNews([])
      } finally {
        setIsLoading(false)
      }
    }

    loadNews()

    // Refresh news every 10 minutes
    const interval = setInterval(loadNews, 10 * 60 * 1000)

    return () => clearInterval(interval)
  }, [location])

  return (
    <div>
      <h2>News Feed</h2>
      {lastUpdated && <p>Last updated: {lastUpdated.toLocaleTimeString()}</p>}
      {isLoading ? (
        <p>Loading news...</p>
      ) : news.length > 0 ? (
        <ul>
          {news.map((item, index) => (
            <li key={index}>
              <h3>
                <a href={item.url} target="_blank" rel="noopener noreferrer">
                  {item.title}
                </a>
              </h3>
              <p>{item.description}</p>
              {item.urlToImage && (
                <img src={item.urlToImage || "/placeholder.svg"} alt={item.title} style={{ maxWidth: "200px" }} />
              )}
              <p>Source: {item.source.name}</p>
              <p>Published: {new Date(item.publishedAt).toLocaleDateString()}</p>
            </li>
          ))}
        </ul>
      ) : (
        <p>No news available for this location.</p>
      )}
    </div>
  )
}

export default NewsFeed
