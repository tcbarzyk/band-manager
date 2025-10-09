import { getCurrentSession } from "./supabase";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
    console.log("🔍 ApiClient initialized with baseUrl:", this.baseUrl);
    console.log("🔍 Environment variable NEXT_PUBLIC_API_URL:", process.env.NEXT_PUBLIC_API_URL);
    console.log("🔍 Default API_BASE_URL:", API_BASE_URL);
  }

  private async getAuthHeaders(): Promise<Record<string, string>> {
    console.log("🔍 Getting auth headers...");
    try {
      const session = await getCurrentSession();
      console.log("🔍 Session:", session ? "exists" : "null");
      console.log("🔍 Access token:", session?.access_token ? "exists" : "missing");
      
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
      };

      if (session?.access_token) {
        headers.Authorization = `Bearer ${session.access_token}`;
      }

      console.log("🔍 Final headers:", headers);
      return headers;
    } catch (error) {
      console.error("🔍 Error getting auth headers:", error);
      return {
        "Content-Type": "application/json",
      };
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
  ): Promise<{ data: T | null; error: string | null }> {
    try {
      console.log("🔍 Making request to:", `${this.baseUrl}${endpoint}`);
      console.log("🔍 API_BASE_URL:", this.baseUrl);
      console.log("🔍 Environment variable:", process.env.NEXT_PUBLIC_API_URL);
      
      const headers = await this.getAuthHeaders();
      console.log("🔍 Headers:", headers);

      console.log("🔍 About to fetch...");
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        ...options,
        headers: {
          ...headers,
          ...options.headers,
        },
      });
      console.log("🔍 Fetch completed, response:", response);
      console.log("🔍 Response status:", response.status);
      console.log("🔍 Response ok:", response.ok);
      console.log("🔍 Response headers:", Object.fromEntries(response.headers.entries()));

      if (!response.ok) {
        console.log("🔍 Response not ok:", response.status, response.statusText);
        const errorData = await response.json().catch(() => ({}));
        const errorMessage =
          errorData.detail || `HTTP ${response.status}: ${response.statusText}`;
        return { data: null, error: errorMessage };
      }

      console.log("🔍 About to parse JSON...");
      let data;
      try {
        const responseText = await response.text();
        console.log("🔍 Response text:", responseText);
        
        if (!responseText) {
          console.log("🔍 Empty response body");
          return { data: null, error: null };
        }
        
        data = JSON.parse(responseText);
        console.log("🔍 Parsed JSON data:", data);
      } catch (parseError) {
        console.error("🔍 JSON parse error:", parseError);
        console.error("🔍 Failed to parse response as JSON");
        return { data: null, error: "Invalid JSON response from server" };
      }

      return { data, error: null };
    } catch (error) {
      console.error("🔍 API request failed:", error);
      console.error("🔍 Error stack:", error instanceof Error ? error.stack : 'No stack');
      return {
        data: null,
        error:
          error instanceof Error ? error.message : "Network error occurred",
      };
    }
  }

  // Health check
  async health() {
    return this.request("/health");
  }

  // Profile endpoints
  async getCurrentProfile() {
    return this.request("/auth/me");
  }

  async updateCurrentProfile(profileData: { display_name: string }) {
    return this.request("/auth/me", {
      method: "PUT",
      body: JSON.stringify(profileData),
    });
  }

  async createProfile(profileData: { display_name: string; email: string }) {
    return this.request("/profiles", {
      method: "POST",
      body: JSON.stringify(profileData),
    });
  }

  // Band endpoints
  async getMyBands() {
    return this.request("/my/bands");
  }

  async createBand(data: CreateBandData) {
    return this.request("/bands", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async joinBand(joinCode: string) {
    return this.request(`/bands/join/${joinCode}`, {
      method: "POST",
    });
  }

  async getBand(bandId: string) {
    return this.request(`/bands/${bandId}`);
  }

  async getBandMembers(bandId: string) {
    return this.request(`/bands/${bandId}/members`);
  }

  // Venue endpoints
  async getBandVenues(bandId: string) {
    return this.request(`/bands/${bandId}/venues`);
  }

  async createVenue(bandId: string, data: CreateVenueData) {
    return this.request(`/bands/${bandId}/venues`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getVenue(venueId: string) {
    return this.request(`/venues/${venueId}`);
  }

  async updateVenue(venueId: string, data: CreateVenueData) {
    return this.request(`/venues/${venueId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async deleteVenue(venueId: string) {
    return this.request(`/venues/${venueId}`, {
      method: "DELETE",
    });
  }

  // Event endpoints
  async getBandEvents(bandId: string) {
    return this.request(`/bands/${bandId}/events`);
  }

  async createEvent(bandId: string, data: CreateEventData) {
    return this.request(`/bands/${bandId}/events`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getEvent(eventId: string) {
    return this.request(`/events/${eventId}`);
  }

  async updateEvent(eventId: string, data: UpdateEventData) {
    return this.request(`/events/${eventId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async deleteEvent(eventId: string) {
    return this.request(`/events/${eventId}`, {
      method: "DELETE",
    });
  }
}

// Export a singleton instance
export const apiClient = new ApiClient();

// Export types for TypeScript
export type ApiResponse<T> = {
  data: T | null;
  error: string | null;
};

export type Profile = {
  user_id: string;
  email: string;
  display_name: string;
  created_at: string;
  updated_at: string;
};

export type Band = {
  id: string;
  name: string;
  description: string | null;
  timezone: string;
  join_code: string;
  created_by: string;
  created_at: string;
};

export type CreateBandData = {
  name: string;
  description?: string;
  timezone: string;
};

export type Venue = {
  id: string;
  band_id: string;
  name: string;
  address: string | null;
  notes: string | null;
};

export type CreateVenueData = {
  name: string;
  address?: string;
  notes?: string;
};

export type Event = {
  id: string;
  band_id: string;
  type: "rehearsal" | "gig";
  status: "planned" | "confirmed" | "cancelled";
  title: string;
  starts_at_utc: string;
  ends_at_utc: string;
  venue_id: string | null;
  notes: string | null;
  created_by: string;
  created_at: string;
};

export type CreateEventData = {
  title: string;
  type: "rehearsal" | "gig";
  starts_at_utc: string;
  ends_at_utc: string;
  venue_id?: string;
  notes?: string;
};

export type UpdateEventData = {
  title?: string;
  type?: "rehearsal" | "gig";
  status?: "planned" | "confirmed" | "cancelled";
  starts_at_utc?: string;
  ends_at_utc?: string;
  venue_id?: string;
  notes?: string;
};

export type Membership = {
  id: string;
  band_id: string;
  user_id: string;
  role: string;
  created_at: string;
  user_display_name?: string;
  user_email?: string;
};
