-- Database schema for AI Voice Agent Appointment Booking

-- Table for storing appointments
CREATE TABLE IF NOT EXISTS appointments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contact_number TEXT NOT NULL,
    slot TIMESTAMP WITH TIME ZONE NOT NULL,
    name TEXT,
    status TEXT NOT NULL DEFAULT 'confirmed' CHECK (status IN ('confirmed', 'cancelled')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Prevent double-booking for the same slot
    UNIQUE(slot)
);

-- Index for faster lookups by contact number
CREATE INDEX IF NOT EXISTS idx_appointments_contact_number ON appointments(contact_number);

-- Enable Row Level Security (RLS) - Note: In a production app, you'd add policies here.
-- For this assignment, we will use the service_role key or assume public access for simplicity.
ALTER TABLE appointments ENABLE ROW LEVEL SECURITY;

-- Creating a simple policy for full access (assuming service role or public demo)
CREATE POLICY "Full access for agent" ON appointments FOR ALL USING (true);
