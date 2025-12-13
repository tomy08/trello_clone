"use client";

import Link from 'next/link';
import { useState,useEffect } from "react";
import { useRouter } from "next/navigation";
import { API_URL } from "../constants";
import { isAuthenticated } from "../lib/auth";

export default function LoginPage() {
  const [errorMessage, setErrorMessage] = useState("");
  const router = useRouter();

  
  useEffect(() => {
    const checkAuth = async () => {
      if (await isAuthenticated()) {
        router.push("/dashboard");
      }
    };
    checkAuth();
  }, [router]);


  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const form = e.target as HTMLFormElement;
    const formData = new FormData(form);
    const email = formData.get("email") as string;
    const password = formData.get("password") as string;

    const API_ENDPOINT = `${API_URL}/auth/login`;

    const payload = {
      email: email,
      password: password,
    };

    try {
      const response = await fetch(API_ENDPOINT, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error("Invalid credentials");
      }

      const data = await response.json();
      
      if (data.access_token) {
        localStorage.setItem("access_token", data.access_token);
      }
      if (data.refresh_token) {
        localStorage.setItem("refresh_token", data.refresh_token);
      }
      
      form.reset();
      setErrorMessage("");
      
  
      router.push("/");
      
    } catch (error) {
      console.error("Error:", error);
      setErrorMessage("Invalid email or password. Please try again.");
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-linear-to-br from-blue-50 to-indigo-100 px-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-blue-600 mb-2">Trello</h1>
          <p className="text-gray-600">Log in to continue</p>
        </div>


        <div className="bg-white rounded-lg shadow-xl p-8">
      
          {errorMessage && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-600">{errorMessage}</p>
            </div>
          )}
          
          <form className="space-y-6" onSubmit={handleSubmit}>
   
            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Email address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                placeholder="Enter your email"
              />
            </div>

       
            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-gray-700 mb-2"
              >
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
                placeholder="Enter your password"
              />
            </div>

         
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <input
                  id="remember-me"
                  name="remember-me"
                  type="checkbox"
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label
                  htmlFor="remember-me"
                  className="ml-2 block text-sm text-gray-700"
                >
                  Remember me
                </label>
              </div>

              <Link
                href="#"
                className="text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                Forgot password?
              </Link>
            </div>

         
            <button
              type="submit"
              className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
            >
              Log in
            </button>
          </form>
        </div>

 
        <p className="mt-8 text-center text-sm text-gray-600">
          Don&apos;t have an account?{' '}
          <Link
            href="/signup"
            className="font-medium text-blue-600 hover:text-blue-700"
          >
            Sign up for free
          </Link>
        </p>


        <div className="mt-8 text-center">
          <div className="flex justify-center space-x-4 text-xs text-gray-500">
            <Link href="#" className="hover:text-gray-700">
              Privacy Policy
            </Link>
            <span>•</span>
            <Link href="#" className="hover:text-gray-700">
              Terms of Service
            </Link>
            <span>•</span>
            <Link href="#" className="hover:text-gray-700">
              Help
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}
