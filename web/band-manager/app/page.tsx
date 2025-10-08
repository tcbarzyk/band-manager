import Image from "next/image";
import Link from "next/link";

export default function Home() {
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

        <div className="flex gap-4 items-center flex-col sm:flex-row">
          <div className="text-center text-sm text-gray-500 dark:text-gray-400">
            <p>Development Version - Authentication pages created</p>
            <p className="mt-2">
              Try the <Link href="/auth/login" className="text-indigo-600 hover:text-indigo-500">login</Link> or{' '}
              <Link href="/auth/signup" className="text-indigo-600 hover:text-indigo-500">signup</Link> pages
            </p>
          </div>
        </div>
      </main>
      <footer className="row-start-3 flex gap-[24px] flex-wrap items-center justify-center">
        <a
          className="flex items-center gap-2 hover:underline hover:underline-offset-4"
          href="https://nextjs.org/learn?utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Image
            aria-hidden
            src="/file.svg"
            alt="File icon"
            width={16}
            height={16}
          />
          Learn
        </a>
        <a
          className="flex items-center gap-2 hover:underline hover:underline-offset-4"
          href="https://vercel.com/templates?framework=next.js&utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Image
            aria-hidden
            src="/window.svg"
            alt="Window icon"
            width={16}
            height={16}
          />
          Examples
        </a>
        <a
          className="flex items-center gap-2 hover:underline hover:underline-offset-4"
          href="https://nextjs.org?utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
          target="_blank"
          rel="noopener noreferrer"
        >
          <Image
            aria-hidden
            src="/globe.svg"
            alt="Globe icon"
            width={16}
            height={16}
          />
          Go to nextjs.org →
        </a>
      </footer>
    </div>
  );
}
