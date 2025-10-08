"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter, useParams } from "next/navigation";
import { useAuth } from "../../../contexts/AuthContext";
import { apiClient, Band, Membership } from "../../../lib/api";

export default function BandPage() {
  const { user, loading } = useAuth();
  const router = useRouter();
  const params = useParams();
  const bandId = params.id as string;

  const [band, setBand] = useState<Band | null>(null);
  const [members, setMembers] = useState<Membership[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!loading && !user) {
      router.push("/auth/login");
    }
  }, [user, loading, router]);

  // Fetch band details and members
  useEffect(() => {
    const fetchBandData = async () => {
      if (!user || !bandId) return;

      try {
        setIsLoading(true);
        
        // Fetch band details
        const { data: bandData, error: bandError } = await apiClient.getBand(bandId);
        if (bandError) {
          setError(bandError);
          return;
        }

        // Fetch band members
        const { data: membersData, error: membersError } = await apiClient.getBandMembers(bandId);
        if (membersError) {
          setError(membersError);
          return;
        }

        setBand(bandData as Band);
        setMembers((membersData as Membership[]) || []);
      } catch (error) {
        console.error("Error fetching band data:", error);
        setError("Failed to load band information");
      } finally {
        setIsLoading(false);
      }
    };

    fetchBandData();
  }, [user, bandId]);

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

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="bg-red-50 border border-red-200 text-red-700 px-6 py-4 rounded-md mb-4">
            {error}
          </div>
          <Link
            href="/dashboard"
            className="text-indigo-600 hover:text-indigo-500"
          >
            ← Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  if (!band) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-500 dark:text-gray-400 mb-4">Band not found</p>
          <Link
            href="/dashboard"
            className="text-indigo-600 hover:text-indigo-500"
          >
            ← Back to Dashboard
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
            <div>
              <Link href="/dashboard" className="text-indigo-600 hover:text-indigo-500">
                ← Back to Dashboard
              </Link>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500">Join Code: {band.join_code}</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {/* Band Info Section */}
          <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg mb-6">
            <div className="px-4 py-5 sm:p-6">
              <div className="flex flex-col lg:flex-row lg:items-start lg:space-x-6">
                {/* Band Image Placeholder */}
                <div className="flex-shrink-0 mb-4 lg:mb-0">
                  <div className="w-48 h-48 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center">
                    <div className="text-white text-center">
                      <div className="text-4xl mb-2">🎵</div>
                      <div className="text-sm font-medium">Band Photo</div>
                    </div>
                  </div>
                </div>

                {/* Band Details */}
                <div className="flex-1">
                  <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
                    {band.name}
                  </h1>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        Timezone
                      </label>
                      <p className="mt-1 text-sm text-gray-900 dark:text-white">
                        {band.timezone}
                      </p>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        Created
                      </label>
                      <p className="mt-1 text-sm text-gray-900 dark:text-white">
                        {new Date(band.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>

                  {band.description && (
                    <div className="mb-6">
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Description
                      </label>
                      <p className="text-sm text-gray-900 dark:text-white whitespace-pre-wrap">
                        {band.description}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Members Section */}
          <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg mb-6">
            <div className="px-4 py-5 sm:p-6">
              <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                Band Members ({members.length})
              </h2>
              
              {members.length === 0 ? (
                <p className="text-gray-500 dark:text-gray-400 text-center py-4">
                  No members found
                </p>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {members.map((member) => (
                    <div
                      key={member.id}
                      className="border border-gray-200 dark:border-gray-600 rounded-lg p-4"
                    >
                      <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 bg-gray-300 dark:bg-gray-600 rounded-full flex items-center justify-center">
                          <span className="text-gray-600 dark:text-gray-300 text-sm font-medium">
                            {member.user_id.slice(0, 2).toUpperCase()}
                          </span>
                        </div>
                        <div>
                          <p className="text-sm font-medium text-gray-900 dark:text-white">
                            User ID: {member.user_id.slice(0, 8)}...
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">
                            {member.role} • Joined {new Date(member.joined_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Navigation Sections */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Events Section */}
            <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                    Events
                  </h3>
                  <span className="text-xs text-gray-500 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                    Coming Soon
                  </span>
                </div>
                <div className="text-center py-8">
                  <div className="text-4xl mb-2">📅</div>
                  <p className="text-gray-500 dark:text-gray-400 text-sm">
                    Manage rehearsals, gigs, and other band events
                  </p>
                </div>
              </div>
            </div>

            {/* Venues Section */}
            <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                    Venues
                  </h3>
                  <span className="text-xs text-gray-500 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                    Coming Soon
                  </span>
                </div>
                <div className="text-center py-8">
                  <div className="text-4xl mb-2">🏛️</div>
                  <p className="text-gray-500 dark:text-gray-400 text-sm">
                    Keep track of performance venues and rehearsal spaces
                  </p>
                </div>
              </div>
            </div>

            {/* Setlists Section */}
            <div className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
              <div className="px-4 py-5 sm:p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                    Setlists
                  </h3>
                  <span className="text-xs text-gray-500 bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">
                    Coming Soon
                  </span>
                </div>
                <div className="text-center py-8">
                  <div className="text-4xl mb-2">🎼</div>
                  <p className="text-gray-500 dark:text-gray-400 text-sm">
                    Create and manage song setlists for performances
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}