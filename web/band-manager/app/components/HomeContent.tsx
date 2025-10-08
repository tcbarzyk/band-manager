"use client";

import Image from "next/image";
import Link from "next/link";
import { useAuth } from "../../contexts/AuthContext";
import { useRouter } from "next/navigation";

export function HomeContent() {
  const { user, loading } = useAuth();
  const router = useRouter();

  // If user is logged in, redirect to dashboard
  if (!loading && user) {
    router.push("/dashboard");
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="font-sans grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20">
      <main className="flex flex-col gap-[32px] row-start-2 items-center sm:items-start">
        <div className="text-center sm:text-left">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
            🎵 Band Manager
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-300 mb-8">
            Manage your band, book gigs, and connect with other musicians
          </p>
        </div>

        <div className="flex gap-4 items-center flex-col sm:flex-row mb-8">
          <Link
            href="/auth/login"
            className="rounded-full border border-solid border-transparent transition-colors flex items-center justify-center bg-indigo-600 text-white gap-2 hover:bg-indigo-700 font-medium text-sm sm:text-base h-10 sm:h-12 px-4 sm:px-5 sm:w-auto"
          >
            Sign In
          </Link>
          <Link
            href="/auth/signup"
            className="rounded-full border border-solid border-indigo-600 text-indigo-600 dark:border-indigo-400 dark:text-indigo-400 transition-colors flex items-center justify-center hover:bg-indigo-50 dark:hover:bg-indigo-900/20 font-medium text-sm sm:text-base h-10 sm:h-12 px-4 sm:px-5 w-full sm:w-auto"
          >
            Create Account
          </Link>
        </div>
      </main>
    </div>
  );
}
