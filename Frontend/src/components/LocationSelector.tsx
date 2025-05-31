import React, { useState, useRef, useEffect } from 'react';
import { Search, MapPin, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';

interface LocationSelectorProps {
  onLocationSelect: (location: { lat: number; lng: number; address: string }) => void;
  currentLocation: { lat: number; lng: number; address: string } | null;
}

const LocationSelector: React.FC<LocationSelectorProps> = ({ 
  onLocationSelect, 
  currentLocation 
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Indian cities and disaster-prone locations
  const indianLocations = [
    { name: 'Mumbai, Maharashtra', lat: 19.0760, lng: 72.8777 },
    { name: 'Delhi, Delhi', lat: 28.7041, lng: 77.1025 },
    { name: 'Bangalore, Karnataka', lat: 12.9716, lng: 77.5946 },
    { name: 'Chennai, Tamil Nadu', lat: 13.0827, lng: 80.2707 },
    { name: 'Kolkata, West Bengal', lat: 22.5726, lng: 88.3639 },
    { name: 'Hyderabad, Telangana', lat: 17.3850, lng: 78.4867 },
    { name: 'Pune, Maharashtra', lat: 18.5204, lng: 73.8567 },
    { name: 'Ahmedabad, Gujarat', lat: 23.0225, lng: 72.5714 },
    { name: 'Surat, Gujarat', lat: 21.1702, lng: 72.8311 },
    { name: 'Jaipur, Rajasthan', lat: 26.9124, lng: 75.7873 },
    { name: 'Kochi, Kerala', lat: 9.9312, lng: 76.2673 },
    { name: 'Bhubaneswar, Odisha', lat: 20.2961, lng: 85.8245 },
    { name: 'Guwahati, Assam', lat: 26.1445, lng: 91.7362 },
    { name: 'Shimla, Himachal Pradesh', lat: 31.1048, lng: 77.1734 },
    { name: 'Gangtok, Sikkim', lat: 27.3389, lng: 88.6065 },
  ];

  // Filter locations based on search query
  const filteredLocations = indianLocations.filter(location =>
    location.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Handle clicks outside dropdown to close it
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    setIsSearching(true);
    // Simulate geocoding for Indian locations
    setTimeout(() => {
      // Try to find exact match first
      const exactMatch = indianLocations.find(loc => 
        loc.name.toLowerCase().includes(searchQuery.toLowerCase())
      );
      
      if (exactMatch) {
        onLocationSelect({
          lat: exactMatch.lat,
          lng: exactMatch.lng,
          address: exactMatch.name
        });
      } else {
        // Default to a location in India if no match found
        onLocationSelect({
          lat: 20.5937,
          lng: 78.9629,
          address: searchQuery + ', India'
        });
      }
      
      setSearchQuery('');
      setShowDropdown(false);
      setIsSearching(false);
    }, 1000);
  };

  const selectQuickLocation = (location: any) => {
    onLocationSelect({
      lat: location.lat,
      lng: location.lng,
      address: location.name
    });
    setShowDropdown(false);
    setSearchQuery('');
  };

  const handleInputFocus = () => {
    setShowDropdown(true);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
    setShowDropdown(true);
  };

  const clearSearch = () => {
    setSearchQuery('');
    setShowDropdown(false);
    inputRef.current?.blur();
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <div className="flex gap-2">
        <div className="relative flex-1">
          <Input
            ref={inputRef}
            type="text"
            placeholder="Search Indian cities..."
            value={searchQuery}
            onChange={handleInputChange}
            onFocus={handleInputFocus}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            className="pr-16"
          />
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2 flex items-center gap-1">
            {searchQuery && (
              <button
                onClick={clearSearch}
                className="h-4 w-4 text-gray-400 hover:text-gray-600"
              >
                <X className="h-4 w-4" />
              </button>
            )}
            <Search className="h-4 w-4 text-gray-400" />
          </div>
        </div>
        <Button 
          onClick={handleSearch}
          disabled={isSearching || !searchQuery.trim()}
          size="sm"
        >
          {isSearching ? 'Searching...' : 'Search'}
        </Button>
      </div>

      {/* Dropdown */}
      {showDropdown && (
        <Card className="absolute top-full left-0 right-0 mt-2 z-50 bg-white shadow-lg border max-h-80 overflow-y-auto">
          <CardContent className="p-2">
            <div className="text-xs text-gray-500 mb-2 px-2 font-medium">
              {searchQuery ? 'Search Results:' : 'Popular Indian Cities:'}
            </div>
            <div className="space-y-1">
              {(searchQuery ? filteredLocations : indianLocations.slice(0, 8)).map((location, index) => (
                <button
                  key={index}
                  onClick={() => selectQuickLocation(location)}
                  className="w-full text-left px-2 py-2 text-sm hover:bg-gray-100 rounded flex items-center gap-2 transition-colors"
                >
                  <MapPin className="h-3 w-3 text-blue-500 flex-shrink-0" />
                  <span className="truncate">{location.name}</span>
                </button>
              ))}
              {searchQuery && filteredLocations.length === 0 && (
                <div className="px-2 py-2 text-sm text-gray-500">
                  No Indian cities found. Press Enter to search anyway.
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default LocationSelector;
