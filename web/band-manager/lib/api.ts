import { getCurrentSession } from "./supabase";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async getAuthHeaders(): Promise<Record<string, string>> {
    const session = await getCurrentSession();
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };

    if (session?.access_token) {
      headers.Authorization = `Bearer ${session.access_token}`;
    }

    return headers;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
  ): Promise<{ data: T | null; error: string | null }> {
    try {
      const headers = await this.getAuthHeaders();

      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        ...options,
        headers: {
          ...headers,
          ...options.headers,
        },
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        const errorMessage =
          errorData.detail || `HTTP ${response.status}: ${response.statusText}`;
        return { data: null, error: errorMessage };
      }

      const data = await response.json();
      return { data, error: null };
    } catch (error) {
      console.error("API request failed:", error);
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

export type Membership = {
  id: string;
  band_id: string;
  user_id: string;
  role: string;
  joined_at: string;
};
