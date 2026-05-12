import React from 'react';
import { Outlet } from 'react-router-dom';
import { Navbar } from './Navbar';
import { Sidebar } from './Sidebar';
export function MainLayout() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col font-sans text-slate-900">
      <Navbar />
      <div className="flex flex-1 max-w-[1600px] mx-auto w-full">
        <Sidebar />
        <main className="flex-1 flex flex-col min-w-0 overflow-hidden">
          <Outlet />
        </main>
      </div>
    </div>);

}