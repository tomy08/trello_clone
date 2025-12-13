'use client';

import AuthCheck from "../components/auth-check";
import {useState, useEffect} from "react";
import { API_URL } from "../constants";

interface ProfileData {
    id: string;
    email: string;
    username?: string;
    created_at?: string;
}

export default function ProfilePage() {
    const [profileData, setProfileData] = useState<ProfileData | null>(null);
    const [errorMessage, setErrorMessage] = useState<string>();
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const retrieveProfileData = async () => {
            try {
                const token = localStorage.getItem('access_token');
                const API_ENDPOINT = API_URL + '/auth/me';
                
                const response = await fetch(API_ENDPOINT, {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                });

                if (!response.ok) {
                    setErrorMessage('Failed to load profile data');
                    setLoading(false);
                    return;
                }

                const data = await response.json();
                setProfileData(data);
                setLoading(false);
            } catch (error) {
                setErrorMessage('An error occurred while loading your profile');
                setLoading(false);
            }
        };

        retrieveProfileData();
    }, []);

    const getInitials = (email: string) => {
        return email.substring(0, 2).toUpperCase();
    };

    return (
        <>
            <AuthCheck />
            <div className="min-h-screen bg-gradient-to-br from-blue-500 via-blue-600 to-indigo-700">
                <div className="container mx-auto px-4 py-12">
                    {loading && (
                        <div className="flex justify-center items-center h-64">
                            <div className="text-white text-xl">Loading profile...</div>
                        </div>
                    )}
                    
                    {errorMessage && (
                        <div className="max-w-2xl mx-auto mb-6">
                            <div className="bg-red-500 text-white px-6 py-4 rounded-lg shadow-lg">
                                <p className="font-semibold">⚠ {errorMessage}</p>
                            </div>
                        </div>
                    )}
                    
                    {profileData && (
                        <div className="max-w-4xl mx-auto">
                            {/* Header Card */}
                            <div className="bg-white rounded-lg shadow-xl mb-6 overflow-hidden">
                                <div className="h-32 bg-gradient-to-r from-blue-400 to-indigo-500"></div>
                                <div className="px-8 pb-8">
                                    <div className="flex items-end -mt-16 mb-6">
                                        <div className="w-32 h-32 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 border-4 border-white shadow-lg flex items-center justify-center">
                                            <span className="text-white text-4xl font-bold">
                                                {getInitials(profileData.email)}
                                            </span>
                                        </div>
                                        <div className="ml-6 mb-2">
                                            <h1 className="text-3xl font-bold text-gray-800">
                                                {profileData.username || 'User Profile'}
                                            </h1>
                                            <p className="text-gray-600">{profileData.email}</p>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            {/* Info Cards Grid */}
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                {/* Account Information */}
                                <div className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow">
                                    <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
                                        <span className="mr-2">👤</span>
                                        Account Information
                                    </h2>
                                    <div className="space-y-4">
                                        <div>
                                            <label className="block text-sm font-semibold text-gray-600 mb-1">Email Address</label>
                                            <p className="text-gray-900 bg-gray-50 px-3 py-2 rounded">{profileData.email}</p>
                                        </div>
                                        {profileData.username && (
                                            <div>
                                                <label className="block text-sm font-semibold text-gray-600 mb-1">Username</label>
                                                <p className="text-gray-900 bg-gray-50 px-3 py-2 rounded">{profileData.username}</p>
                                            </div>
                                        )}
                                        <div>
                                            <label className="block text-sm font-semibold text-gray-600 mb-1">User ID</label>
                                            <p className="text-gray-900 bg-gray-50 px-3 py-2 rounded font-mono text-sm">{profileData.id}</p>
                                        </div>
                                    </div>
                                </div>

                              
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </>
    );
}