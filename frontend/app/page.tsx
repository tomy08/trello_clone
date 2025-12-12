import Image from 'next/image'
import { redirect } from "next/navigation";
import Link from 'next/link'

import Header from './components/header-hero'

async function handleSignup(formData: FormData) {
  'use server'
  
  const email = formData.get("email") as string;
  redirect(`/signup?email=${encodeURIComponent(email)}`);
}

export default function Home() {

  return (
    <>
      <Header />
      <main className="flex flex-col">
        <div className="container mx-auto px-6 py-16 flex flex-col md:flex-row items-center justify-center gap-12 flex-1">
          <section className="max-w-xl mb-auto md:mb-0">
            <h1 className="text-3xl md:text-6xl font-semibold text-gray-900 leading-tight">
              Capture, organize, and tackle your to-dos from anywhere.
            </h1>
            <p className="mt-6 text-xl text-gray-700">
              Escape the clutter and chaos—unleash your productivity with
              Trello.
            </p>
            <form action={handleSignup} className="mt-8 flex flex-col sm:flex-row gap-3">
              <input
                type="email"
                name="email"
                placeholder="Email"
                required
                className="flex-1 border border-gray-300 px-4 py-3 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button
                type="submit"
                className="bg-blue-600 text-white px-6 py-3 rounded font-medium hover:bg-blue-700 transition-colors whitespace-nowrap"
              >
                Sign up - it&apos;s free!
              </button>
            </form>
            <p className="mt-4 text-sm text-gray-600">
              By entering my email, I acknowledge the{' '}
              <Link
                href="#"
                className="text-blue-600 underline hover:text-blue-700"
              >
                Atlassian Privacy Policy
              </Link>
            </p>
          </section>
          <div className="shrink-0 self-end">
            <Image
              src="/foto-hero.png"
              alt="Hero Image"
              width={650}
              height={760}
              className="max-w-full h-auto"
            />
          </div>
        </div>
      </main>
    </>
  )
}
