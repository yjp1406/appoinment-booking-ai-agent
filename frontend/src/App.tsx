import { useState, useEffect } from 'react';
import {
  LiveKitRoom,
  RoomAudioRenderer,
  useRemoteParticipants,
} from '@livekit/components-react';
import { Phone, PhoneOff, Loader2, MessageSquare, BadgeInfo, Calendar } from 'lucide-react';
import { Avatar } from './components/Avatar';
import { Summary } from './components/Summary';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const LIVEKIT_URL = import.meta.env.VITE_LIVEKIT_URL || 'wss://your-livekit-url.livekit.cloud';

function AgentDisconnectListener({ onDisconnect }: { onDisconnect: () => void }) {
  const participants = useRemoteParticipants();
  const [hadAgent, setHadAgent] = useState(false);

  useEffect(() => {
    const hasAgent = participants.length > 0;

    if (hasAgent) {
      setHadAgent(true);
    } else if (hadAgent) {
      // Agent was here, now they are gone
      console.log("Agent disconnected, ending call...");
      onDisconnect();
    }
  }, [participants, hadAgent, onDisconnect]);

  return null;
}

export default function App() {
  const [token, setToken] = useState<string | null>(null);
  const [isCalling, setIsCalling] = useState(false);
  const [showSummary, setShowSummary] = useState(false);
  const [callSummary, setCallSummary] = useState<any>(null);
  const [currentTool] = useState<string | null>(null);

  const startCall = async () => {
    // In a real app, you'd fetch this from your backend
    // For demo purposes, we'll assume a local dev server provides tokens
    setIsCalling(true);
    try {
      // Mocking token fetch
      console.log("Fetching token from backend...");
      const res = await fetch('https://appoinment-booking-ai-agent.onrender.com/api/token');
      const data = await res.json();
      setToken(data.token);
    } catch (e) {
      window.alert("Backend Error: Could not reach the token server. Please ensure server.py is running on port 8080.");
      console.error("Failed to start call", e);
      // For testing, let's just pretend if we can't reach a backend
      setIsCalling(false);
    }
  };

  const endCall = () => {
    setToken(null);
    setIsCalling(false);
    // Mocking summary generation
    generateSummary();
  };

  const generateSummary = async (retries = 5) => {
    try {
      console.log(`Fetching summary (attempts left: ${retries})...`);
      const res = await fetch('https://appoinment-booking-ai-agent.onrender.com/api/summary');
      if (res.ok) {
        const data = await res.json();
        setCallSummary(data);
        setShowSummary(true);
      } else if (retries > 0) {
        // Wait 1 second and try again
        setTimeout(() => generateSummary(retries - 1), 1000);
      } else {
        // Final fallback
        setCallSummary({
          text: "The conversation has ended. Thank you for using our AI booking assistant.",
          appointments: [],
          timestamp: new Date().toISOString()
        });
        setShowSummary(true);
      }
    } catch (e) {
      console.error("Failed to fetch summary", e);
      if (retries > 0) {
        setTimeout(() => generateSummary(retries - 1), 1000);
      } else {
        setCallSummary({
          text: "The conversation has ended. Thank you for using our AI booking assistant.",
          appointments: [],
          timestamp: new Date().toISOString()
        });
        setShowSummary(true);
      }
    }
  };

  return (
    <div className="min-h-screen bg-[#fafafa] flex flex-col font-sans text-gray-900">
      {/* Header */}
      <header className="px-8 py-6 flex justify-between items-center bg-white border-b border-gray-100">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-indigo-600 rounded-xl flex items-center justify-center text-white shadow-indigo-200 shadow-lg">
            <BadgeInfo size={24} />
          </div>
          <h1 className="text-2xl font-black bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 to-purple-600">
            VoiceAgent.ai
          </h1>
        </div>
        <div className="flex items-center gap-2">
          <div className={cn(
            "w-3 h-3 rounded-full animate-pulse",
            isCalling ? "bg-green-500" : "bg-gray-300"
          )} />
          <span className="text-sm font-semibold text-gray-500">
            {isCalling ? "System Online" : "System Ready"}
          </span>
        </div>
      </header>

      <main className="flex-1 flex p-8 gap-8 container mx-auto overflow-hidden">
        {/* Left Column: Avatar & Controls */}
        <div className="flex-1 flex flex-col gap-6">
          <div className="flex-1 relative min-h-[500px]">
            <Avatar
              isCalling={isCalling}
              replicaId={import.meta.env.VITE_TAVUS_REPLICA_ID}
            />

            {/* Real-time Tool Display Overlay */}
            {isCalling && currentTool && (
              <div className="absolute top-6 left-6 animate-in slide-in-from-top duration-300">
                <div className="bg-white/90 backdrop-blur-md px-4 py-2 rounded-full shadow-lg border border-indigo-100 flex items-center gap-2">
                  <Loader2 className="animate-spin text-indigo-600" size={16} />
                  <span className="text-sm font-bold text-gray-800">Processing: {currentTool}</span>
                </div>
              </div>
            )}
          </div>

          {/* Controls */}
          <div className="bg-white p-6 rounded-3xl shadow-xl shadow-gray-200/50 border border-gray-100 flex items-center justify-between">
            {!isCalling ? (
              <button
                onClick={startCall}
                className="flex items-center gap-3 px-8 py-4 bg-indigo-600 text-white rounded-2xl font-bold hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-200 scale-100 active:scale-95 group"
              >
                <Phone className="group-hover:animate-bounce" />
                Start Booking Call
              </button>
            ) : (
              <button
                onClick={endCall}
                className="flex items-center gap-3 px-8 py-4 bg-red-500 text-white rounded-2xl font-bold hover:bg-red-600 transition-all shadow-lg shadow-red-200 scale-100 active:scale-95"
              >
                <PhoneOff />
                End Conversation
              </button>
            )}

            <div className="flex items-center gap-4 text-gray-400">
              <div className="p-3 bg-gray-50 rounded-xl">
                <MessageSquare size={20} />
              </div>
              <div className="p-3 bg-gray-50 rounded-xl text-indigo-600">
                <Calendar size={20} />
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Information/Status */}
        <div className="w-96 flex flex-col gap-6">
          <div className="bg-white p-8 rounded-3xl border border-gray-100 shadow-sm flex-1">
            <h3 className="text-lg font-bold mb-6 flex items-center gap-2">
              <BadgeInfo className="text-indigo-600" size={20} />
              Assistant Capabilities
            </h3>
            <ul className="space-y-4">
              {[
                "Identity Verification",
                "Live Slot Retrieval",
                "Appointment Booking",
                "Cancellation Management",
                "Booking Modification"
              ].map((item, idx) => (
                <li key={idx} className="flex items-center gap-3 text-sm text-gray-600 group">
                  <div className="w-1.5 h-1.5 bg-indigo-200 rounded-full group-hover:bg-indigo-500 transition-colors" />
                  {item}
                </li>
              ))}
            </ul>

            <div className="mt-12 p-6 bg-gradient-to-br from-indigo-50 to-purple-50 rounded-2xl border border-indigo-100">
              <p className="text-xs font-bold text-indigo-500 mb-2 uppercase tracking-tighter">Pro Tip</p>
              <p className="text-sm text-indigo-900 leading-snug">
                "You can ask me to find slots for tomorrow or next week!"
              </p>
            </div>
          </div>

          <div className="bg-gray-900 text-white p-6 rounded-3xl flex items-center justify-between">
            <div>
              <p className="text-xs opacity-60 uppercase font-bold tracking-widest">Call Status</p>
              <p className="text-lg font-bold">{isCalling ? "In Progress" : "Disconnected"}</p>
            </div>
            <div className={cn(
              "w-12 h-12 rounded-full flex items-center justify-center",
              isCalling ? "bg-indigo-500" : "bg-gray-800"
            )}>
              {isCalling ? <Loader2 className="animate-spin" /> : <PhoneOff size={20} />}
            </div>
          </div>
        </div>
      </main>

      {/* LiveKit Interface */}
      {token && (
        <LiveKitRoom
          token={token}
          serverUrl={LIVEKIT_URL}
          audio={true}
          video={false}
          onDisconnected={endCall}
        >
          <RoomAudioRenderer />
          <AgentDisconnectListener onDisconnect={endCall} />
        </LiveKitRoom>
      )}

      {/* Summary Overlay */}
      {showSummary && callSummary && (
        <Summary
          summary={callSummary}
          onClose={() => setShowSummary(false)}
        />
      )}
    </div>
  );
}
