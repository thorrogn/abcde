import React from 'react';
import { Phone, MapPin, Clock, AlertTriangle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface EmergencyContactsProps {
  location: { lat: number; lng: number; address: string };
}

const EmergencyContacts: React.FC<EmergencyContactsProps> = ({ location }) => {
  // Get location-specific emergency services based on address
  const getLocationSpecificServices = (address: string) => {
    const city = address.toLowerCase();
    
    // State-specific emergency numbers
    const stateServices: { [key: string]: any } = {
      'mumbai': {
        state: 'Maharashtra',
        police: '100',
        fire: '101',
        ambulance: '102/108',
        disaster: '022-22694725',
        control: 'Mumbai Disaster Management - 022-22001111'
      },
      'delhi': {
        state: 'Delhi',
        police: '100',
        fire: '101',
        ambulance: '102/108',
        disaster: '011-23438252',
        control: 'Delhi Disaster Management - 011-23438252'
      },
      'bangalore': {
        state: 'Karnataka',
        police: '100',
        fire: '101',
        ambulance: '102/108',
        disaster: '080-22212020',
        control: 'BBMP Emergency - 080-22660000'
      },
      'chennai': {
        state: 'Tamil Nadu',
        police: '100',
        fire: '101',
        ambulance: '102/108',
        disaster: '044-25619999',
        control: 'Greater Chennai Corporation - 044-25619999'
      },
      'kolkata': {
        state: 'West Bengal',
        police: '100',
        fire: '101',
        ambulance: '102/108',
        disaster: '033-22143526',
        control: 'Kolkata Municipal Corporation - 033-22861111'
      },
      'hyderabad': {
        state: 'Telangana',
        police: '100',
        fire: '101',
        ambulance: '102/108',
        disaster: '040-23450733',
        control: 'GHMC Emergency - 040-23450050'
      },
      'pune': {
        state: 'Maharashtra',
        police: '100',
        fire: '101',
        ambulance: '102/108',
        disaster: '020-26127394',
        control: 'PMC Emergency - 020-26123456'
      },
      'ahmedabad': {
        state: 'Gujarat',
        police: '100',
        fire: '101',
        ambulance: '102/108',
        disaster: '079-26851111',
        control: 'AMC Emergency - 079-26851111'
      }
    };

    // Find matching city
    for (const [cityKey, services] of Object.entries(stateServices)) {
      if (city.includes(cityKey)) {
        return services;
      }
    }

    // Default services for other locations
    return {
      state: 'India',
      police: '100',
      fire: '101',
      ambulance: '102/108',
      disaster: '1078',
      control: 'National Emergency Response - 112'
    };
  };

  const locationServices = getLocationSpecificServices(location.address);

  const emergencyServices = [
    {
      name: 'Emergency Services (All)',
      number: '112',
      description: 'Single emergency number for all services',
      available: '24/7',
      priority: 'Critical'
    },
    {
      name: 'Police',
      number: locationServices.police,
      description: 'Local police emergency',
      available: '24/7',
      priority: 'Critical'
    },
    {
      name: 'Fire Brigade',
      number: locationServices.fire,
      description: 'Fire emergency services',
      available: '24/7',
      priority: 'Critical'
    },
    {
      name: 'Ambulance',
      number: locationServices.ambulance,
      description: 'Medical emergency services',
      available: '24/7',
      priority: 'Critical'
    },
    {
      name: 'Disaster Management',
      number: locationServices.disaster,
      description: `${locationServices.state} disaster control room`,
      available: '24/7',
      priority: 'High'
    },
    {
      name: 'Local Control Room',
      number: locationServices.control.split(' - ')[1] || locationServices.disaster,
      description: locationServices.control.split(' - ')[0],
      available: '24/7',
      priority: 'High'
    }
  ];

  // Get location-specific shelters
  const getLocationShelters = (address: string) => {
    const city = address.toLowerCase();
    
    const cityShelters: { [key: string]: any[] } = {
      'mumbai': [
        {
          name: 'Shivaji Park Grounds',
          address: 'Shivaji Park, Dadar, Mumbai',
          distance: '2.1 km',
          capacity: 'High (5000+)',
          status: 'Open',
          type: 'Primary Shelter'
        },
        {
          name: 'BKC Ground',
          address: 'Bandra Kurla Complex, Mumbai',
          distance: '4.5 km',
          capacity: 'High (3000+)',
          status: 'Open',
          type: 'Emergency Shelter'
        },
        {
          name: 'Oval Maidan',
          address: 'Fort, Mumbai',
          distance: '6.2 km',
          capacity: 'Medium (2000+)',
          status: 'Standby',
          type: 'Secondary Shelter'
        }
      ],
      'delhi': [
        {
          name: 'Ramlila Maidan',
          address: 'Near Red Fort, Delhi',
          distance: '3.2 km',
          capacity: 'High (10000+)',
          status: 'Open',
          type: 'Primary Shelter'
        },
        {
          name: 'Jawaharlal Nehru Stadium',
          address: 'Lodhi Road, New Delhi',
          distance: '5.8 km',
          capacity: 'High (8000+)',
          status: 'Open',
          type: 'Emergency Shelter'
        },
        {
          name: 'Talkatora Stadium',
          address: 'President Estate, Delhi',
          distance: '4.1 km',
          capacity: 'Medium (3000+)',
          status: 'Standby',
          type: 'Secondary Shelter'
        }
      ],
      'bangalore': [
        {
          name: 'Kanteerava Stadium',
          address: 'Kasturba Road, Bangalore',
          distance: '2.8 km',
          capacity: 'High (4000+)',
          status: 'Open',
          type: 'Primary Shelter'
        },
        {
          name: 'Palace Grounds',
          address: 'Jayamahal Road, Bangalore',
          distance: '5.3 km',
          capacity: 'High (6000+)',
          status: 'Open',
          type: 'Emergency Shelter'
        },
        {
          name: 'Cubbon Park',
          address: 'Kasturba Road, Bangalore',
          distance: '3.7 km',
          capacity: 'Medium (2500+)',
          status: 'Standby',
          type: 'Secondary Shelter'
        }
      ]
    };

    // Find matching city shelters
    for (const [cityKey, shelters] of Object.entries(cityShelters)) {
      if (city.includes(cityKey)) {
        return shelters;
      }
    }

    // Default shelters for other locations
    return [
      {
        name: 'Local Community Center',
        address: `Near ${location.address}`,
        distance: '2.5 km',
        capacity: 'Medium (1500+)',
        status: 'Open',
        type: 'Primary Shelter'
      },
      {
        name: 'District Stadium',
        address: `District Center, ${location.address}`,
        distance: '4.2 km',
        capacity: 'High (3000+)',
        status: 'Standby',
        type: 'Emergency Shelter'
      },
      {
        name: 'Government School',
        address: `Local Area, ${location.address}`,
        distance: '1.8 km',
        capacity: 'Low (500+)',
        status: 'Open',
        type: 'Secondary Shelter'
      }
    ];
  };

  const shelters = getLocationShelters(location.address);

  // Location-specific safety tips
  const getLocationSafetyTips = (address: string) => {
    const city = address.toLowerCase();
    
    if (city.includes('mumbai') || city.includes('coastal')) {
      return [
        "Monitor monsoon and cyclone warnings during June-September",
        "Keep emergency kit with waterproof items during monsoon season",
        "Know flood-prone areas and alternate routes",
        "Stay updated with BMC flood alerts and traffic updates",
        "Keep important documents in waterproof containers"
      ];
    } else if (city.includes('delhi')) {
      return [
        "Monitor air quality index during winter months",
        "Prepare for extreme temperature variations",
        "Keep masks ready for dust storms and pollution",
        "Stay hydrated during summer heat waves",
        "Know nearest metro stations for emergency transport"
      ];
    } else {
      return [
        "Stay informed through local emergency broadcast systems",
        "Keep emergency contact numbers saved offline",
        "Maintain emergency supplies: water, food, flashlight, radio",
        "Know your evacuation routes and assembly points",
        "Register with local disaster management authorities"
      ];
    }
  };

  const safetyTips = getLocationSafetyTips(location.address);

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'Critical': return 'destructive';
      case 'High': return 'default';
      case 'Medium': return 'secondary';
      default: return 'outline';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Open': return 'bg-green-100 text-green-800';
      case 'Standby': return 'bg-yellow-100 text-yellow-800';
      case 'Full': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Location Info */}
      <div className="p-3 bg-blue-50 rounded-lg">
        <div className="flex items-center gap-2">
          <MapPin className="h-4 w-4 text-blue-600" />
          <span className="text-sm font-medium text-blue-900">
            Emergency Services for: {location.address}
          </span>
          <Badge variant="secondary" className="ml-2 text-xs">
            {locationServices.state}
          </Badge>
        </div>
      </div>

      {/* Emergency Numbers */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-red-600">
            <Phone className="h-5 w-5" />
            Emergency Contacts
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {emergencyServices.map((service, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="font-semibold text-sm">{service.name}</span>
                  <Badge variant={getPriorityColor(service.priority)} className="text-xs">
                    {service.priority}
                  </Badge>
                </div>
                <p className="text-xs text-gray-600 mb-1">{service.description}</p>
                <div className="flex items-center gap-1 text-xs text-gray-500">
                  <Clock className="h-3 w-3" />
                  {service.available}
                </div>
              </div>
              <Button 
                size="sm" 
                className="ml-3"
                onClick={() => window.open(`tel:${service.number}`)}
              >
                <Phone className="h-4 w-4 mr-1" />
                {service.number}
              </Button>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Emergency Shelters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-blue-600">
            <MapPin className="h-5 w-5" />
            Nearby Emergency Shelters
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {shelters.map((shelter, index) => (
            <div key={index} className="p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="font-semibold text-sm">{shelter.name}</span>
                <div className="flex gap-2">
                  <Badge className={`text-xs ${getStatusColor(shelter.status)}`}>
                    {shelter.status}
                  </Badge>
                  <Badge variant="outline" className="text-xs">
                    {shelter.type}
                  </Badge>
                </div>
              </div>
              <p className="text-xs text-gray-600 mb-1">{shelter.address}</p>
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>{shelter.distance} away</span>
                <span>Capacity: {shelter.capacity}</span>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Safety Tips */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-orange-600">
            <AlertTriangle className="h-5 w-5" />
            Location-Specific Safety Tips
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2">
            {safetyTips.map((tip, index) => (
              <li key={index} className="flex items-start gap-2 text-sm">
                <span className="text-orange-600 font-bold">•</span>
                <span className="text-gray-700">{tip}</span>
              </li>
            ))}
          </ul>
        </CardContent>
      </Card>
    </div>
  );
};

export default EmergencyContacts;
