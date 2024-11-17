import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Lock, Mail, User } from 'lucide-react';

export function StaffDashboard() {
    const [activeTab, setActiveTab] = useState('department');
    const [departmentData, setDepartmentData] = useState({
        courseOfferings: {
            totalActiveCourses: 53,
            availableSeats: 1250
        },
        faculty: {
            totalFaculty: 14,
            averageCourseLoad: 3.2
        },
        requirements: {
            requiredCredits: 120,
            coreCourses: 45
        }
    });

    const [formData, setFormData] = useState({
        currentPassword: '',
        newPassword: '',
        confirmPassword: '',
        email: '',
    });

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleProfileSubmit = async (e) => {
        e.preventDefault();

        if (formData.newPassword !== formData.confirmPassword) {
            alert('New passwords do not match');
            return;
        }

        try {
            const response = await fetch('/api/staff/update-profile', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData),
            });

            if (response.ok) {
                alert('Profile updated successfully');
                setFormData({
                    currentPassword: '',
                    newPassword: '',
                    confirmPassword: '',
                    email: '',
                });
                setActiveTab('department'); // Return to main view after success
            } else {
                const data = await response.json();
                alert(data.message || 'Failed to update profile');
            }
        } catch (error) {
            alert('An error occurred while updating profile');
        }
    };

    return (
        <div className="p-6">
            {/* Header section with title and profile button */}
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h1 className="text-2xl font-bold">Staff Dashboard</h1>
                    <h2 className="text-gray-600">Welcome, STF1</h2>
                </div>
                <button
                    onClick={() => setActiveTab('profile')}
                    className="flex items-center gap-2 px-4 py-2 text-white bg-blue-600 rounded-md hover:bg-blue-700"
                >
                    <User className="w-4 h-4" />
                    Profile Settings
                </button>
            </div>

            {/* Main action buttons */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                <button
                    onClick={() => setActiveTab('department')}
                    className="px-4 py-3 text-white bg-blue-600 rounded-md hover:bg-blue-700"
                >
                    Department Statistics
                </button>
                <button className="px-4 py-3 text-white bg-blue-600 rounded-md hover:bg-blue-700">
                    Manage Courses
                </button>
                <button className="px-4 py-3 text-white bg-blue-600 rounded-md hover:bg-blue-700">
                    Manage Students
                </button>
                <button className="px-4 py-3 text-white bg-blue-600 rounded-md hover:bg-blue-700">
                    View Schedule
                </button>
                <button className="px-4 py-3 text-white bg-blue-600 rounded-md hover:bg-blue-700">
                    Generate Reports
                </button>
                <button className="px-4 py-3 text-white bg-blue-600 rounded-md hover:bg-blue-700">
                    System Logs
                </button>
            </div>

            {/* Department Statistics Section */}
            {activeTab === 'department' && (
                <div className="bg-white rounded-lg shadow p-6">
                    <h2 className="text-xl font-bold mb-6">Department Statistics</h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                        <div>
                            <h3 className="text-gray-600">Total Active Courses</h3>
                            <p className="text-3xl font-bold text-blue-600">53</p>
                        </div>
                        <div>
                            <h3 className="text-gray-600">Total Faculty</h3>
                            <p className="text-3xl font-bold text-blue-600">14</p>
                        </div>
                        <div>
                            <h3 className="text-gray-600">Active Students</h3>
                            <p className="text-3xl font-bold text-blue-600">57</p>
                        </div>
                        <div>
                            <h3 className="text-gray-600">Available Seats</h3>
                            <p className="text-3xl font-bold text-blue-600">1250</p>
                        </div>
                    </div>
                </div>
            )}

            {/* Profile Management Section */}
            {activeTab === 'profile' && (
                <Card className="w-full max-w-2xl mx-auto">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <User className="w-5 h-5" />
                            Profile Management
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <form onSubmit={handleProfileSubmit} className="space-y-4">
                            {/* Email Section */}
                            <div className="space-y-2">
                                <label className="block text-sm font-medium text-gray-700">
                                    <div className="flex items-center gap-2 mb-1">
                                        <Mail className="w-4 h-4" />
                                        Email Address
                                    </div>
                                    <input
                                        type="email"
                                        name="email"
                                        value={formData.email}
                                        onChange={handleInputChange}
                                        className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500 focus:ring-blue-500"
                                        placeholder="Enter new email address"
                                    />
                                </label>
                            </div>

                            {/* Current Password */}
                            <div className="space-y-2">
                                <label className="block text-sm font-medium text-gray-700">
                                    <div className="flex items-center gap-2 mb-1">
                                        <Lock className="w-4 h-4" />
                                        Current Password
                                    </div>
                                    <input
                                        type="password"
                                        name="currentPassword"
                                        value={formData.currentPassword}
                                        onChange={handleInputChange}
                                        className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500 focus:ring-blue-500"
                                        placeholder="Enter current password"
                                    />
                                </label>
                            </div>

                            {/* New Password */}
                            <div className="space-y-2">
                                <label className="block text-sm font-medium text-gray-700">
                                    <div className="flex items-center gap-2 mb-1">
                                        <Lock className="w-4 h-4" />
                                        New Password
                                    </div>
                                    <input
                                        type="password"
                                        name="newPassword"
                                        value={formData.newPassword}
                                        onChange={handleInputChange}
                                        className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500 focus:ring-blue-500"
                                        placeholder="Enter new password"
                                    />
                                </label>
                            </div>

                            {/* Confirm Password */}
                            <div className="space-y-2">
                                <label className="block text-sm font-medium text-gray-700">
                                    <div className="flex items-center gap-2 mb-1">
                                        <Lock className="w-4 h-4" />
                                        Confirm New Password
                                    </div>
                                    <input
                                        type="password"
                                        name="confirmPassword"
                                        value={formData.confirmPassword}
                                        onChange={handleInputChange}
                                        className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 focus:border-blue-500 focus:ring-blue-500"
                                        placeholder="Confirm new password"
                                    />
                                </label>
                            </div>

                            {/* Submit Buttons */}
                            <div className="flex justify-end space-x-3 pt-4">
                                <button
                                    type="button"
                                    onClick={() => {
                                        setFormData({
                                            currentPassword: '',
                                            newPassword: '',
                                            confirmPassword: '',
                                            email: '',
                                        });
                                        setActiveTab('department');
                                    }}
                                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                                >
                                    Save Changes
                                </button>
                            </div>
                        </form>
                    </CardContent>
                </Card>
            )}

            {/* Back to Sign In button */}
            <button
                onClick={() => window.location.href = '/signin'}
                className="mt-8 px-4 py-2 text-white bg-red-600 rounded-md hover:bg-red-700"
            >
                Back to Sign In
            </button>
        </div>
    );
}