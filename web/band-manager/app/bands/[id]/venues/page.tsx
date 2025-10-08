"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter, useParams } from "next/navigation";
import { useAuth } from "../../../../contexts/AuthContext";
import { apiClient, Band, Venue, CreateVenueData } from "../../../../lib/api";

export default function VenuesPage() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const params = useParams();
  const bandId = params.id as string;

  const [band, setBand] = useState<Band | null>(null);
  const [venues, setVenues] = useState<Venue[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingVenue, setEditingVenue] = useState<Venue | null>(null);

  // Form state
  const [formData, setFormData] = useState<CreateVenueData>({
    name: "",
    address: "",
    notes: "",
  });

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!loading && !user) {
      router.push("/auth/login");
    }
  }, [user, loading, router]);

  // Fetch band and venues data
  useEffect(() => {
    const fetchData = async () => {
      if (!user || !bandId) return;

      try {
        setIsLoading(true);
        
        // Fetch band details
        const { data: bandData, error: bandError } = await apiClient.getBand(bandId);
        if (bandError) {
          setError(bandError);
          return;
        }

        // Fetch venues
        const { data: venuesData, error: venuesError } = await apiClient.getBandVenues(bandId);
        if (venuesError) {
          setError(venuesError);
          return;
        }

        setBand(bandData as Band);
        setVenues((venuesData as Venue[]) || []);
      } catch (error) {
        console.error("Error fetching data:", error);
        setError("Failed to load venues");
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [user, bandId]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name.trim()) return;

    setIsCreating(true);
    setError(null);

    try {
      let data: any = null;
      let apiError: string | null = null;

      if (editingVenue) {
        // Update existing venue
        const response = await apiClient.updateVenue(editingVenue.id, {
          name: formData.name.trim(),
          address: formData.address?.trim() || undefined,
          notes: formData.notes?.trim() || undefined,
        });
        data = response.data;
        apiError = response.error;

        if (!apiError && data) {
          // Update venue in the list
          setVenues(prev => prev.map(venue => 
            venue.id === editingVenue.id ? data as Venue : venue
          ));
        }
      } else {
        // Create new venue
        const response = await apiClient.createVenue(bandId, {
          name: formData.name.trim(),
          address: formData.address?.trim() || undefined,
          notes: formData.notes?.trim() || undefined,
        });
        data = response.data;
        apiError = response.error;

        if (!apiError && data) {
          // Add new venue to the list
          setVenues(prev => [...prev, data as Venue]);
        }
      }

      if (apiError) {
        setError(apiError);
        return;
      }

      // Reset form
      resetForm();
    } catch (error) {
      console.error("Venue operation error:", error);
      setError("An unexpected error occurred. Please try again.");
    } finally {
      setIsCreating(false);
    }
  };

  const handleEdit = (venue: Venue) => {
    setEditingVenue(venue);
    setFormData({
      name: venue.name,
      address: venue.address || "",
      notes: venue.notes || "",
    });
    setShowCreateForm(true);
  };

  const handleDelete = async (venueId: string) => {
    if (!confirm("Are you sure you want to delete this venue? This action cannot be undone.")) {
      return;
    }

    try {
      const { error: apiError } = await apiClient.deleteVenue(venueId);

      if (apiError) {
        setError(apiError);
        return;
      }

      // Remove venue from the list
      setVenues(prev => prev.filter(venue => venue.id !== venueId));
    } catch (error) {
      console.error("Delete venue error:", error);
      setError("Failed to delete venue. Please try again.");
    }
  };

  const resetForm = () => {
    setFormData({ name: "", address: "", notes: "" });
    setShowCreateForm(false);
    setEditingVenue(null);
    setError(null);
  };

  if (loading || isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!user) {
    return null; // Will redirect to login
  }

  if (error && !band) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-md mb-4">
            {error}
          </div>
          <Link
            href={`/bands/${bandId}`}
            className="text-indigo-600 hover:text-indigo-500"
          >
            ← Back to Band
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-4">
              <Link href={`/bands/${bandId}`} className="text-indigo-600 hover:text-indigo-500">
                ← Back to {band?.name || "Band"}
              </Link>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                🏛️ Venues
              </h1>
            </div>
            <button
              onClick={() => setShowCreateForm(true)}
              className="bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-indigo-700 transition-colors"
            >
              Add Venue
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Error Display */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md mb-6">
              {error}
            </div>
          )}

          {/* Create/Edit Form */}
          {showCreateForm && (
            <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg mb-6">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                  {editingVenue ? "Edit Venue" : "Add New Venue"}
                </h3>
                
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div>
                    <label
                      htmlFor="name"
                      className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                    >
                      Venue Name *
                    </label>
                    <input
                      id="name"
                      name="name"
                      type="text"
                      required
                      className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                      placeholder="Enter venue name"
                      value={formData.name}
                      onChange={handleInputChange}
                      maxLength={120}
                    />
                  </div>

                  <div>
                    <label
                      htmlFor="address"
                      className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                    >
                      Address
                    </label>
                    <input
                      id="address"
                      name="address"
                      type="text"
                      className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                      placeholder="Enter venue address"
                      value={formData.address}
                      onChange={handleInputChange}
                    />
                  </div>

                  <div>
                    <label
                      htmlFor="notes"
                      className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                    >
                      Notes
                    </label>
                    <textarea
                      id="notes"
                      name="notes"
                      rows={3}
                      className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                      placeholder="Additional notes about this venue (sound system, capacity, etc.)"
                      value={formData.notes}
                      onChange={handleInputChange}
                    />
                  </div>

                  <div className="flex justify-end space-x-3">
                    <button
                      type="button"
                      onClick={resetForm}
                      className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700"
                    >
                      Cancel
                    </button>
                    <button
                      type="submit"
                      disabled={isCreating || !formData.name.trim()}
                      className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isCreating ? (editingVenue ? "Updating..." : "Creating...") : (editingVenue ? "Update Venue" : "Create Venue")}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}

          {/* Venues List */}
          <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                All Venues ({venues.length})
              </h2>
              
              {venues.length === 0 ? (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">🏛️</div>
                  <p className="text-gray-500 dark:text-gray-400 mb-4">
                    No venues added yet
                  </p>
                  <p className="text-sm text-gray-400 dark:text-gray-500">
                    Add your first venue to keep track of performance spaces and rehearsal locations
                  </p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {venues.map((venue) => (
                    <div
                      key={venue.id}
                      className="border border-gray-200 dark:border-gray-600 rounded-lg p-6"
                    >
                      <div className="flex justify-between items-start mb-3">
                        <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                          {venue.name}
                        </h3>
                        <div className="flex space-x-1">
                          <button
                            onClick={() => handleEdit(venue)}
                            className="text-indigo-600 hover:text-indigo-800 p-1"
                            title="Edit venue"
                          >
                            <svg
                              className="w-4 h-4"
                              fill="none"
                              stroke="currentColor"
                              viewBox="0 0 24 24"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                              />
                            </svg>
                          </button>
                          <button
                            onClick={() => handleDelete(venue.id)}
                            className="text-red-600 hover:text-red-800 p-1"
                            title="Delete venue"
                          >
                            <svg
                              className="w-4 h-4"
                              fill="none"
                              stroke="currentColor"
                              viewBox="0 0 24 24"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                              />
                            </svg>
                          </button>
                        </div>
                      </div>
                      
                      {venue.address && (
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                          📍 {venue.address}
                        </p>
                      )}
                      
                      {venue.notes && (
                        <p className="text-sm text-gray-500 dark:text-gray-500">
                          {venue.notes}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}