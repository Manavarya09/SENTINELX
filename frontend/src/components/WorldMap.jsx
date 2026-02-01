import { useQuery } from '@tanstack/react-query'
import axios from 'axios'
import { MapPin, Globe } from 'lucide-react'

function WorldMap() {
  const { data: geoData, isLoading } = useQuery({
    queryKey: ['attack-geography'],
    queryFn: async () => {
      const response = await axios.get('/api/dashboard/geo/attacks')
      return response.data
    },
    refetchInterval: 300000, // Refresh every 5 minutes
  })

  if (isLoading) {
    return (
      <div className="card">
        <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center">
          <Globe className="h-5 w-5 mr-2" />
          Attack Geography
        </h3>
        <div className="h-64 flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center">
        <Globe className="h-5 w-5 mr-2" />
        Attack Origins
      </h3>
      <div className="h-64 bg-surface/50 rounded-md flex items-center justify-center">
        <div className="text-center">
          <MapPin className="h-12 w-12 text-muted mx-auto mb-4" />
          <p className="text-muted">Interactive world map</p>
          <p className="text-sm text-muted mt-2">
            {geoData?.locations?.length || 0} countries with attack activity
          </p>
        </div>
      </div>
      {geoData?.locations && (
        <div className="mt-4 space-y-2">
          {geoData.locations.slice(0, 5).map((location, index) => (
            <div key={index} className="flex items-center justify-between text-sm">
              <span className="text-foreground">{location.country}</span>
              <span className="text-primary font-medium">{location.attacks} attacks</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default WorldMap