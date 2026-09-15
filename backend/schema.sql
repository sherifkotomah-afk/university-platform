-- ============================================================
-- UNIVERSITY PLATFORM — DATABASE SCHEMA (PostgreSQL)
-- Designed for Ghanaian tertiary institution structure
-- White-label: all institution-specific settings live in
-- `institution_settings`, nothing else is hardcoded.
-- ============================================================

-- ---------- 0. INSTITUTION / WHITE-LABEL CONFIG ----------
CREATE TABLE institution_settings (
    id SERIAL PRIMARY KEY,
    institution_name VARCHAR(255) NOT NULL,
    short_code VARCHAR(20) NOT NULL,          -- e.g. 'UG', 'KNUST', 'UCC'
    logo_url TEXT,
    primary_color VARCHAR(7) DEFAULT '#1a1a2e',
    secondary_color VARCHAR(7) DEFAULT '#ffffff',
    grading_system VARCHAR(10) NOT NULL DEFAULT 'GPA' CHECK (grading_system IN ('GPA','CWA')),
    academic_year VARCHAR(9) NOT NULL,        -- e.g. '2025/2026'
    current_semester INT NOT NULL DEFAULT 1,
    contact_email VARCHAR(255),
    contact_phone VARCHAR(20),
    address TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ---------- 1. USERS & ROLES ----------
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('applicant','student','faculty','admin','registrar','finance')),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    must_change_password BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    refresh_token_hash VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ---------- 2. ACADEMIC STRUCTURE ----------
CREATE TABLE schools (            -- e.g. "School of Engineering"
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    dean_user_id INT REFERENCES users(id)
);

CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    school_id INT REFERENCES schools(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    hod_user_id INT REFERENCES users(id)  -- head of department
);

CREATE TABLE programmes (          -- e.g. "BSc Computer Science"
    id SERIAL PRIMARY KEY,
    department_id INT REFERENCES departments(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    level VARCHAR(20) NOT NULL CHECK (level IN ('Diploma','Undergraduate','Masters','PhD','Certificate')),
    duration_years NUMERIC(3,1) NOT NULL,
    total_credit_hours INT NOT NULL,
    accreditation_status VARCHAR(50) DEFAULT 'Accredited', -- GTEC accreditation tracking
    accreditation_expiry DATE,
    description TEXT
);

CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    programme_id INT REFERENCES programmes(id) ON DELETE CASCADE,
    code VARCHAR(20) NOT NULL,        -- e.g. "CSCD 401"
    title VARCHAR(255) NOT NULL,
    credit_hours INT NOT NULL,
    semester_offered INT NOT NULL,    -- 1 or 2
    year_level INT NOT NULL,          -- 1,2,3,4...
    course_type VARCHAR(20) NOT NULL CHECK (course_type IN ('Required','Elective')),
    description TEXT,
    syllabus_url TEXT,
    approved_by_board BOOLEAN DEFAULT FALSE   -- Faculty/Academic Board approval
);

CREATE TABLE course_prerequisites (
    course_id INT REFERENCES courses(id) ON DELETE CASCADE,
    prerequisite_course_id INT REFERENCES courses(id) ON DELETE CASCADE,
    PRIMARY KEY (course_id, prerequisite_course_id)
);

CREATE TABLE academic_calendar (
    id SERIAL PRIMARY KEY,
    academic_year VARCHAR(9) NOT NULL,
    semester INT NOT NULL,
    registration_start DATE,
    registration_end DATE,
    lectures_start DATE,
    lectures_end DATE,
    exams_start DATE,
    exams_end DATE
);

-- ---------- 3. APPLICANTS / ADMISSIONS ----------
CREATE TABLE applications (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    programme_id INT REFERENCES programmes(id),
    application_type VARCHAR(20) CHECK (application_type IN ('Fresh','Transfer','International','Graduate')),
    status VARCHAR(30) DEFAULT 'Submitted' CHECK (status IN
        ('Draft','Submitted','Under Review','Offer Made','Accepted','Rejected','Enrolled')),
    -- Ghana-specific qualification fields
    wassce_index_number VARCHAR(50),
    wassce_year INT,
    core_english_grade VARCHAR(2),
    core_maths_grade VARCHAR(2),
    core_science_or_social_studies_grade VARCHAR(2),
    elective_subjects JSONB,          -- [{subject, grade}, ...] min 3 required
    gtec_verification_reference VARCHAR(100),  -- for foreign WASSCE verification
    prior_qualification VARCHAR(100), -- e.g. HND, Diploma for mature/transfer entry
    prior_institution VARCHAR(255),
    prior_fgpa_or_cwa NUMERIC(5,2),
    submitted_at TIMESTAMP,
    decision_at TIMESTAMP,
    decision_notes TEXT
);

CREATE TABLE application_documents (
    id SERIAL PRIMARY KEY,
    application_id INT REFERENCES applications(id) ON DELETE CASCADE,
    document_type VARCHAR(50) NOT NULL, -- transcript, WASSCE result slip, passport photo, essay, ref letter
    file_url TEXT NOT NULL,
    uploaded_at TIMESTAMP DEFAULT NOW(),
    verified BOOLEAN DEFAULT FALSE
);

-- ---------- 4. STUDENTS & ENROLLMENT ----------
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    user_id INT UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    student_id_number VARCHAR(30) UNIQUE NOT NULL,
    programme_id INT REFERENCES programmes(id),
    current_year_level INT DEFAULT 1,
    admission_year VARCHAR(9),
    status VARCHAR(20) DEFAULT 'Active' CHECK (status IN ('Active','On Leave','Withdrawn','Dismissed','Graduated')),
    registration_hold BOOLEAN DEFAULT FALSE,     -- blocks registration/transcript per Ghana academic policy
    hold_reason TEXT
);

CREATE TABLE course_registrations (
    id SERIAL PRIMARY KEY,
    student_id INT REFERENCES students(id) ON DELETE CASCADE,
    course_id INT REFERENCES courses(id),
    academic_year VARCHAR(9) NOT NULL,
    semester INT NOT NULL,
    status VARCHAR(20) DEFAULT 'Registered' CHECK (status IN ('Registered','Waitlisted','Dropped','Completed')),
    registered_at TIMESTAMP DEFAULT NOW()
);

-- ---------- 5. ASSESSMENT & RESULTS ----------
CREATE TABLE assessment_components (      -- CATs, quizzes, assignments, final exam
    id SERIAL PRIMARY KEY,
    course_registration_id INT REFERENCES course_registrations(id) ON DELETE CASCADE,
    component_type VARCHAR(30) NOT NULL,  -- 'CAT1','CAT2','Assignment','Exam'
    max_score NUMERIC(5,2) NOT NULL,
    score NUMERIC(5,2),
    weight_percent NUMERIC(5,2) NOT NULL,
    entered_by INT REFERENCES users(id),  -- faculty
    entered_at TIMESTAMP,
    approved_by_registrar BOOLEAN DEFAULT FALSE,
    released_to_student BOOLEAN DEFAULT FALSE
);

CREATE TABLE final_grades (
    id SERIAL PRIMARY KEY,
    course_registration_id INT UNIQUE REFERENCES course_registrations(id) ON DELETE CASCADE,
    total_score NUMERIC(5,2),
    letter_grade VARCHAR(2),
    grade_point NUMERIC(3,2),
    is_retake BOOLEAN DEFAULT FALSE,
    appeal_status VARCHAR(20) DEFAULT 'None' CHECK (appeal_status IN ('None','Requested','Under Review','Resolved'))
);

CREATE TABLE transcript_requests (
    id SERIAL PRIMARY KEY,
    student_id INT REFERENCES students(id),
    request_type VARCHAR(20) CHECK (request_type IN ('Unofficial','Official')),
    status VARCHAR(20) DEFAULT 'Pending' CHECK (status IN ('Pending','Approved','Issued','Rejected')),
    requested_at TIMESTAMP DEFAULT NOW(),
    issued_at TIMESTAMP,
    approved_by INT REFERENCES users(id)  -- registrar sign-off
);

-- ---------- 6. FEES / LEVIES / PAYMENTS (Ghana structure) ----------
CREATE TABLE fee_items (
    -- Configurable per institution/year — mirrors GTEC-approved itemized levies
    id SERIAL PRIMARY KEY,
    academic_year VARCHAR(9) NOT NULL,
    programme_level VARCHAR(20),           -- fees can differ by level
    name VARCHAR(100) NOT NULL,            -- 'Academic Facility User Fee','SRC Dues','GRASAG Development Levy', etc.
    amount NUMERIC(10,2) NOT NULL,
    is_mandatory BOOLEAN DEFAULT TRUE,
    opt_out_eligible BOOLEAN DEFAULT FALSE,  -- per GTEC guidance on levy opt-outs
    one_time_only BOOLEAN DEFAULT FALSE,     -- e.g. an anniversary levy for one year only
    gtec_approved BOOLEAN DEFAULT FALSE,
    active BOOLEAN DEFAULT TRUE
);

CREATE TABLE student_fee_invoices (
    id SERIAL PRIMARY KEY,
    student_id INT REFERENCES students(id),
    academic_year VARCHAR(9) NOT NULL,
    semester INT NOT NULL,
    total_amount NUMERIC(10,2) NOT NULL,
    amount_paid NUMERIC(10,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'Unpaid' CHECK (status IN ('Unpaid','Partially Paid','Paid','Overdue')),
    due_date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE invoice_line_items (
    id SERIAL PRIMARY KEY,
    invoice_id INT REFERENCES student_fee_invoices(id) ON DELETE CASCADE,
    fee_item_id INT REFERENCES fee_items(id),
    amount NUMERIC(10,2) NOT NULL,
    opted_out BOOLEAN DEFAULT FALSE
);

CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    invoice_id INT REFERENCES student_fee_invoices(id),
    amount NUMERIC(10,2) NOT NULL,
    payment_method VARCHAR(30),        -- 'Mobile Money','Card','Bank Transfer'
    provider_reference VARCHAR(100),   -- reference from payment gateway
    status VARCHAR(20) DEFAULT 'Pending' CHECK (status IN ('Pending','Successful','Failed','Refunded')),
    paid_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE payment_plans (
    id SERIAL PRIMARY KEY,
    invoice_id INT REFERENCES student_fee_invoices(id),
    installment_number INT NOT NULL,
    amount_due NUMERIC(10,2) NOT NULL,
    due_date DATE NOT NULL,
    paid BOOLEAN DEFAULT FALSE
);

CREATE TABLE scholarships_financial_aid (
    id SERIAL PRIMARY KEY,
    student_id INT REFERENCES students(id),
    aid_type VARCHAR(50),              -- 'Scholarship','Bursary','Loan','Fee Waiver'
    amount NUMERIC(10,2),
    coverage_percent NUMERIC(5,2),
    academic_year VARCHAR(9),
    status VARCHAR(20) DEFAULT 'Pending' CHECK (status IN ('Pending','Approved','Rejected','Disbursed'))
);

-- ---------- 7. FACULTY ----------
CREATE TABLE faculty_profiles (
    id SERIAL PRIMARY KEY,
    user_id INT UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    staff_id_number VARCHAR(30) UNIQUE NOT NULL,
    department_id INT REFERENCES departments(id),
    academic_rank VARCHAR(50),   -- Lecturer, Senior Lecturer, Associate Prof, Prof
    office_location VARCHAR(100),
    bio TEXT
);

CREATE TABLE course_assignments (      -- which lecturer teaches which course/semester
    id SERIAL PRIMARY KEY,
    faculty_id INT REFERENCES faculty_profiles(id),
    course_id INT REFERENCES courses(id),
    academic_year VARCHAR(9) NOT NULL,
    semester INT NOT NULL
);

CREATE TABLE office_hours (
    id SERIAL PRIMARY KEY,
    faculty_id INT REFERENCES faculty_profiles(id),
    day_of_week VARCHAR(10),
    start_time TIME,
    end_time TIME,
    location VARCHAR(100)
);

CREATE TABLE advising_appointments (
    id SERIAL PRIMARY KEY,
    student_id INT REFERENCES students(id),
    advisor_id INT REFERENCES users(id),
    scheduled_at TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'Scheduled' CHECK (status IN ('Scheduled','Completed','Cancelled')),
    notes TEXT
);

-- ---------- 8. RESEARCH ----------
CREATE TABLE research_publications (
    id SERIAL PRIMARY KEY,
    faculty_id INT REFERENCES faculty_profiles(id),
    title VARCHAR(500) NOT NULL,
    journal_or_venue VARCHAR(255),
    publication_year INT,
    doi_or_link TEXT
);

CREATE TABLE research_grants (
    id SERIAL PRIMARY KEY,
    faculty_id INT REFERENCES faculty_profiles(id),
    title VARCHAR(255),
    funder VARCHAR(255),
    amount NUMERIC(12,2),
    start_date DATE,
    end_date DATE
);

-- ---------- 9. STUDENT LIFE ----------
CREATE TABLE hostels (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    capacity INT,
    gender_type VARCHAR(20)
);

CREATE TABLE room_allocations (
    id SERIAL PRIMARY KEY,
    student_id INT REFERENCES students(id),
    hostel_id INT REFERENCES hostels(id),
    room_number VARCHAR(20),
    academic_year VARCHAR(9),
    status VARCHAR(20) DEFAULT 'Applied' CHECK (status IN ('Applied','Allocated','Checked In','Checked Out'))
);

CREATE TABLE clubs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150),
    description TEXT,
    patron_faculty_id INT REFERENCES faculty_profiles(id)
);

CREATE TABLE club_memberships (
    student_id INT REFERENCES students(id),
    club_id INT REFERENCES clubs(id),
    joined_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (student_id, club_id)
);

-- ---------- 10. LIBRARY ----------
CREATE TABLE library_items (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500),
    author VARCHAR(255),
    isbn VARCHAR(30),
    copies_total INT,
    copies_available INT,
    is_ebook BOOLEAN DEFAULT FALSE,
    ebook_url TEXT
);

CREATE TABLE library_loans (
    id SERIAL PRIMARY KEY,
    library_item_id INT REFERENCES library_items(id),
    student_id INT REFERENCES students(id),
    borrowed_at TIMESTAMP DEFAULT NOW(),
    due_date DATE,
    returned_at TIMESTAMP
);

-- ---------- 11. COURSE MATERIALS / LMS-LITE ----------
CREATE TABLE course_materials (
    id SERIAL PRIMARY KEY,
    course_assignment_id INT REFERENCES course_assignments(id) ON DELETE CASCADE,
    title VARCHAR(255),
    file_url TEXT,
    material_type VARCHAR(30),  -- 'Slide','Note','Recording','Reading'
    uploaded_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE assignments (
    id SERIAL PRIMARY KEY,
    course_assignment_id INT REFERENCES course_assignments(id) ON DELETE CASCADE,
    title VARCHAR(255),
    description TEXT,
    due_at TIMESTAMP,
    max_score NUMERIC(5,2)
);

CREATE TABLE assignment_submissions (
    id SERIAL PRIMARY KEY,
    assignment_id INT REFERENCES assignments(id) ON DELETE CASCADE,
    student_id INT REFERENCES students(id),
    file_url TEXT,
    submitted_at TIMESTAMP DEFAULT NOW(),
    score NUMERIC(5,2),
    feedback TEXT
);

CREATE TABLE discussion_posts (
    id SERIAL PRIMARY KEY,
    course_assignment_id INT REFERENCES course_assignments(id) ON DELETE CASCADE,
    author_user_id INT REFERENCES users(id),
    parent_post_id INT REFERENCES discussion_posts(id),
    content TEXT NOT NULL,
    posted_at TIMESTAMP DEFAULT NOW()
);

-- ---------- 12. NOTIFICATIONS / MESSAGING ----------
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255),
    body TEXT,
    channel VARCHAR(20) DEFAULT 'in_app' CHECK (channel IN ('in_app','email','sms')),
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    sender_id INT REFERENCES users(id),
    recipient_id INT REFERENCES users(id),
    subject VARCHAR(255),
    body TEXT,
    sent_at TIMESTAMP DEFAULT NOW(),
    read BOOLEAN DEFAULT FALSE
);

-- ---------- 13. SUPPORT / HELP DESK ----------
CREATE TABLE support_tickets (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    category VARCHAR(50),   -- 'IT','Registrar','Finance','Housing'
    subject VARCHAR(255),
    description TEXT,
    status VARCHAR(20) DEFAULT 'Open' CHECK (status IN ('Open','In Progress','Resolved','Closed')),
    assigned_to INT REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP
);

-- ---------- 14. CONTENT MANAGEMENT (public site) ----------
CREATE TABLE news_posts (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    author_id INT REFERENCES users(id),
    published BOOLEAN DEFAULT FALSE,
    published_at TIMESTAMP,
    cover_image_url TEXT
);

CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    location VARCHAR(255),
    start_time TIMESTAMP,
    end_time TIMESTAMP
);

CREATE TABLE staff_directory (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    title VARCHAR(100),
    department_id INT REFERENCES departments(id),
    office_location VARCHAR(100),
    public_email VARCHAR(255),
    photo_url TEXT
);

-- ---------- 15. AUDIT LOG (compliance) ----------
CREATE TABLE audit_log (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id INT,
    details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================
-- INDEXES for common lookups
-- ============================================================
CREATE INDEX idx_students_user ON students(user_id);
CREATE INDEX idx_courseregs_student ON course_registrations(student_id);
CREATE INDEX idx_invoices_student ON student_fee_invoices(student_id);
CREATE INDEX idx_applications_user ON applications(user_id);
CREATE INDEX idx_finalgrades_reg ON final_grades(course_registration_id);
