import React, { useState } from 'react';
import ChatInterface from './ChatInterface';

const Dashboard = () => {
    return (
        <div className="flex h-screen overflow-hidden">
            {/* Sidebar */}
            <aside className="hidden w-64 flex-col border-r bg-card md:flex">
                <div className="p-6">
                    <h1 className="text-xl font-bold tracking-tight text-primary">DataPella AI</h1>
                </div>
                <nav className="flex-1 space-y-2 p-4">
                    <div className="rounded-md bg-secondary/50 p-2 text-sm font-medium">New Analysis</div>
                    <div className="rounded-md p-2 text-sm text-muted-foreground hover:bg-secondary/30">History</div>
                    <div className="rounded-md p-2 text-sm text-muted-foreground hover:bg-secondary/30">Settings</div>
                </nav>
            </aside>

            {/* Main Content */}
            <main className="flex flex-1 flex-col overflow-hidden">
                <header className="flex h-14 items-center border-b px-6">
                    <h2 className="text-lg font-medium">Analytics Workspace</h2>
                </header>

                <div className="flex-1 overflow-hidden p-6">
                    <div className="grid h-full grid-cols-1 gap-6 lg:grid-cols-3">
                        {/* Chat Area (2 cols) */}
                        <div className="lg:col-span-1 border rounded-lg bg-card/50 p-4 flex flex-col">
                            <ChatInterface />
                        </div>

                        {/* Visualisation Area (2 cols) */}
                        <div className="lg:col-span-2 border rounded-lg bg-card/50 p-4 flex flex-col items-center justify-center text-muted-foreground">
                            <p>Chart Visualizations will appear here based on your query.</p>
                            {/* TODO: Add Chart Component */}
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default Dashboard;
