-- Supabase Database Schema

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('super_admin', 'placement_officer', 'training_coordinator', 'student')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Students Table
CREATE TABLE students (
    id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    roll_number VARCHAR(50) UNIQUE,
    registration_number VARCHAR(50) UNIQUE,
    full_name VARCHAR(255),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(20),
    gender VARCHAR(20),
    date_of_birth DATE,
    branch VARCHAR(100),
    department VARCHAR(100),
    graduation_year INTEGER,
    cgpa NUMERIC(4, 2),
    tenth_percentage NUMERIC(5, 2),
    twelfth_percentage NUMERIC(5, 2),
    diploma_percentage NUMERIC(5, 2),
    active_backlogs INTEGER DEFAULT 0,
    address TEXT,
    skills TEXT,
    certifications TEXT,
    projects TEXT,
    resume_url VARCHAR(255),
    linkedin_url VARCHAR(255),
    github_url VARCHAR(255),
    leetcode_url VARCHAR(255),
    hackerrank_url VARCHAR(255),
    placement_status VARCHAR(50) DEFAULT 'Unplaced' CHECK (placement_status IN ('Unplaced', 'Placed')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Companies Table
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_name VARCHAR(255) NOT NULL,
    logo_url VARCHAR(255),
    website VARCHAR(255),
    industry VARCHAR(100),
    location VARCHAR(255),
    job_role VARCHAR(255),
    package VARCHAR(100),
    ctc NUMERIC(10, 2),
    bond_details TEXT,
    job_description TEXT,
    required_skills TEXT,
    contact_person VARCHAR(255),
    hr_email VARCHAR(255),
    hr_phone VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Placement Drives Table
CREATE TABLE placement_drives (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    drive_name VARCHAR(255) NOT NULL,
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    drive_date DATE,
    registration_start TIMESTAMP WITH TIME ZONE,
    registration_end TIMESTAMP WITH TIME ZONE,
    aptitude_test_date TIMESTAMP WITH TIME ZONE,
    technical_interview_date TIMESTAMP WITH TIME ZONE,
    hr_interview_date TIMESTAMP WITH TIME ZONE,
    venue VARCHAR(255),
    drive_status VARCHAR(50) DEFAULT 'Upcoming' CHECK (drive_status IN ('Upcoming', 'Registration Open', 'Registration Closed', 'Ongoing', 'Completed', 'Cancelled')),
    min_cgpa NUMERIC(4, 2),
    allowed_branches TEXT[],
    max_backlogs INTEGER,
    graduation_year INTEGER,
    required_skills TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Applications Table
CREATE TABLE applications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    drive_id UUID REFERENCES placement_drives(id) ON DELETE CASCADE,
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'Applied' CHECK (status IN ('Applied', 'Shortlisted', 'Aptitude Cleared', 'Technical Cleared', 'HR Cleared', 'Selected', 'Rejected', 'Withdrawn')),
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (drive_id, student_id)
);

-- 6. Announcements Table
CREATE TABLE announcements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    is_pinned BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 7. Notifications Table
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply triggers
CREATE TRIGGER update_users_modtime BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_modified_column();
CREATE TRIGGER update_students_modtime BEFORE UPDATE ON students FOR EACH ROW EXECUTE FUNCTION update_modified_column();
CREATE TRIGGER update_companies_modtime BEFORE UPDATE ON companies FOR EACH ROW EXECUTE FUNCTION update_modified_column();
CREATE TRIGGER update_placement_drives_modtime BEFORE UPDATE ON placement_drives FOR EACH ROW EXECUTE FUNCTION update_modified_column();
CREATE TRIGGER update_applications_modtime BEFORE UPDATE ON applications FOR EACH ROW EXECUTE FUNCTION update_modified_column();
CREATE TRIGGER update_announcements_modtime BEFORE UPDATE ON announcements FOR EACH ROW EXECUTE FUNCTION update_modified_column();
