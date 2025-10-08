"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter, useParams } from "next/navigation";
import { useAuth } from "../../../../contexts/AuthContext";
import { apiClient, Band, Event, Venue, CreateEventData, UpdateEventData } from "../../../../lib/api";

export default function EventsPage() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const params = useParams();
  const bandId = params.id as string;

  const [band, setBand] = useState<Band | null>(null);
  const [events, setEvents] = useState<Event[]>([]);
  const [venues, setVenues] = useState<Venue[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingEvent, setEditingEvent] = useState<Event | null>(null);

  // Form state
  const [formData, setFormData] = useState<CreateEventData & { status?: string }>({
    title: "",
    type: "rehearsal",
    starts_at_utc: "",
    ends_at_utc: "",
    venue_id: "",
    notes: "",
    status: "planned",
  });

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!loading && !user) {
      router.push("/auth/login");
    }
  }, [user, loading, router]);

  // Fetch band, events, and venues data
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

        // Fetch events
        const { data: eventsData, error: eventsError } = await apiClient.getBandEvents(bandId);
        if (eventsError) {
          setError(eventsError);
          return;
        }

        // Fetch venues for dropdown
        const { data: venuesData, error: venuesError } = await apiClient.getBandVenues(bandId);
        if (venuesError) {
          setError(venuesError);
          return;
        }

        setBand(bandData as Band);
        setEvents((eventsData as Event[]) || []);
        setVenues((venuesData as Venue[]) || []);
      } catch (error) {
        console.error("Error fetching data:", error);
        setError("Failed to load events");
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, [user, bandId]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value === "" ? undefined : value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.title?.trim() || !formData.starts_at_utc || !formData.ends_at_utc) return;

    setIsCreating(true);
    setError(null);

    try {
      let data: any = null;
      let apiError: string | null = null;

      const eventData = {
        title: formData.title?.trim() || "",
        type: formData.type,
        starts_at_utc: formData.starts_at_utc,
        ends_at_utc: formData.ends_at_utc,
        venue_id: formData.venue_id || undefined,
        notes: formData.notes?.trim() || undefined,
      };

      if (editingEvent) {
        // Update existing event
        const updateData: UpdateEventData = {
          ...eventData,
          status: formData.status as any,
        };
        const response = await apiClient.updateEvent(editingEvent.id, updateData);
        data = response.data;
        apiError = response.error;

        if (!apiError && data) {
          // Update event in the list
          setEvents(prev => prev.map(event => 
            event.id === editingEvent.id ? data as Event : event
          ));
        }
      } else {
        // Create new event
        const response = await apiClient.createEvent(bandId, eventData);
        data = response.data;
        apiError = response.error;

        if (!apiError && data) {
          // Add new event to the list
          setEvents(prev => [...prev, data as Event]);
        }
      }

      if (apiError) {
        // Handle both string errors and object errors from validation
        const errorMessage = typeof apiError === 'string' ? apiError : 
          (apiError as any)?.detail || 
          (Array.isArray(apiError) ? (apiError as any[]).map((e: any) => e.msg || e).join(', ') : 
          'Validation error occurred');
        setError(errorMessage);
        return;
      }

      // Reset form
      resetForm();
    } catch (error) {
      console.error("Event operation error:", error);
      setError("An unexpected error occurred. Please try again.");
    } finally {
      setIsCreating(false);
    }
  };

  const handleEdit = (event: Event) => {
    setEditingEvent(event);
    setFormData({
      title: event.title,
      type: event.type,
      starts_at_utc: event.starts_at_utc.slice(0, 16), // Convert to datetime-local format
      ends_at_utc: event.ends_at_utc.slice(0, 16),
      venue_id: event.venue_id || "",
      notes: event.notes || "",
      status: event.status,
    });
    setShowCreateForm(true);
  };

  const handleDelete = async (eventId: string) => {
    if (!confirm("Are you sure you want to delete this event? This action cannot be undone.")) {
      return;
    }

    try {
      const { error: apiError } = await apiClient.deleteEvent(eventId);

      if (apiError) {
        setError(apiError);
        return;
      }

      // Remove event from the list
      setEvents(prev => prev.filter(event => event.id !== eventId));
    } catch (error) {
      console.error("Delete event error:", error);
      setError("Failed to delete event. Please try again.");
    }
  };

  const resetForm = () => {
    setFormData({
      title: "",
      type: "rehearsal",
      starts_at_utc: "",
      ends_at_utc: "",
      venue_id: "",
      notes: "",
      status: "planned",
    });
    setShowCreateForm(false);
    setEditingEvent(null);
    setError(null);
  };

  const formatDateTime = (dateTimeStr: string) => {
    // Use a consistent format that's timezone-agnostic for SSR
    const date = new Date(dateTimeStr);
    const year = date.getUTCFullYear();
    const month = (date.getUTCMonth() + 1).toString().padStart(2, '0');
    const day = date.getUTCDate().toString().padStart(2, '0');
    const hours = date.getUTCHours().toString().padStart(2, '0');
    const minutes = date.getUTCMinutes().toString().padStart(2, '0');
    
    return `${year}-${month}-${day} ${hours}:${minutes} UTC`;
  };

  const getEventTypeIcon = (type: string) => {
    return type === "gig" ? "🎤" : "🎵";
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "confirmed": return "text-green-600 bg-green-100 dark:bg-green-900 dark:text-green-300";
      case "cancelled": return "text-red-600 bg-red-100 dark:bg-red-900 dark:text-red-300";
      default: return "text-yellow-600 bg-yellow-100 dark:bg-yellow-900 dark:text-yellow-300";
    }
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
            {typeof error === 'string' ? error : 'An error occurred'}
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
                📅 Events
              </h1>
            </div>
            <button
              onClick={() => setShowCreateForm(true)}
              className="bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-indigo-700 transition-colors"
            >
              Add Event
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
              {typeof error === 'string' ? error : 'An error occurred'}
            </div>
          )}

          {/* Create/Edit Form */}
          {showCreateForm && (
            <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg mb-6">
              <div className="px-4 py-5 sm:p-6">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                  {editingEvent ? "Edit Event" : "Add New Event"}
                </h3>
                
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="md:col-span-2">
                      <label
                        htmlFor="title"
                        className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                      >
                        Event Title *
                      </label>
                      <input
                        id="title"
                        name="title"
                        type="text"
                        required
                        className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                        placeholder="Enter event title"
                        value={formData.title}
                        onChange={handleInputChange}
                        maxLength={120}
                      />
                    </div>

                    <div>
                      <label
                        htmlFor="type"
                        className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                      >
                        Event Type *
                      </label>
                      <select
                        id="type"
                        name="type"
                        required
                        className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                        value={formData.type}
                        onChange={handleInputChange}
                      >
                        <option value="rehearsal">🎵 Rehearsal</option>
                        <option value="gig">🎤 Gig</option>
                      </select>
                    </div>

                    {editingEvent && (
                      <div>
                        <label
                          htmlFor="status"
                          className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                        >
                          Status
                        </label>
                        <select
                          id="status"
                          name="status"
                          className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                          value={formData.status}
                          onChange={handleInputChange}
                        >
                          <option value="planned">Planned</option>
                          <option value="confirmed">Confirmed</option>
                          <option value="cancelled">Cancelled</option>
                        </select>
                      </div>
                    )}

                    <div>
                      <label
                        htmlFor="starts_at_utc"
                        className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                      >
                        Start Time *
                      </label>
                      <input
                        id="starts_at_utc"
                        name="starts_at_utc"
                        type="datetime-local"
                        required
                        className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                        value={formData.starts_at_utc}
                        onChange={handleInputChange}
                      />
                    </div>

                    <div>
                      <label
                        htmlFor="ends_at_utc"
                        className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                      >
                        End Time *
                      </label>
                      <input
                        id="ends_at_utc"
                        name="ends_at_utc"
                        type="datetime-local"
                        required
                        className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                        value={formData.ends_at_utc}
                        onChange={handleInputChange}
                      />
                    </div>

                    <div>
                      <label
                        htmlFor="venue_id"
                        className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1"
                      >
                        Venue
                      </label>
                      <select
                        id="venue_id"
                        name="venue_id"
                        className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                        value={formData.venue_id}
                        onChange={handleInputChange}
                      >
                        <option value="">No venue selected</option>
                        {venues.map((venue) => (
                          <option key={venue.id} value={venue.id}>
                            {venue.name}
                          </option>
                        ))}
                      </select>
                    </div>

                    <div className="md:col-span-2">
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
                        placeholder="Additional notes about this event"
                        value={formData.notes}
                        onChange={handleInputChange}
                      />
                    </div>
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
                      disabled={isCreating || !formData.title?.trim() || !formData.starts_at_utc || !formData.ends_at_utc}
                      className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isCreating ? (editingEvent ? "Updating..." : "Creating...") : (editingEvent ? "Update Event" : "Create Event")}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}

          {/* Events List */}
          <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                All Events ({events.length})
              </h2>
              
              {events.length === 0 ? (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">📅</div>
                  <p className="text-gray-500 dark:text-gray-400 mb-4">
                    No events scheduled yet
                  </p>
                  <p className="text-sm text-gray-400 dark:text-gray-500">
                    Add your first event to start scheduling rehearsals and gigs
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {events
                    .sort((a, b) => new Date(a.starts_at_utc).getTime() - new Date(b.starts_at_utc).getTime())
                    .map((event) => {
                      const venue = venues.find(v => v.id === event.venue_id);
                      return (
                        <div
                          key={event.id}
                          className="border border-gray-200 dark:border-gray-600 rounded-lg p-6"
                        >
                          <div className="flex justify-between items-start mb-3">
                            <div className="flex items-center space-x-3">
                              <span className="text-2xl">{getEventTypeIcon(event.type)}</span>
                              <div>
                                <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                                  {event.title}
                                </h3>
                                <span className={`inline-block px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(event.status)}`}>
                                  {event.status.charAt(0).toUpperCase() + event.status.slice(1)}
                                </span>
                              </div>
                            </div>
                            <div className="flex space-x-1">
                              <button
                                onClick={() => handleEdit(event)}
                                className="text-indigo-600 hover:text-indigo-800 p-1"
                                title="Edit event"
                              >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                                </svg>
                              </button>
                              <button
                                onClick={() => handleDelete(event.id)}
                                className="text-red-600 hover:text-red-800 p-1"
                                title="Delete event"
                              >
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                </svg>
                              </button>
                            </div>
                          </div>
                          
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                            <div>
                              <span className="font-medium text-gray-700 dark:text-gray-300">Start:</span>
                              <p className="text-gray-900 dark:text-white">{formatDateTime(event.starts_at_utc)}</p>
                            </div>
                            <div>
                              <span className="font-medium text-gray-700 dark:text-gray-300">End:</span>
                              <p className="text-gray-900 dark:text-white">{formatDateTime(event.ends_at_utc)}</p>
                            </div>
                            {venue && (
                              <div className="md:col-span-2">
                                <span className="font-medium text-gray-700 dark:text-gray-300">Venue:</span>
                                <p className="text-gray-900 dark:text-white">🏛️ {venue.name}</p>
                              </div>
                            )}
                            {event.notes && (
                              <div className="md:col-span-2">
                                <span className="font-medium text-gray-700 dark:text-gray-300">Notes:</span>
                                <p className="text-gray-700 dark:text-gray-400">{event.notes}</p>
                              </div>
                            )}
                          </div>
                        </div>
                      );
                    })}
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}