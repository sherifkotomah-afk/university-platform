import { Routes, Route } from 'react-router-dom'
import ProtectedRoute from './components/ProtectedRoute'

import Home from './pages/public/Home'
import Academics from './pages/public/Academics'
import Admissions from './pages/public/Admissions'
import News from './pages/public/News'
import NewsDetail from './pages/public/NewsDetail'
import Contact from './pages/public/Contact'

import Login from './pages/auth/Login'
import Register from './pages/auth/Register'

import ApplicantDashboard from './pages/applicant/ApplicantDashboard'
import ApplicationForm from './pages/applicant/ApplicationForm'
import ApplicationDetail from './pages/applicant/ApplicationDetail'

import StudentDashboard from './pages/student/StudentDashboard'
import StudentFees from './pages/student/StudentFees'
import StudentResults from './pages/student/StudentResults'
import StudentRegistration from './pages/student/StudentRegistration'

import FacultyDashboard from './pages/faculty/FacultyDashboard'
import FacultyCourseManage from './pages/faculty/FacultyCourseManage'

import AdminDashboard from './pages/admin/AdminDashboard'
import AdminApplications from './pages/admin/AdminApplications'
import AdminGrades from './pages/admin/AdminGrades'

export default function App() {
  return (
    <Routes>
      {/* Public site */}
      <Route path="/" element={<Home />} />
      <Route path="/academics" element={<Academics />} />
      <Route path="/admissions" element={<Admissions />} />
      <Route path="/news" element={<News />} />
      <Route path="/news/:id" element={<NewsDetail />} />
      <Route path="/contact" element={<Contact />} />

      {/* Auth */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Applicant portal */}
      <Route path="/applicant/dashboard" element={
        <ProtectedRoute allowedRoles={['applicant']}><ApplicantDashboard /></ProtectedRoute>
      } />
      <Route path="/applicant/apply" element={
        <ProtectedRoute allowedRoles={['applicant']}><ApplicationForm /></ProtectedRoute>
      } />
      <Route path="/applicant/applications/:id" element={
        <ProtectedRoute allowedRoles={['applicant']}><ApplicationDetail /></ProtectedRoute>
      } />

      {/* Student portal */}
      <Route path="/student/dashboard" element={
        <ProtectedRoute allowedRoles={['student']}><StudentDashboard /></ProtectedRoute>
      } />
      <Route path="/student/fees" element={
        <ProtectedRoute allowedRoles={['student']}><StudentFees /></ProtectedRoute>
      } />
      <Route path="/student/results" element={
        <ProtectedRoute allowedRoles={['student']}><StudentResults /></ProtectedRoute>
      } />
      <Route path="/student/registration" element={
        <ProtectedRoute allowedRoles={['student']}><StudentRegistration /></ProtectedRoute>
      } />

      {/* Faculty portal */}
      <Route path="/faculty/dashboard" element={
        <ProtectedRoute allowedRoles={['faculty']}><FacultyDashboard /></ProtectedRoute>
      } />
      <Route path="/faculty/courses/:id" element={
        <ProtectedRoute allowedRoles={['faculty']}><FacultyCourseManage /></ProtectedRoute>
      } />

      {/* Admin back office */}
      <Route path="/admin/dashboard" element={
        <ProtectedRoute allowedRoles={['admin', 'registrar', 'finance']}><AdminDashboard /></ProtectedRoute>
      } />
      <Route path="/admin/applications" element={
        <ProtectedRoute allowedRoles={['admin', 'registrar']}><AdminApplications /></ProtectedRoute>
      } />
      <Route path="/admin/grades" element={
        <ProtectedRoute allowedRoles={['admin', 'registrar']}><AdminGrades /></ProtectedRoute>
      } />

      <Route path="*" element={<Home />} />
    </Routes>
  )
}
