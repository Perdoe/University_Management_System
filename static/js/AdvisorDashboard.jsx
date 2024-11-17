import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { User, Mail, Phone, Clock, Users } from 'lucide-react';

export default function AdvisorDashboard() {
    const [activeTab, setActiveTab] = useState('students');
    const [formData, setFormData] = useState({
        currentPassword: '',
        newPassword: '',
        confirmPassword: '',
        email: '',
        phone: '',
        officeHours: ''
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
            const response = await fetch('/api/advisor/update-profile', {
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
                    phone: '',
                    officeHours: ''
                });
                setActiveTab('students');
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
            {/* Header section */}
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h1 className="text-2xl font-bold">Advisor Dashboard</h1>
                    <h2 className="text-gray-600">Welcome, A12345</h2>
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
                    onClick={() => setActiveTab('students')}
                    className="px-4 py-3 text-white bg-blue-600 rounded-md hover:bg-blue-700"
                >
                    View Students
                </button>
                <button className="px-4 py-3 text-white bg-blue-600 rounded-md hover:bg-blue-700">
                    Schedule Appointments
                </button>
                <button className="px-4 py-3 text-white bg-blue-600 rounded-md hover:bg-blue-700">
                    Course Registration
                </button>
                <button className="px-4 py-3 text-white bg-blue-600 rounded-md hover:bg-blue-700">
                    Generate Reports
                </button>
                <button className="px-4 py-3 text-white bg-blue-600 rounded-md hover:bg-blue-700">
                    Department Contact
                </button>
                <button className="px-4 py-3 text-white bg-blue-600 rounded-md hover:bg-blue-700">
                    View Calendar
                </button>
            </div>

            {/* Students List Section */}
            {activeTab === 'students' && (
                <Card className="w-full">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Users className="w-5 h-5" />
                            My Students
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="overflow-x-auto">
                            <table className="w-full">
                                <thead>
                                    <tr>
                                        <th className="text-left p-2">Student ID</th>
                                        <th className="text-left p-2">Major</th>
                                        <th className="text-left p-2">GPA</th>
                                        <th className="text-left p-2">Credits</th>
                                        <th className="text-left p-2">Status</th>
                                        <th className="text-left p-2">Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td className="p-2">S12345</td>
                                        <td className="p-2">CIS</td>
                                        <td className="p-2">3.75</td>
                                        <td className="p-2">45</td>
                                        <td className="p-2">
                                            <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                                                Good Standing
                                            </span>
                                        </td>
                                        <td className="p-2">
                                            <button className="text-blue-600 hover:text-blue-800 mr-2">View Details</button>
                                            <button className="text-blue-600 hover:text-blue-800">Schedule Meeting</button>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </CardContent>
                </Card>
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
                                        className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2"
                                        placeholder="Enter new email address"
                                    />
                                </label>
                            </div>

                            {/* Phone Section */}
                            <div className="space-y-2">
                                <label className="block text-sm font-medium text-gray-700">
                                    <div className="flex items-center gap-2 mb-1">
                                        <Phone className="w-4 h-4" />
                                        Phone Number
                                    </div>
                                    <input
                                        type="tel"
                                        name="phone"
                                        value={formData.phone}
                                        onChange={handleInputChange}
                                        className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2"
                                        placeholder="Enter phone number"
                                    />
                                </label>
                            </div>

                            {/* Office Hours Section */}
                            <div className="space-y-2">
                                <label className="block text-sm font-medium text-gray-700">
                                    <div className="flex items-center gap-2 mb-1">
                                        <Clock className="w-4 h-4" />
                                        Office Hours
                                    </div>
                                    <input
                                        type="text"
                                        name="officeHours"
                                        value={formData.officeHours}
                                        onChange={handleInputChange}
                                        className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2"
                                        placeholder="Enter office hours"
                                    />
                                </label>
                            </div>

                            {/* Password Section */}
                            <div className="space-y-2">
                                <label className="block text-sm font-medium text-gray-700">
                                    Current Password
                                    <input
                                        type="password"
                                        name="currentPassword"
                                        value={formData.currentPassword}
                                        onChange={handleInputChange}
                                        className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2"
                                        placeholder="Enter current password"
                                    />
                                </label>
                            </div>

                            <div className="space-y-2">
                                <label className="block text-sm font-medium text-gray-700">
                                    New Password
                                    <input
                                        type="password"
                                        name="newPassword"
                                        value={formData.newPassword}
                                        onChange={handleInputChange}
                                        className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2"
                                        placeholder="Enter new password"
                                    />
                                </label>
                            </div>

                            <div className="space-y-2">
                                <label className="block text-sm font-medium text-gray-700">
                                    Confirm New Password
                                    <input
                                        type="password"
                                        name="confirmPassword"
                                        value={formData.confirmPassword}
                                        onChange={handleInputChange}
                                        className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2"
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
                                            phone: '',
                                            officeHours: ''
                                        });
                                        setActiveTab('students');
                                    }}
                                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700"
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