import { useState, useEffect } from 'react';
import {
  LayoutDashboard,
  Users,
  Briefcase,
  Activity,
  CheckCircle,
  Award,
  FileText,
  RefreshCw,
  Clock,
  ShieldAlert,
  TrendingDown,
  MessageSquare,
  AlertTriangle,
  Sun,
  Moon,
  Shield,
  ClipboardList,
  LogOut
} from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_URL || 
  (window.location.port === '5173'
    ? `${window.location.protocol}//${window.location.hostname}:8000`
    : window.location.origin);

const DASHBOARD_TRANSLATIONS = {
  uz: {
    title: "PDP University Karyera Markazi",
    subtitle: "Karyera Markazi",
    overview: "Boshqaruv paneli",
    studentMap: "Talabalar xaritasi",
    vacancyMatch: "Vakansiya saralovchi",
    deficitAnalyzer: "O'quv rejasi tahlilchisi",
    telemetrySafety: "Telemetriya va xavfsizlik",
    staffAllowlist: "Xodimlar ro'yxati",
    auditLogs: "Audit jurnali",
    systemStatus: "Tizim holati",
    live: "Faol",
    syncData: "Sinxronlash",
    light: "Yorug'lik",
    dark: "Qorong'ulik",
    welcomeTitle: "Campus Career Copilot",
    welcomeSubtitle: "Staff Dashboard",
    welcomeDesc: "PDP University Career Center uchun AI boshqaruv paneli. Faqat ruxsat berilgan xodimlar kira oladi.",
    signInGoogle: "Google orqali kirish",
    or: "YOKI",
    sandboxMode: "demo rejimga kirish",
    demoLabel: "demo uchun:",
    demoLink: "demo rejim",
    staffLoginTitle: "Tizimga kirish (Xodimlar)",
    emailLabel: "Email pochta",
    passwordLabel: "Parol",
    loginButton: "Kirish",
    demoLoginButton: "Demo rejimga kirish",
    changePasswordTitle: "Yangi parol o'rnatish",
    changePasswordDesc: "Bu sizning birinchi kirishingiz. Xavfsizlik uchun vaqtinchalik parolingizni o'zgartiring.",
    newPasswordLabel: "Yangi parol",
    confirmPasswordLabel: "Parolni tasdiqlash",
    savePasswordButton: "Parolni saqlash va kirish",
    cancelButton: "Orqaga",
    recentTalent: "Yaqinda faol bo'lgan talabalar",
    recentTalentDesc: "Tasdiqlangan yutuqlarga ega eng yaxshi ishga tayyor talabalar",
    viewAll: "Barchasini ko'rish",
    tableName: "Ism",
    tableRole: "Maqsadli lavozim",
    tableSkills: "Tasdiqlangan ko'nikmalar",
    tableReadiness: "Tayyorlik darajasi",
    tableAction: "Harakat",
    tableDetails: "Batafsil",
    safetyCompliance: "AI Agent xavfsizligi va muvofiqligi",
    guardrailCompliance: "Xavfsizlik talablariga rioya etish darajasi",
    guardrailFailures: "Faollashgan himoya ogohlantirishlari",
    noGuardrailHits: "Hech qanday xavfsizlik ogohlantirishi qayd etilmadi.",
    sessionHealth: "Faol sessiyalar salomatligi",
    totalSessions: "Jami sessiyalar",
    tokensUsed: "Ishlatilgan LLM tokenlari",
    notSpecified: "Ko'rsatilmagan",
    noVerifiedSkills: "Tasdiqlangan ko'nikmalar yo'q",
    profileIncomplete: "Profil to'liq emas",
    totalStudents: "Jami talabalar",
    activeSeekers: "Faol ish qidiruvchilar",
    avgResponseTime: "O'rtacha AI tezligi",
    safetyFlags: "Xavfsizlik ogohlantirishlari",
    registeredViaBot: "Telegram bot orqali ro'yxatdan o'tganlar",
    hasTargetRole: "Maqsadli lavozimi aniqlanganlar",
    latencyDesc: "AI agentining o'rtacha javob berish tezligi",
    guardrailDesc: "Tizim tomonidan to'xtatilgan xavfli so'rovlar",
    marketTrends: "Mehnat bozori trendlari (Top ko'nikmalar)",
    marketTrendsDesc: "Hamkor vakansiyalarida eng ko'p talab qilinayotgan texnologiyalar"
  },
  en: {
    title: "PDP University Career Center",
    subtitle: "Career Center",
    overview: "Overview",
    studentMap: "Student Skill Map",
    vacancyMatch: "Vacancy Matchmaker",
    deficitAnalyzer: "Curriculum Deficit Analyzer",
    telemetrySafety: "Telemetry & Safety",
    staffAllowlist: "Staff Allowlist",
    auditLogs: "Audit Logs",
    systemStatus: "System Status",
    live: "Live",
    syncData: "Sync Data",
    light: "Light",
    dark: "Dark",
    welcomeTitle: "Campus Career Copilot",
    welcomeSubtitle: "Staff Dashboard",
    welcomeDesc: "AI Dashboard for PDP University Career Center. Only authorized staff members can sign in.",
    signInGoogle: "Sign in with Google",
    or: "OR",
    sandboxMode: "enter demo mode",
    demoLabel: "for demo:",
    demoLink: "demo mode",
    staffLoginTitle: "Staff Sign In",
    emailLabel: "Email Address",
    passwordLabel: "Password",
    loginButton: "Sign In",
    demoLoginButton: "Access Demo Mode",
    changePasswordTitle: "Set New Password",
    changePasswordDesc: "This is your first sign in. For security, please change your temporary password.",
    newPasswordLabel: "New Password",
    confirmPasswordLabel: "Confirm Password",
    savePasswordButton: "Save Password & Log In",
    cancelButton: "Cancel",
    recentTalent: "Recent Active Talent Profiles",
    recentTalentDesc: "Top job-ready students based on verified achievements",
    viewAll: "View All",
    tableName: "Name",
    tableRole: "Target Role",
    tableSkills: "Verified Skills",
    tableReadiness: "Readiness Score",
    tableAction: "Action",
    tableDetails: "Details",
    safetyCompliance: "Harness Safety Compliance",
    guardrailCompliance: "Guardrail Compliance Rate",
    guardrailFailures: "Guardrail Failures Count",
    noGuardrailHits: "No guardrail interventions recorded.",
    sessionHealth: "Active Session Health",
    totalSessions: "Total Sessions",
    tokensUsed: "LLM Tokens Used",
    notSpecified: "Not Specified",
    noVerifiedSkills: "No verified skills",
    profileIncomplete: "Profile Incomplete",
    totalStudents: "Registered Students",
    activeSeekers: "Active Seekers",
    avgResponseTime: "Avg Response Time",
    safetyFlags: "Safety Flags",
    registeredViaBot: "Registered via Telegram bot",
    hasTargetRole: "Profile has Target Role defined",
    latencyDesc: "Latency of Agent reasoning steps",
    guardrailDesc: "Guardrail events flagged by agent",
    marketTrends: "Labor Market Trends (Top Skills)",
    marketTrendsDesc: "Top technologies requested in partner vacancies"
  }
};

interface Profile {
  id: number;
  telegram_id: string;
  name: string;
  university?: string;
  faculty?: string;
  year?: string;
  target_role?: string;
  verified_skills: string[];
  unverified_skills: string[];
  readiness_score: number;
  lms_verification_status?: string;
  student_id?: string;
  phone_number?: string;
}

interface StudentSummary {
  id: number;
  telegram_id: string;
  name: string;
  university?: string;
  faculty?: string;
  year?: string;
  target_role?: string;
  verified_skills: string[];
  unverified_skills: string[];
  readiness_score: number;
  lms_verification_status?: string;
  student_id?: string;
  phone_number?: string;
}

interface StudentDetail {
  profile: Profile;
  assessments: any[];
  resumes: any[];
  quizzes: any[];
  interviews?: any[];
  recommended_vacancies?: any[];
}


interface Vacancy {
  id: string;
  title: string;
  company: string;
  location?: string;
  skills_required: string[];
  description?: string;
  salary?: string;
}

interface VacancyMatch {
  telegram_id: string;
  name: string;
  target_role: string;
  match_score: number;
  skills_matched: { name: string; verified: boolean }[];
  skills_missing: string[];
  readiness_score: number;
}

interface TelemetryData {
  latency_trend: { id: number; latency_sec: number; timestamp: string }[];
  token_trend: { id: number; input_tokens: number; output_tokens: number; timestamp: string }[];
  guardrail_stats: { [key: string]: number };
  retry_stats: { [key: string]: number };
  risk_logs: { id: number; telegram_id: string; category: string; description: string; severity: string; timestamp: string }[];
}

interface WeakArea {
  skill: string;
  missing_count: number;
}

function App() {
  const [user, setUser] = useState<any | null>(null);
  const [authLoading, setAuthLoading] = useState(true);
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [loginError, setLoginError] = useState('');
  const [mustChangePassword, setMustChangePassword] = useState(false);
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  
  const [activeTab, setActiveTab] = useState<'overview' | 'students' | 'vacancies' | 'weak-areas' | 'telemetry' | 'staff-mgmt' | 'audit-logs'>('overview');
  const [loading, setLoading] = useState(true);
  const [isDemoMode, setIsDemoMode] = useState(false);
  const [theme, setTheme] = useState<'dark' | 'light'>(
    (localStorage.getItem('theme') as 'dark' | 'light') || 'dark'
  );
  const [learningPlanText, setLearningPlanText] = useState<string | null>(null);
  const [dashboardLanguage, setDashboardLanguage] = useState<'uz' | 'en'>(
    (localStorage.getItem('dashboardLanguage') as 'uz' | 'en') || 'uz'
  );

  const dt = (key: string): string => {
    const section = (DASHBOARD_TRANSLATIONS as any)[dashboardLanguage];
    return section?.[key] || (DASHBOARD_TRANSLATIONS.uz as any)[key] || key;
  };

  // Allowlist & Auditing management states
  const [staffUsers, setStaffUsers] = useState<any[]>([]);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [auditLogsTotal, setAuditLogsTotal] = useState(0);
  const [auditLogsPage, setAuditLogsPage] = useState(1);
  const [auditLogsFilter, setAuditLogsFilter] = useState({
    actor_id: '',
    action: '',
    target_type: ''
  });

  useEffect(() => {
    localStorage.setItem('theme', theme);
    document.body.classList.toggle('light-theme', theme === 'light');
  }, [theme]);

  // Secure request wrapper with credentials & refresh support
  const apiFetch = async (url: string, options: RequestInit = {}) => {
    if (isDemoMode) {
      throw new Error("Cannot fetch in demo mode");
    }
    options.credentials = 'include';
    
    let res = await fetch(url, options);
    
    if (res.status === 401) {
      try {
        const refreshRes = await fetch(`${API_BASE_URL}/auth/refresh`, {
          method: 'POST',
          credentials: 'include',
        });
        if (refreshRes.ok) {
          const newUserData = await refreshRes.json();
          setUser(newUserData);
          res = await fetch(url, options);
        } else {
          setUser(null);
          throw new Error("Session expired");
        }
      } catch (err) {
        setUser(null);
        throw err;
      }
    }
    return res;
  };

  // Check user session
  const checkSession = async () => {
    setAuthLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/auth/me`, { credentials: 'include' });
      if (res.ok) {
        const userData = await res.json();
        setUser(userData);
        setIsDemoMode(false);
        await fetchData(false, userData);
      } else {
        const refreshRes = await fetch(`${API_BASE_URL}/auth/refresh`, {
          method: 'POST',
          credentials: 'include',
        });
        if (refreshRes.ok) {
          const userData = await refreshRes.json();
          setUser(userData);
          setIsDemoMode(false);
          await fetchData(false, userData);
        } else {
          setUser(null);
          setLoading(false);
        }
      }
    } catch (e) {
      console.warn("Session check failed, backend might be offline.", e);
      setLoading(false);
    } finally {
      setAuthLoading(false);
    }
  };

  useEffect(() => {
    checkSession();
  }, []);

  const handleEmailPasswordLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginError('');
    setLoading(true);
    
    // Secret backdoor to launch demo mode
    if (loginEmail.trim().toLowerCase() === 'demo@pdp.uz') {
      setIsDemoMode(true);
      setUser({
        id: 0,
        email: 'demo@pdp.uz',
        name: 'Demo Administrator',
        role: 'super_admin',
        department: 'career',
        avatar_url: null
      });
      loadMockData();
      setLoading(false);
      return;
    }
    
    try {
      const res = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: loginEmail,
          password: loginPassword,
        }),
      });
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: 'Noto\'g\'ri email yoki parol / Incorrect email or password' }));
        throw new Error(errorData.detail || 'Failed to login');
      }
      const userData = await res.json();
      if (userData.must_change_password) {
        setMustChangePassword(true);
        setLoginError('');
        return;
      }
      setUser(userData);
      setIsDemoMode(false);
      await fetchData(false, userData);
    } catch (err: any) {
      setLoginError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordChangeSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginError('');
    if (newPassword !== confirmPassword) {
      setLoginError(dashboardLanguage === 'uz' ? 'Parollar mos kelmadi / Passwords do not match' : 'Passwords do not match');
      return;
    }
    if (newPassword.length < 6) {
      setLoginError(dashboardLanguage === 'uz' ? 'Parol kamida 6 ta belgidan iborat bo\'lishi kerak / Password must be at least 6 characters' : 'Password must be at least 6 characters');
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/auth/change-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: loginEmail,
          old_password: loginPassword,
          new_password: newPassword,
        }),
      });
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: 'Parolni o\'zgartirish muvaffaqiyatsiz tugadi / Password change failed' }));
        throw new Error(errorData.detail || 'Password change failed');
      }
      const userData = await res.json();
      setUser(userData);
      setMustChangePassword(false);
      setNewPassword('');
      setConfirmPassword('');
      setIsDemoMode(false);
      await fetchData(false, userData);
    } catch (err: any) {
      setLoginError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    if (!isDemoMode) {
      try {
        await fetch(`${API_BASE_URL}/auth/logout`, {
          method: 'POST',
          credentials: 'include'
        });
      } catch (err) {
        console.error("Logout request failed", err);
      }
    }
    setUser(null);
    setStudents([]);
    setVacancies([]);
    setWeakAreas([]);
    setTelemetry({
      latency_trend: [],
      token_trend: [],
      guardrail_stats: {},
      retry_stats: {},
      risk_logs: []
    });
  };

  const handleMessageStudent = (profile: Profile) => {
    alert(`💬 Opening Telegram Chat\n\nRedirecting to chat session with ${profile.name} (@t.me/student_${profile.telegram_id})...`);
    window.open(`https://t.me/student_${profile.telegram_id}`, '_blank');
  };

  const handleScheduleMockInterview = async (profile: Profile) => {
    if (isDemoMode) {
      alert(`[Demo Mode] 📅 Mock Interview Scheduled!\n\nAn automated request has been sent to ${profile.name}'s Telegram Assistant to start a mock interview practice for the role of "${profile.target_role || 'Software Developer'}".`);
      return;
    }
    try {
      const res = await apiFetch(`${API_BASE_URL}/api/admin/students/${profile.telegram_id}/schedule-interview`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ role: profile.target_role })
      });
      if (res.ok) {
        alert(`📅 Mock Interview Scheduled!\n\nAn automated invitation was sent to ${profile.name}'s Telegram bot to start an interview simulation for the role of "${profile.target_role || 'Software Developer'}".`);
      } else {
        const errData = await res.json().catch(() => ({ detail: 'Unknown error' }));
        alert(`❌ Failed to schedule mock interview: ${errData.detail}`);
      }
    } catch (err: any) {
      alert(`❌ Error scheduling mock interview: ${err.message}`);
    }
  };

  const handleExportShortlist = (detail: StudentDetail) => {
    const p = detail.profile;
    const verified = p.verified_skills.join(', ') || 'None';
    const unverified = p.unverified_skills.join(', ') || 'None';
    const score = (p.readiness_score === 0 || p.readiness_score === null || p.readiness_score === undefined) ? 'Profile Incomplete' : `${p.readiness_score}%`;
    
    let content = `PDP UNIVERSITY CAREER CENTER - STUDENT DOSSIER\n`;
    content += `=========================================\n\n`;
    content += `Name: ${p.name}\n`;
    content += `Telegram ID: ${p.telegram_id}\n`;
    content += `Student ID: ${p.student_id || 'N/A'}\n`;
    content += `Phone Number: ${p.phone_number || 'N/A'}\n`;
    content += `LMS Status: ${p.lms_verification_status || 'pending'}\n`;
    content += `University: ${p.university || 'N/A'}\n`;
    content += `Faculty: ${p.faculty || 'N/A'}\n`;
    content += `Year: ${p.year || 'N/A'}\n`;
    content += `Target Role: ${p.target_role || 'General'}\n`;
    content += `Readiness Score: ${score}\n\n`;
    content += `Verified Skills: ${verified}\n`;
    content += `Self-declared Skills: ${unverified}\n\n`;
    
    if (detail.quizzes && detail.quizzes.length > 0) {
      content += `QUIZ ATTEMPTS:\n`;
      detail.quizzes.forEach(q => {
        content += `- [${q.timestamp}] ${q.topic}: Score ${q.score}/${q.total_questions}\n`;
      });
      content += `\n`;
    }
    
    if (detail.resumes && detail.resumes.length > 0) {
      content += `ATS RESUME REVIEWS:\n`;
      detail.resumes.forEach(r => {
        content += `- ${r.filename} (ATS Score: ${r.score}%)\n`;
        content += `  Feedback: ${r.feedback}\n`;
      });
      content += `\n`;
    }
    
    if (detail.interviews && detail.interviews.length > 0) {
      content += `STAR MOCK INTERVIEWS:\n`;
      detail.interviews.forEach(i => {
        content += `- [${i.timestamp}] ${i.topic} (STAR Score: ${i.score}/10)\n`;
        content += `  Situation: ${i.situation}\n`;
        content += `  Task: ${i.task}\n`;
        content += `  Action: ${i.action}\n`;
        content += `  Result: ${i.result}\n`;
      });
      content += `\n`;
    }
    
    const element = document.createElement("a");
    const file = new Blob([content], {type: 'text/plain'});
    element.href = URL.createObjectURL(file);
    element.download = `${p.name.replace(/\s+/g, '_')}_dossier.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const handleGenerateLearningPlan = (detail: StudentDetail) => {
    const role = detail.profile.target_role || 'Software Engineer';
    const currentSkills = new Set([...detail.profile.verified_skills, ...detail.profile.unverified_skills].map(s => s.toLowerCase().trim()));
    let gaps: string[] = [];
    
    if (detail.recommended_vacancies && detail.recommended_vacancies.length > 0) {
      const topVac = detail.recommended_vacancies[0];
      const req = topVac.skills_required || [];
      gaps = req.filter((s: string) => !currentSkills.has(s.toLowerCase().trim()));
    } else {
      if (role.toLowerCase().includes('python') || role.toLowerCase().includes('backend')) {
        const standard = ['Docker', 'FastAPI', 'CI/CD', 'Kubernetes', 'Redis'];
        gaps = standard.filter(s => !currentSkills.has(s.toLowerCase()));
      } else if (role.toLowerCase().includes('frontend') || role.toLowerCase().includes('react')) {
        const standard = ['TypeScript', 'Redux', 'Webpack', 'TailwindCSS'];
        gaps = standard.filter(s => !currentSkills.has(s.toLowerCase()));
      } else {
        const standard = ['Git', 'Docker', 'SQL', 'Algorithms'];
        gaps = standard.filter(s => !currentSkills.has(s.toLowerCase()));
      }
    }
    
    let plan = `🎯 CUSTOMIZED LEARNING PATHWAY\n`;
    plan += `Target Career Goal: ${role}\n\n`;
    if (gaps.length === 0) {
      plan += `✅ Outstanding! The student currently has all required core skills for this role. We recommend undertaking mock interviews and refining resume ATS keywords to land the job.`;
    } else {
      plan += `Based on active employer demands, the student has ${gaps.length} curriculum gaps. Here is the suggested learning plan:\n\n`;
      gaps.forEach((gap, idx) => {
        plan += `📍 Stage ${idx+1}: Learn ${gap}\n`;
        plan += `   - Recommended course: Advanced ${gap} Fundamentals\n`;
        plan += `   - Hackathon milestone: Build a small project utilizing ${gap} and pass the verification quiz on PDP Career Center.\n\n`;
      });
      plan += `⚡ Pass verification quizzes to earn "Verified Skill" badges and boost match rates!`;
    }
    setLearningPlanText(plan);
  };

  const getStudentGaps = () => {
    if (!studentDetail) return [];
    const p = studentDetail.profile;
    const currentSkills = new Set([...p.verified_skills, ...p.unverified_skills].map(s => s.toLowerCase().trim()));
    
    let targetSkills: string[] = [];
    if (studentDetail.recommended_vacancies && studentDetail.recommended_vacancies.length > 0) {
      const topVac = studentDetail.recommended_vacancies[0];
      targetSkills = topVac.skills_required || [];
    } else {
      const role = (p.target_role || '').toLowerCase();
      if (role.includes('python') || role.includes('backend')) {
        targetSkills = ['Python', 'SQL', 'FastAPI', 'Git', 'Docker'];
      } else if (role.includes('frontend') || role.includes('react')) {
        targetSkills = ['React', 'JavaScript', 'TypeScript', 'HTML/CSS'];
      } else if (role.includes('security')) {
        targetSkills = ['Linux', 'Network Security', 'Python', 'Cryptography'];
      } else if (role.includes('data')) {
        targetSkills = ['SQL', 'Python', 'Excel', 'Tableau'];
      }
    }
    
    return targetSkills.filter(s => !currentSkills.has(s.toLowerCase().trim()));
  };

  const handleVerifyStudent = async (studentId: number, status: 'verified' | 'rejected') => {
    if (isDemoMode) {
      setStudentDetail(prev => {
        if (!prev) return null;
        return {
          ...prev,
          profile: {
            ...prev.profile,
            lms_verification_status: status
          }
        };
      });
      setStudents(prev => prev.map(s => s.id === studentId ? { ...s, lms_verification_status: status } : s));
      alert(`[Demo Mode] Student verification status updated to: ${status}`);
      return;
    }

    try {
      const res = await apiFetch(`${API_BASE_URL}/api/admin/students/${studentId}/verify`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status })
      });
      if (res.ok) {
        setStudentDetail(prev => {
          if (!prev) return null;
          return {
            ...prev,
            profile: {
              ...prev.profile,
              lms_verification_status: status
            }
          };
        });
        setStudents(prev => prev.map(s => s.id === studentId ? { ...s, lms_verification_status: status } : s));
        alert(`Student verification status updated to: ${status}`);
      } else {
        const errData = await res.json();
        alert(`Failed to verify student: ${errData.detail || 'Error'}`);
      }
    } catch (err: any) {
      alert(`Error updating verification status: ${err.message}`);
    }
  };

  const fetchStaffList = async () => {
    try {
      const res = await apiFetch(`${API_BASE_URL}/api/admin/staff`);
      if (res.ok) {
        const data = await res.json();
        setStaffUsers(data);
      }
    } catch (err) {
      console.error("Error fetching staff list", err);
    }
  };

  const fetchAuditLogs = async (page = 1, filters = auditLogsFilter) => {
    try {
      const offset = (page - 1) * 20;
      let queryStr = `limit=20&offset=${offset}`;
      if (filters.actor_id) queryStr += `&actor_id=${encodeURIComponent(filters.actor_id)}`;
      if (filters.action) queryStr += `&action=${encodeURIComponent(filters.action)}`;
      if (filters.target_type) queryStr += `&target_type=${encodeURIComponent(filters.target_type)}`;

      const res = await apiFetch(`${API_BASE_URL}/api/admin/audit-logs?${queryStr}`);
      if (res.ok) {
        const data = await res.json();
        setAuditLogs(data.logs);
        setAuditLogsTotal(data.total);
      }
    } catch (err) {
      console.error("Error fetching audit logs", err);
    }
  };

  const handleAddStaff = async (email: string, name: string, role: string, department: string) => {
    if (isDemoMode) {
      const newStaff = {
        id: Date.now(),
        email,
        name,
        role,
        department,
        is_active: 1,
        created_at: new Date().toISOString(),
        last_login: null
      };
      setStaffUsers(prev => [...prev, newStaff]);
      alert(`[Demo Mode] Xodim muvaffaqiyatli qo'shildi! / Staff added successfully!\nVaqtinchalik parol / Temporary Password: demo_temp_pass`);
      return true;
    }
    try {
      const res = await apiFetch(`${API_BASE_URL}/api/admin/staff`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, name, role, department })
      });
      if (res.ok) {
        const data = await res.json();
        await fetchStaffList();
        alert(`Xodim muvaffaqiyatli qo'shildi! / Staff added successfully!\n\nVaqtinchalik parol / Temporary Password: ${data.temp_password}\n\nIltimos, ushbu parolni xodimga yetkazing. U birinchi marta kirganda parolni o'zgartirishi shart. / Please share this password with the staff member. They must change it upon first login.`);
        return true;
      } else {
        const errData = await res.json();
        alert(`Failed to add staff: ${errData.detail}`);
        return false;
      }
    } catch (err: any) {
      alert(`Error adding staff: ${err.message}`);
      return false;
    }
  };

  const handleUpdateStaff = async (id: number, updates: { role?: string; department?: string; is_active?: number }) => {
    if (isDemoMode) {
      setStaffUsers(prev => prev.map(s => s.id === id ? { ...s, ...updates } : s));
      return;
    }
    try {
      const res = await apiFetch(`${API_BASE_URL}/api/admin/staff/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      });
      if (res.ok) {
        await fetchStaffList();
      } else {
        const errData = await res.json();
        alert(`Failed to update staff: ${errData.detail}`);
      }
    } catch (err: any) {
      alert(`Error updating staff: ${err.message}`);
    }
  };

  const handleDeactivateStaff = async (id: number) => {
    const currentUser = user;
    if (currentUser && id === currentUser.id) {
      alert("Cannot deactivate yourself!");
      return;
    }
    if (!confirm("Are you sure you want to deactivate this staff user?")) {
      return;
    }
    if (isDemoMode) {
      setStaffUsers(prev => prev.map(s => s.id === id ? { ...s, is_active: 0 } : s));
      return;
    }
    try {
      const res = await apiFetch(`${API_BASE_URL}/api/admin/staff/${id}`, {
        method: 'DELETE'
      });
      if (res.ok) {
        await fetchStaffList();
      } else {
        const errData = await res.json();
        alert(`Failed to deactivate staff: ${errData.detail}`);
      }
    } catch (err: any) {
      alert(`Error deactivating staff: ${err.message}`);
    }
  };

  const [stats, setStats] = useState<any>({
    total_students: 0,
    active_seekers: 0,
    avg_latency_sec: 0,
    total_tokens_exchanged: 0,
    total_agent_turns: 0,
    active_sessions: 0,
    guardrail_hits: 0,
    critical_risks: 0
  });
  const [students, setStudents] = useState<StudentSummary[]>([]);
  const [vacancies, setVacancies] = useState<Vacancy[]>([]);
  const [selectedVacancyId, setSelectedVacancyId] = useState<string>('');
  const [vacancyMatches, setVacancyMatches] = useState<VacancyMatch[]>([]);
  const [weakAreas, setWeakAreas] = useState<WeakArea[]>([]);
  const [telemetry, setTelemetry] = useState<TelemetryData>({
    latency_trend: [],
    token_trend: [],
    guardrail_stats: {},
    retry_stats: {},
    risk_logs: []
  });

  // Filters for Student Map
  const [searchQuery, setSearchQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState('All');
  const [readinessFilter, setReadinessFilter] = useState('All');

  // Selected Student Modal
  const [selectedStudentId, setSelectedStudentId] = useState<string | null>(null);
  const [studentDetail, setStudentDetail] = useState<StudentDetail | null>(null);
  const [loadingDetail, setLoadingDetail] = useState(false);

  // Load Initial Data
  const fetchData = async (forceDemo = false, loggedInUser = null) => {
    setLoading(true);
    const activeUser = loggedInUser || user;
    try {
      if (forceDemo) {
        throw new Error('Forced Demo Mode');
      }

      // 1. Stats
      const statsRes = await apiFetch(`${API_BASE_URL}/api/stats`);
      if (!statsRes.ok) throw new Error('API server error');
      const statsData = await statsRes.json();
      setStats(statsData);

      // 2. Students
      const studentsRes = await apiFetch(`${API_BASE_URL}/api/students`);
      const studentsData = await studentsRes.json();
      setStudents(studentsData);

      // 3. Vacancies
      const vacanciesRes = await apiFetch(`${API_BASE_URL}/api/vacancies`);
      const vacanciesData = await vacanciesRes.json();
      setVacancies(vacanciesData);
      if (vacanciesData.length > 0) {
        setSelectedVacancyId(vacanciesData[0].id);
      }

      // 4. Weak Areas
      if (activeUser && ['super_admin', 'career_staff'].includes(activeUser.role)) {
        const weakAreasRes = await apiFetch(`${API_BASE_URL}/api/analytics/weak-areas`);
        const weakAreasData = await weakAreasRes.json();
        setWeakAreas(weakAreasData);
      }

      // 5. Telemetry (super_admin only)
      if (activeUser && activeUser.role === 'super_admin') {
        const telemetryRes = await apiFetch(`${API_BASE_URL}/api/telemetry`);
        const telemetryData = await telemetryRes.json();
        setTelemetry(telemetryData);
        
        await fetchStaffList();
        await fetchAuditLogs(1);
      }

      setIsDemoMode(false);
    } catch (err) {
      console.warn('Backend API connection failed. Reverting to Mock Demo Mode.', err);
      // Wait, let's only auto-trigger demo mode if the user explicitly clicked sandbox,
      // or if we have a connection drop while already logged in/active.
      if (forceDemo || activeUser) {
        setIsDemoMode(true);
        loadMockData();
      }
    } finally {
      setLoading(false);
    }
  };



  // Fetch Vacancy matches when selected vacancy changes
  useEffect(() => {
    if (!selectedVacancyId) return;

    if (isDemoMode) {
      // Mock matching logic
      const selectedVac = mockVacancies.find(v => v.id === selectedVacancyId);
      if (selectedVac) {
        const matches = mockStudents.map(student => {
          const reqSkills = selectedVac.skills_required.map(s => s.toLowerCase().trim());
          const studSkills = [...student.verified_skills, ...student.unverified_skills].map(s => s.toLowerCase().trim());
          const overlap = studSkills.filter(s => reqSkills.includes(s));
          
          let score = 0;
          if (reqSkills.length > 0) {
            score += (overlap.length / reqSkills.length) * 60;
          }
          if (student.target_role && selectedVac.title.toLowerCase().includes(student.target_role.toLowerCase())) {
            score += 30;
          }
          if (selectedVac.title.toLowerCase().includes('junior') || selectedVac.title.toLowerCase().includes('intern')) {
            score += 10;
          }
          score = Math.min(100, Math.round(score));

          const skills_matched = selectedVac.skills_required.map(skill => {
            const hasIt = studSkills.includes(skill.toLowerCase().trim());
            const verified = student.verified_skills.map(s => s.toLowerCase().trim()).includes(skill.toLowerCase().trim());
            return { name: skill, verified: hasIt && verified, matched: hasIt };
          }).filter(s => s.matched);

          const skills_missing = selectedVac.skills_required.filter(skill => 
            !studSkills.includes(skill.toLowerCase().trim())
          );

          return {
            telegram_id: student.telegram_id,
            name: student.name,
            target_role: student.target_role || 'General',
            match_score: score,
            skills_matched,
            skills_missing,
            readiness_score: student.readiness_score
          };
        }).sort((a, b) => b.match_score - a.match_score);

        setVacancyMatches(matches);
      }
    } else {
      // API call
      fetch(`${API_BASE_URL}/api/vacancies/${selectedVacancyId}/matching-students`)
        .then(res => res.json())
        .then(data => {
          setVacancyMatches(data.matches);
        })
        .catch(err => console.error('Error fetching vacancy matches', err));
    }
  }, [selectedVacancyId, isDemoMode]);

  // Fetch Student Detail
  const handleViewStudentDetail = async (id: string) => {
    setSelectedStudentId(id);
    setLoadingDetail(true);
    try {
      if (isDemoMode) {
        // mock detail lookup
        const profile = mockStudents.find(s => s.telegram_id === id);
        if (profile) {
          const studentVacancies = mockVacancies.map(vacancy => {
            const reqSkills = vacancy.skills_required.map(s => s.toLowerCase().trim());
            const studSkills = [...profile.verified_skills, ...profile.unverified_skills].map(s => s.toLowerCase().trim());
            const overlap = studSkills.filter(s => reqSkills.includes(s));
            
            let score = 0;
            if (reqSkills.length > 0) {
              score += (overlap.length / reqSkills.length) * 60;
            }
            if (profile.target_role && vacancy.title.toLowerCase().includes(profile.target_role.toLowerCase())) {
              score += 30;
            }
            if (vacancy.title.toLowerCase().includes('junior') || vacancy.title.toLowerCase().includes('intern')) {
              score += 10;
            }
            score = Math.min(100, Math.round(score));
            return {
              ...vacancy,
              match_score: score,
              skills_matched: overlap.length,
              skills_total: reqSkills.length
            };
          }).sort((a, b) => b.match_score - a.match_score);

          const detail: StudentDetail = {
            profile,
            assessments: mockAssessments.filter(a => String(a.telegram_id) === id),
            resumes: mockResumes.filter(r => String(r.telegram_id) === id),
            quizzes: mockQuizzes.filter(q => String(q.telegram_id) === id),
            interviews: mockInterviews.filter(i => String(i.telegram_id) === id),
            recommended_vacancies: studentVacancies
          };
          setStudentDetail(detail);
        }
      } else {
        const res = await fetch(`${API_BASE_URL}/api/students/${id}`);
        if (!res.ok) throw new Error('Failed to load detail');
        const data = await res.json();
        setStudentDetail(data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingDetail(false);
    }
  };

  // Mock / Demo Data Generator
  const loadMockData = () => {
    setStats({
      total_students: mockStudents.length,
      active_seekers: mockStudents.filter(s => s.target_role).length,
      avg_latency_sec: 1.42,
      total_tokens_exchanged: 124500,
      total_agent_turns: 488,
      active_sessions: 12,
      guardrail_hits: 14,
      critical_risks: 2
    });
    setStudents(mockStudents);
    setVacancies(mockVacancies);
    setSelectedVacancyId(mockVacancies[0].id);
    setWeakAreas(mockWeakAreas);
    setTelemetry(mockTelemetry);
  };

  const getReadinessColor = (score: number | null | undefined) => {
    if (score === 0 || score === null || score === undefined) return 'badge-neutral';
    if (score >= 80) return 'badge-success';
    if (score >= 50) return 'badge-warning';
    return 'badge-danger';
  };


  const getSeverityBadge = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical': return 'badge-danger';
      case 'high': return 'badge-warning';
      case 'medium': return 'badge-primary';
      default: return 'badge-success';
    }
  };

  // Filtered Students
  const filteredStudents = students.filter(student => {
    const matchesSearch = student.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
                          (student.target_role || '').toLowerCase().includes(searchQuery.toLowerCase()) ||
                          (student.university || '').toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesRole = roleFilter === 'All' || student.target_role === roleFilter;

    let matchesReadiness = true;
    if (readinessFilter === 'High') {
      matchesReadiness = student.readiness_score >= 80;
    } else if (readinessFilter === 'Medium') {
      matchesReadiness = student.readiness_score >= 50 && student.readiness_score < 80;
    } else if (readinessFilter === 'Low') {
      matchesReadiness = student.readiness_score < 50;
    }

    return matchesSearch && matchesRole && matchesReadiness;
  });

  const uniqueRoles = Array.from(new Set(students.map(s => s.target_role).filter(Boolean)));

  if (authLoading) {
    return (
      <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', height: '100vh', width: '100vw', backgroundColor: 'var(--bg-main)' }}>
        <div className="spinner" style={{ marginBottom: '16px' }}></div>
        <p style={{ color: 'var(--text-muted)', fontFamily: 'var(--font-display)', fontSize: '16px' }}>
          {dashboardLanguage === 'uz' ? 'Xavfsiz sessiya tekshirilmoqda...' : 'Checking secure session...'}
        </p>
      </div>
    );
  }

  if (!user) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        width: '100vw',
        backgroundColor: 'var(--bg-main)',
        backgroundImage: 'radial-gradient(circle at top right, rgba(16, 185, 129, 0.08), transparent 400px), radial-gradient(circle at bottom left, rgba(16, 185, 129, 0.05), transparent 400px)',
        fontFamily: 'var(--font-sans)',
        padding: '20px',
        position: 'relative'
      }}>
        {/* Global Language Toggle Switch on Login Screen - Top Right */}
        <div style={{ position: 'absolute', top: '24px', right: '24px', display: 'flex', gap: '8px', zIndex: 10 }}>
          <button 
            onClick={() => { setDashboardLanguage('uz'); localStorage.setItem('dashboardLanguage', 'uz'); }} 
            className={`btn btn-outline ${dashboardLanguage === 'uz' ? 'btn-primary' : ''}`}
            style={{ padding: '6px 12px', fontSize: '12px', minWidth: '90px' }}
          >
            🇺🇿 O'zbekcha
          </button>
          <button 
            onClick={() => { setDashboardLanguage('en'); localStorage.setItem('dashboardLanguage', 'en'); }} 
            className={`btn btn-outline ${dashboardLanguage === 'en' ? 'btn-primary' : ''}`}
            style={{ padding: '6px 12px', fontSize: '12px', minWidth: '90px' }}
          >
            🇬🇧 English
          </button>
        </div>

        <div className="card" style={{
          maxWidth: '420px',
          width: '100%',
          padding: '28px 32px',
          textAlign: 'center',
          backdropFilter: 'blur(20px)',
          backgroundColor: 'var(--bg-card)',
          border: '1px solid var(--border-color)',
          boxShadow: 'var(--shadow-lg), var(--shadow-glow)',
          borderRadius: 'var(--radius-lg)'
        }}>
          <div style={{
            width: '56px',
            height: '56px',
            borderRadius: 'var(--radius-md)',
            backgroundColor: 'var(--primary-glow)',
            border: '2px solid var(--primary)',
            color: 'var(--primary)',
            fontSize: '20px',
            fontWeight: '800',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 16px auto',
            fontFamily: 'var(--font-display)',
            boxShadow: '0 0 15px rgba(16, 185, 129, 0.2)'
          }}>
            PDP
          </div>
          
          <h2 style={{
            fontFamily: 'var(--font-display)',
            fontSize: '24px',
            fontWeight: '700',
            color: 'var(--text-main)',
            margin: '0 0 4px 0',
            letterSpacing: '-0.02em'
          }}>
            {dt('welcomeTitle')}
          </h2>

          <h3 style={{
            fontFamily: 'var(--font-sans)',
            fontSize: '12px',
            fontWeight: '600',
            color: 'var(--primary)',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            margin: '0 0 16px 0'
          }}>
            {dt('welcomeSubtitle')}
          </h3>
          
          <p style={{
            fontSize: '14px',
            color: 'var(--text-muted)',
            margin: '0 0 20px 0',
            lineHeight: '1.5'
          }}>
            {dt('welcomeDesc')}
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            {mustChangePassword ? (
              <form onSubmit={handlePasswordChangeSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px', textAlign: 'left' }}>
                <h4 style={{
                  margin: '0 0 4px 0',
                  fontSize: '15px',
                  fontWeight: '600',
                  color: 'var(--text-main)',
                  fontFamily: 'var(--font-display)'
                }}>
                  {dt('changePasswordTitle')}
                </h4>

                <p style={{
                  fontSize: '13px',
                  color: 'var(--text-muted)',
                  margin: '0 0 6px 0',
                  lineHeight: '1.4'
                }}>
                  {dt('changePasswordDesc')}
                </p>

                {loginError && (
                  <div style={{
                    padding: '10px 12px',
                    borderRadius: 'var(--radius-sm)',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    border: '1px solid rgba(239, 68, 68, 0.2)',
                    color: '#ef4444',
                    fontSize: '13px',
                    lineHeight: '1.4'
                  }}>
                    {loginError}
                  </div>
                )}

                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  <label htmlFor="new-password-input" style={{ fontSize: '12px', fontWeight: '500', color: 'var(--text-muted)' }}>
                    {dt('newPasswordLabel')}
                  </label>
                  <input
                    id="new-password-input"
                    type="password"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    placeholder="••••••••"
                    required
                    style={{
                      padding: '10px 12px',
                      fontSize: '14px',
                      borderRadius: 'var(--radius-sm)',
                      border: '1px solid var(--border-color)',
                      backgroundColor: 'var(--card-bg)',
                      color: 'var(--text-main)',
                      fontFamily: 'var(--font-sans)',
                      outline: 'none',
                      transition: 'border-color 0.2s'
                    }}
                    onFocus={(e) => e.target.style.borderColor = 'var(--primary)'}
                    onBlur={(e) => e.target.style.borderColor = 'var(--border-color)'}
                  />
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  <label htmlFor="confirm-password-input" style={{ fontSize: '12px', fontWeight: '500', color: 'var(--text-muted)' }}>
                    {dt('confirmPasswordLabel')}
                  </label>
                  <input
                    id="confirm-password-input"
                    type="password"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="••••••••"
                    required
                    style={{
                      padding: '10px 12px',
                      fontSize: '14px',
                      borderRadius: 'var(--radius-sm)',
                      border: '1px solid var(--border-color)',
                      backgroundColor: 'var(--card-bg)',
                      color: 'var(--text-main)',
                      fontFamily: 'var(--font-sans)',
                      outline: 'none',
                      transition: 'border-color 0.2s'
                    }}
                    onFocus={(e) => e.target.style.borderColor = 'var(--primary)'}
                    onBlur={(e) => e.target.style.borderColor = 'var(--border-color)'}
                  />
                </div>

                <div style={{ display: 'flex', gap: '10px', marginTop: '6px' }}>
                  <button
                    type="button"
                    onClick={() => {
                      setMustChangePassword(false);
                      setNewPassword('');
                      setConfirmPassword('');
                      setLoginError('');
                    }}
                    style={{
                      flex: 1,
                      padding: '11px 16px',
                      fontSize: '14px',
                      fontWeight: '600',
                      borderRadius: 'var(--radius-sm)',
                      cursor: 'pointer',
                      backgroundColor: 'transparent',
                      border: '1px solid var(--border-color)',
                      color: 'var(--text-muted)',
                      transition: 'all 0.2s ease',
                      fontFamily: 'var(--font-sans)'
                    }}
                    onMouseOver={(e) => {
                      e.currentTarget.style.backgroundColor = 'var(--card-bg-hover)';
                      e.currentTarget.style.color = 'var(--text-main)';
                    }}
                    onMouseOut={(e) => {
                      e.currentTarget.style.backgroundColor = 'transparent';
                      e.currentTarget.style.color = 'var(--text-muted)';
                    }}
                  >
                    {dt('cancelButton')}
                  </button>
                  <button
                    type="submit"
                    disabled={loading}
                    style={{
                      flex: 2,
                      padding: '11px 16px',
                      fontSize: '14px',
                      fontWeight: '600',
                      borderRadius: 'var(--radius-sm)',
                      cursor: loading ? 'not-allowed' : 'pointer',
                      backgroundColor: 'var(--primary)',
                      border: 'none',
                      color: '#ffffff',
                      boxShadow: '0 1px 2px rgba(0,0,0,0.05)',
                      transition: 'all 0.2s ease',
                      fontFamily: 'var(--font-sans)'
                    }}
                    onMouseOver={(e) => {
                      if (!loading) e.currentTarget.style.filter = 'brightness(1.1)';
                    }}
                    onMouseOut={(e) => {
                      if (!loading) e.currentTarget.style.filter = 'none';
                    }}
                  >
                    {loading ? '...' : dt('savePasswordButton')}
                  </button>
                </div>
              </form>
            ) : (
              <form onSubmit={handleEmailPasswordLogin} style={{ display: 'flex', flexDirection: 'column', gap: '14px', textAlign: 'left' }}>
                <h4 style={{
                  margin: '0 0 4px 0',
                  fontSize: '14px',
                  fontWeight: '600',
                  color: 'var(--text-main)',
                  fontFamily: 'var(--font-sans)'
                }}>
                  {dt('staffLoginTitle')}
                </h4>

                {loginError && (
                  <div style={{
                    padding: '10px 12px',
                    borderRadius: 'var(--radius-sm)',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    border: '1px solid rgba(239, 68, 68, 0.2)',
                    color: '#ef4444',
                    fontSize: '13px',
                    lineHeight: '1.4'
                  }}>
                    {loginError}
                  </div>
                )}

                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  <label htmlFor="email-input" style={{ fontSize: '12px', fontWeight: '500', color: 'var(--text-muted)' }}>
                    {dt('emailLabel')}
                  </label>
                  <input
                    id="email-input"
                    type="email"
                    value={loginEmail}
                    onChange={(e) => setLoginEmail(e.target.value)}
                    placeholder="admin@pdp.uz"
                    required
                    style={{
                      padding: '10px 12px',
                      fontSize: '14px',
                      borderRadius: 'var(--radius-sm)',
                      border: '1px solid var(--border-color)',
                      backgroundColor: 'var(--card-bg)',
                      color: 'var(--text-main)',
                      fontFamily: 'var(--font-sans)',
                      outline: 'none',
                      transition: 'border-color 0.2s'
                    }}
                    onFocus={(e) => e.target.style.borderColor = 'var(--primary)'}
                    onBlur={(e) => e.target.style.borderColor = 'var(--border-color)'}
                  />
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  <label htmlFor="password-input" style={{ fontSize: '12px', fontWeight: '500', color: 'var(--text-muted)' }}>
                    {dt('passwordLabel')}
                  </label>
                  <input
                    id="password-input"
                    type="password"
                    value={loginPassword}
                    onChange={(e) => setLoginPassword(e.target.value)}
                    placeholder="••••••••"
                    required
                    style={{
                      padding: '10px 12px',
                      fontSize: '14px',
                      borderRadius: 'var(--radius-sm)',
                      border: '1px solid var(--border-color)',
                      backgroundColor: 'var(--card-bg)',
                      color: 'var(--text-main)',
                      fontFamily: 'var(--font-sans)',
                      outline: 'none',
                      transition: 'border-color 0.2s'
                    }}
                    onFocus={(e) => e.target.style.borderColor = 'var(--primary)'}
                    onBlur={(e) => e.target.style.borderColor = 'var(--border-color)'}
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  style={{
                    width: '100%',
                    padding: '11px 24px',
                    fontSize: '14px',
                    fontWeight: '600',
                    borderRadius: 'var(--radius-sm)',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    backgroundColor: 'var(--card-bg-hover)',
                    border: '1px solid var(--border-color)',
                    color: 'var(--text-main)',
                    boxShadow: '0 1px 2px rgba(0,0,0,0.05)',
                    transition: 'all 0.2s ease',
                    marginTop: '6px',
                    fontFamily: 'var(--font-sans)'
                  }}
                  onMouseOver={(e) => {
                    if (!loading) e.currentTarget.style.backgroundColor = 'var(--border-color)';
                  }}
                  onMouseOut={(e) => {
                    if (!loading) e.currentTarget.style.backgroundColor = 'var(--card-bg-hover)';
                  }}
                >
                  {loading ? '...' : dt('loginButton')}
                </button>
              </form>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Helper to extract top trending skills from vacancies
  const getTrendingSkills = () => {
    const counts: { [key: string]: number } = {};
    vacancies.forEach(v => {
      if (v.skills_required) {
        v.skills_required.forEach(skill => {
          const s = skill.trim();
          counts[s] = (counts[s] || 0) + 1;
        });
      }
    });
    return Object.entries(counts)
      .map(([skill, count]) => ({ skill, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 5);
  };

  return (
    <div className="app-container">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="logo-container">
          <div className="logo-icon">PDP</div>
          <div className="logo-text">
            <h1>PDP University</h1>
            <p>{dt('subtitle')}</p>
          </div>
        </div>

        <nav className="nav-links">
          <button 
            className={`nav-item ${activeTab === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveTab('overview')}
          >
            <LayoutDashboard size={18} />
            {dt('overview')}
          </button>
          {['super_admin', 'career_staff', 'viewer'].includes(user?.role) && (
            <button 
              className={`nav-item ${activeTab === 'students' ? 'active' : ''}`}
              onClick={() => setActiveTab('students')}
            >
              <Users size={18} />
              {dt('studentMap')}
            </button>
          )}
          {['super_admin', 'career_staff', 'viewer'].includes(user?.role) && (
            <button 
              className={`nav-item ${activeTab === 'vacancies' ? 'active' : ''}`}
              onClick={() => setActiveTab('vacancies')}
            >
              <Briefcase size={18} />
              {dt('vacancyMatch')}
            </button>
          )}
          {['super_admin', 'career_staff'].includes(user?.role) && (
            <button 
              className={`nav-item ${activeTab === 'weak-areas' ? 'active' : ''}`}
              onClick={() => setActiveTab('weak-areas')}
            >
              <TrendingDown size={18} />
              {dt('deficitAnalyzer')}
            </button>
          )}
          {user?.role === 'super_admin' && (
            <button 
              className={`nav-item ${activeTab === 'telemetry' ? 'active' : ''}`}
              onClick={() => setActiveTab('telemetry')}
            >
              <Activity size={18} />
              {dt('telemetrySafety')}
            </button>
          )}
          {user?.role === 'super_admin' && (
            <button 
              className={`nav-item ${activeTab === 'staff-mgmt' ? 'active' : ''}`}
              onClick={() => setActiveTab('staff-mgmt')}
            >
              <Shield size={18} />
              {dt('staffAllowlist')}
            </button>
          )}
          {user?.role === 'super_admin' && (
            <button 
              className={`nav-item ${activeTab === 'audit-logs' ? 'active' : ''}`}
              onClick={() => setActiveTab('audit-logs')}
            >
              <ClipboardList size={18} />
              {dt('auditLogs')}
            </button>
          )}
        </nav>

        <div className="sidebar-footer">
          {user && (
            <div className="user-profile-block" style={{ borderBottom: '1px solid var(--border-color)', paddingBottom: '12px', marginBottom: '12px' }}>
              <div style={{ display: 'flex', gap: '10px', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  backgroundColor: 'var(--primary)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 'bold',
                  color: 'white',
                  overflow: 'hidden',
                  flexShrink: 0
                }}>
                  {user.avatar_url ? (
                    <img src={user.avatar_url} alt={user.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                  ) : (
                    user.name.charAt(0).toUpperCase()
                  )}
                </div>
                <div style={{ flex: 1, minWidth: 0, paddingLeft: '4px' }}>
                  <h4 style={{ margin: 0, fontSize: '12px', fontWeight: 600, color: 'var(--text-main)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{user.name}</h4>
                  <span style={{ fontSize: '10px', color: 'var(--primary)', textTransform: 'uppercase', fontWeight: 600 }}>{user.role.replace('_', ' ')}</span>
                </div>
                <button 
                  onClick={handleLogout} 
                  className="btn btn-outline" 
                  style={{ padding: '4px 6px', minWidth: 'unset', color: 'var(--danger)', height: '28px', border: '1px solid var(--border-color)' }} 
                  title="Logout"
                >
                  <LogOut size={12} />
                </button>
              </div>
            </div>
          )}
          <div className="flex-between">
            <span>{dt('systemStatus')}</span>
            <span className="status-badge">
              <span className="pulse-dot"></span>
              {dt('live')}
            </span>
          </div>
          {isDemoMode ? (
            <div className="badge badge-warning" style={{ justifyContent: 'center', width: '100%', padding: '6px' }}>
              {dashboardLanguage === 'uz' ? '⚠️ Demo Rejim (API Offline)' : '⚠️ Demo Mode (API Offline)'}
            </div>
          ) : (
            <div className="badge badge-success" style={{ justifyContent: 'center', width: '100%', padding: '6px' }}>
              {dashboardLanguage === 'uz' ? 'API-ga ulandi' : 'Connected to API'}
            </div>
          )}
          <button 
            onClick={() => fetchData()} 
            className="btn btn-outline" 
            style={{ padding: '6px', fontSize: '11px', marginTop: '4px' }}
            disabled={loading}
          >
            <RefreshCw size={12} className={loading ? 'spin-animation' : ''} />
            {dt('syncData')}
          </button>
          
          <div className="theme-switch-container">
            <button 
              onClick={() => setTheme('light')} 
              className={`theme-switch-btn ${theme === 'light' ? 'active' : ''}`}
              title="Light Theme"
            >
              <Sun size={14} />
              <span>{dt('light')}</span>
            </button>
            <button 
              onClick={() => setTheme('dark')} 
              className={`theme-switch-btn ${theme === 'dark' ? 'active' : ''}`}
              title="Dark Theme"
            >
              <Moon size={14} />
              <span>{dt('dark')}</span>
            </button>
          </div>

          {/* Sidebar Language switcher */}
          <div className="theme-switch-container" style={{ marginTop: '4px' }}>
            <button 
              onClick={() => {
                setDashboardLanguage('uz');
                localStorage.setItem('dashboardLanguage', 'uz');
              }} 
              className={`theme-switch-btn ${dashboardLanguage === 'uz' ? 'active' : ''}`}
              title="O'zbek tili"
            >
              <span>UZB</span>
            </button>
            <button 
              onClick={() => {
                setDashboardLanguage('en');
                localStorage.setItem('dashboardLanguage', 'en');
              }} 
              className={`theme-switch-btn ${dashboardLanguage === 'en' ? 'active' : ''}`}
              title="English"
            >
              <span>ENG</span>
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="main-content">
        
        {/* Header */}
        <header className="page-header">
          <div className="header-title">
            <h2>
              {activeTab === 'overview' && dt('overview')}
              {activeTab === 'students' && dt('studentMap')}
              {activeTab === 'vacancies' && dt('vacancyMatch')}
              {activeTab === 'weak-areas' && dt('deficitAnalyzer')}
              {activeTab === 'telemetry' && dt('telemetrySafety')}
              {activeTab === 'staff-mgmt' && dt('staffAllowlist')}
              {activeTab === 'audit-logs' && dt('auditLogs')}
            </h2>
            <p>
              {activeTab === 'overview' && (dashboardLanguage === 'uz' ? 'Real vaqtdagi samaradorlik va karyerani rivojlantirish ko\'rsatkichlari.' : 'Real-time performance metrics and career development insights.')}
              {activeTab === 'students' && (dashboardLanguage === 'uz' ? 'Talabalarning tasdiqlangan ko\'nikmalari, maqsadlari va tayyorlik darajalarini kuzatish.' : 'Track student verified skills, target roles, and readiness scores.')}
              {activeTab === 'vacancies' && (dashboardLanguage === 'uz' ? 'Talabalar va hamkor vakansiyalari o\'rtasida sun\'iy intellektga asoslangan moslashtirish.' : 'Perform RAG-driven matches between student profiles and vacancies.')}
              {activeTab === 'weak-areas' && (dashboardLanguage === 'uz' ? 'Talaba profillaridan kelib chiqqan holda, o\'quv dasturidagi kamchiliklarni aniqlash.' : 'Identify critical skill gaps and curricular weakness areas.')}
              {activeTab === 'telemetry' && (dashboardLanguage === 'uz' ? 'Agent jurnallari, tezlik ko\'rsatkichlari va xavfsizlik holati.' : 'Verify agent security, guardrails compliance, and latency metrics.')}
              {activeTab === 'staff-mgmt' && (dashboardLanguage === 'uz' ? 'Tizimdan foydalanish huquqiga ega xodimlar va ularning rollarini boshqarish.' : 'Manage authorized staff emails, roles, and department access control.')}
              {activeTab === 'audit-logs' && (dashboardLanguage === 'uz' ? 'Tizimdagi barcha ma\'muriy harakatlar jurnali.' : 'View access and administrative action logs for compliance and security.')}
            </p>
          </div>
          <div className="flex-row-gap">
            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
              May 22, 2026
            </span>
          </div>
        </header>

        {loading ? (
          <div className="spinner"></div>
        ) : (
          <>
            {/* Overview / KPI Widgets */}
            <section className="metrics-grid">
              <div className="metric-card">
                <div className="metric-header">
                  <span className="metric-title">{dt('totalStudents')}</span>
                  <div className="metric-icon-wrapper"><Users size={16} /></div>
                </div>
                <h3 className="metric-value">{stats.total_students}</h3>
                <p className="metric-desc">{dt('registeredViaBot')}</p>
              </div>

              <div className="metric-card success-border">
                <div className="metric-header">
                  <span className="metric-title">{dt('activeSeekers')}</span>
                  <div className="metric-icon-wrapper"><Briefcase size={16} /></div>
                </div>
                <h3 className="metric-value">{stats.active_seekers}</h3>
                <p className="metric-desc">{dt('hasTargetRole')}</p>
              </div>

              <div className="metric-card warning-border">
                <div className="metric-header">
                  <span className="metric-title">{dt('avgResponseTime')}</span>
                  <div className="metric-icon-wrapper"><Clock size={16} /></div>
                </div>
                <h3 className="metric-value">{stats.avg_latency_sec}s</h3>
                <p className="metric-desc">{dt('latencyDesc')}</p>
              </div>

              <div className="metric-card danger-border">
                <div className="metric-header">
                  <span className="metric-title">{dt('safetyFlags')}</span>
                  <div className="metric-icon-wrapper"><ShieldAlert size={16} /></div>
                </div>
                <h3 className="metric-value">{stats.critical_risks}</h3>
                <p className="metric-desc">{dt('guardrailDesc')}</p>
              </div>
            </section>

            {/* TAB: OVERVIEW */}
            {activeTab === 'overview' && (
              <div className="dashboard-grid">
                {/* Left Side: Summary Lists */}
                <div className="card">
                  <div className="card-header">
                    <div>
                      <h3>{dt('recentTalent')}</h3>
                      <p>{dt('recentTalentDesc')}</p>
                    </div>
                    <button onClick={() => setActiveTab('students')} className="btn btn-outline" style={{ padding: '6px 12px', fontSize: '12px' }}>
                      {dt('viewAll')}
                    </button>
                  </div>
                  
                  <div className="table-wrapper">
                    <table className="custom-table">
                      <thead>
                        <tr>
                          <th>{dt('tableName')}</th>
                          <th>{dt('tableRole')}</th>
                          <th>{dt('tableSkills')}</th>
                          <th>{dt('tableReadiness')}</th>
                          <th>{dt('tableAction')}</th>
                        </tr>
                      </thead>
                      <tbody>
                        {students.slice(0, 5).map(student => (
                          <tr key={student.telegram_id}>
                            <td style={{ fontWeight: '600' }}>{student.name}</td>
                            <td>{student.target_role || <span style={{ color: 'var(--text-muted)' }}>{dt('notSpecified')}</span>}</td>
                            <td>
                              <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                                {student.verified_skills.slice(0, 2).map(skill => (
                                  <span key={skill} className="badge badge-accent">✅ {skill}</span>
                                ))}
                                {student.verified_skills.length > 2 && (
                                  <span className="badge badge-primary">+{student.verified_skills.length - 2}</span>
                                )}
                                {student.verified_skills.length === 0 && (
                                  <span style={{ color: 'var(--text-muted)', fontSize: '12px' }}>{dt('noVerifiedSkills')}</span>
                                )}
                              </div>
                            </td>
                            <td>
                              <span className={`badge ${getReadinessColor(student.readiness_score)}`}>
                                {(student.readiness_score === 0 || student.readiness_score === null || student.readiness_score === undefined) ? dt('profileIncomplete') : `${student.readiness_score}%`}
                              </span>
                            </td>
                            <td>
                              <button onClick={() => handleViewStudentDetail(student.telegram_id)} className="btn btn-outline" style={{ padding: '4px 8px', fontSize: '12px' }}>
                                {dt('tableDetails')}
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Right Side: Quick Security Health Check */}
                <div className="card">
                  <div className="card-header">
                    <div>
                      <h3>{dt('safetyCompliance')}</h3>
                      <p>{dashboardLanguage === 'uz' ? 'Xavfsizlik qoidalari va avtomatik tuzatishlar' : 'Guardrail actions & self-corrections'}</p>
                    </div>
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '12px', borderRadius: 'var(--radius-sm)', backgroundColor: 'var(--bg-main)' }}>
                      <div>
                        <div style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>{dt('guardrailCompliance')}</div>
                        <div style={{ fontSize: '24px', fontWeight: '800', color: 'var(--success)' }}>
                          {stats.total_agent_turns > 0 ? (Math.round((1 - (stats.guardrail_hits / stats.total_agent_turns)) * 100)) : 100}%
                        </div>
                      </div>
                      <div className="align-center" style={{ color: 'var(--success)' }}>
                        <CheckCircle size={24} />
                      </div>
                    </div>

                    <div>
                      <h4 style={{ margin: '0 0 10px 0', fontSize: '13px' }}>{dt('guardrailFailures')}</h4>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        {Object.entries(telemetry.guardrail_stats).map(([status, cnt]) => (
                          <div key={status} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                            <span style={{ color: 'var(--text-muted)' }}>{status}</span>
                            <span className="badge badge-danger">{cnt} {dashboardLanguage === 'uz' ? 'marta' : 'times'}</span>
                          </div>
                        ))}
                        {Object.keys(telemetry.guardrail_stats).length === 0 && (
                          <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>{dt('noGuardrailHits')}</div>
                        )}
                      </div>
                    </div>

                    <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '16px' }}>
                      <h4 style={{ margin: '0 0 10px 0', fontSize: '13px' }}>{dt('sessionHealth')}</h4>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                        <span style={{ color: 'var(--text-muted)' }}>{dt('totalSessions')}</span>
                        <span>{stats.active_sessions}</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginTop: '6px' }}>
                        <span style={{ color: 'var(--text-muted)' }}>{dt('tokensUsed')}</span>
                        <span>{stats.total_tokens_exchanged.toLocaleString()}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Third Card: Labor Market Trends Widget */}
                <div className="card" style={{ gridColumn: 'span 2' }}>
                  <div className="card-header">
                    <div>
                      <h3>{dt('marketTrends')}</h3>
                      <p>{dt('marketTrendsDesc')}</p>
                    </div>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px', alignItems: 'center' }}>
                    {/* Bar Chart */}
                    <div>
                      <div className="custom-bar-chart" style={{ height: '160px' }}>
                        {getTrendingSkills().map((item) => {
                          const maxVal = Math.max(...getTrendingSkills().map(s => s.count), 1);
                          const pct = (item.count / maxVal) * 80 + 10; // scale between 10% and 90%
                          return (
                            <div key={item.skill} className="bar-wrapper">
                              <div 
                                className="bar-column primary-bar" 
                                style={{ height: `${pct}%` }}
                                title={`${item.count} vacancies`}
                              ></div>
                              <span className="bar-label">{item.skill}</span>
                            </div>
                          );
                        })}
                        {getTrendingSkills().length === 0 && (
                          <div style={{ width: '100%', textAlign: 'center', color: 'var(--text-muted)' }}>
                            No active vacancy skill data.
                          </div>
                        )}
                      </div>
                    </div>
                    {/* Summary text list */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                      {getTrendingSkills().map((item, idx) => (
                        <div key={item.skill} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px' }}>
                          <span style={{ fontWeight: '600' }}>{idx + 1}. {item.skill}</span>
                          <span className="badge badge-accent">{item.count} {dashboardLanguage === 'uz' ? 'ta vakansiya' : 'vacancies'}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* TAB: STUDENT SKILL MAP */}
            {activeTab === 'students' && (
              <div className="card">
                <div className="card-header" style={{ borderBottom: 'none', paddingBottom: '0' }}>
                  <div>
                    <h3>{dt('talentPoolTitle')}</h3>
                    <p>{dt('talentPoolDesc')}</p>
                  </div>
                </div>

                {/* Filters Row */}
                <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', backgroundColor: 'var(--bg-main)', padding: '16px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
                  <div style={{ flexGrow: 1, minWidth: '200px' }}>
                    <div className="search-input-wrapper">
                      <input 
                        type="text" 
                        placeholder={dt('searchPlaceholder')}
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="form-input"
                      />
                    </div>
                  </div>
                  <div>
                    <select 
                      className="form-select"
                      value={roleFilter}
                      onChange={(e) => setRoleFilter(e.target.value)}
                    >
                      <option value="All">{dt('allRoles')}</option>
                      {uniqueRoles.map(role => (
                        <option key={role} value={role}>{role}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <select 
                      className="form-select"
                      value={readinessFilter}
                      onChange={(e) => setReadinessFilter(e.target.value)}
                    >
                      <option value="All">{dt('allReadiness')}</option>
                      <option value="High">{dt('highReadiness')}</option>
                      <option value="Medium">{dt('midReadiness')}</option>
                      <option value="Low">{dt('lowReadiness')}</option>
                    </select>
                  </div>
                </div>

                <div className="table-wrapper">
                  <table className="custom-table">
                    <thead>
                      <tr>
                        <th>{dt('tableName')}</th>
                        <th>{dashboardLanguage === 'uz' ? 'Universitet va Kurs' : 'University & Year'}</th>
                        <th>{dt('tableRole')}</th>
                        <th>{dashboardLanguage === 'uz' ? 'Tasdiqlangan ko\'nikmalar (LMS)' : 'Verified Skills (Quiz Passed)'}</th>
                        <th>{dashboardLanguage === 'uz' ? 'O\'zi kiritgan ko\'nikmalar' : 'Ready Skills (Self-declared)'}</th>
                        <th>{dt('tableReadiness')}</th>
                        <th>{dt('tableAction')}</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredStudents.map(student => (
                        <tr key={student.telegram_id}>
                          <td style={{ fontWeight: '600' }}>{student.name}</td>
                          <td>
                            <div>{student.university || 'N/A'}</div>
                            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                              {student.faculty} {student.year ? `• ${dashboardLanguage === 'uz' ? 'Kurs' : 'Year'} ${student.year}` : ''}
                            </div>
                          </td>
                          <td>{student.target_role || <span style={{ color: 'var(--text-muted)' }}>{dt('notSpecified')}</span>}</td>
                          <td>
                            <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                              {student.verified_skills.map(skill => (
                                <span key={skill} className="badge badge-accent">✅ {skill}</span>
                              ))}
                              {student.verified_skills.length === 0 && (
                                <span style={{ color: 'var(--text-muted)', fontSize: '12px' }}>-</span>
                              )}
                            </div>
                          </td>
                          <td>
                            <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                              {student.unverified_skills.map(skill => (
                                <span key={skill} className="badge badge-primary">{skill}</span>
                              ))}
                              {student.unverified_skills.length === 0 && (
                                <span style={{ color: 'var(--text-muted)', fontSize: '12px' }}>-</span>
                              )}
                            </div>
                          </td>
                          <td>
                            <span className={`badge ${getReadinessColor(student.readiness_score)}`}>
                              {(student.readiness_score === 0 || student.readiness_score === null || student.readiness_score === undefined) ? dt('profileIncomplete') : `${student.readiness_score}%`}
                            </span>
                          </td>
                          <td>
                            <button 
                              onClick={() => handleViewStudentDetail(student.telegram_id)} 
                              className="btn btn-outline" 
                              style={{ padding: '6px 12px', fontSize: '12px' }}
                            >
                              {dashboardLanguage === 'uz' ? 'Profilni ko\'rish' : 'Explore Profile'}
                            </button>
                          </td>
                        </tr>
                      ))}
                      {filteredStudents.length === 0 && (
                        <tr>
                          <td colSpan={7} style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
                            {dashboardLanguage === 'uz' ? 'Qidiruv mezonlariga mos keladigan talabalar topilmadi.' : 'No student profiles match your search criteria.'}
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* TAB: VACANCY MATCHMAKER */}
            {activeTab === 'vacancies' && (
              <div className="dashboard-grid">
                {/* Selector and Vacancy Details */}
                <div className="card">
                  <div className="card-header">
                    <div>
                      <h3>Active Vacancies List</h3>
                      <p>Select a vacancy to compute student qualification rankings</p>
                    </div>
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    <div>
                      <label style={{ display: 'block', marginBottom: '8px', fontSize: '13px', fontWeight: '600', color: 'var(--text-muted)' }}>
                        Select Target Vacancy
                      </label>
                      <select 
                        className="form-select" 
                        style={{ width: '100%' }}
                        value={selectedVacancyId}
                        onChange={(e) => setSelectedVacancyId(e.target.value)}
                      >
                        {vacancies.map(v => (
                          <option key={v.id} value={v.id}>{v.title} at {v.company}</option>
                        ))}
                      </select>
                    </div>

                    {(() => {
                      const selectedVac = vacancies.find(v => v.id === selectedVacancyId);
                      if (!selectedVac) return null;
                      return (
                        <div style={{ padding: '20px', borderRadius: 'var(--radius-md)', backgroundColor: 'var(--bg-main)', border: '1px solid var(--border-color)', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                            <div>
                              <h4 style={{ margin: '0', fontSize: '18px', fontWeight: '700' }}>{selectedVac.title}</h4>
                              <span style={{ fontSize: '14px', color: 'var(--primary)', fontWeight: '600' }}>{selectedVac.company}</span>
                            </div>
                            <span className="badge badge-primary">{selectedVac.location || 'Remote'}</span>
                          </div>
                          
                          {selectedVac.description && (
                            <p style={{ margin: '0', fontSize: '13px', color: 'var(--text-muted)', lineHeight: '1.5' }}>
                              {selectedVac.description}
                            </p>
                          )}

                          <div>
                            <span style={{ display: 'block', fontSize: '12px', color: 'var(--text-muted)', marginBottom: '6px', fontWeight: '600' }}>
                              Required Skills Checklist
                            </span>
                            <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                              {selectedVac.skills_required.map(skill => (
                                <span key={skill} className="badge badge-neutral">
                                  {skill}
                                </span>
                              ))}
                            </div>
                          </div>

                          {selectedVac.salary && (
                            <div style={{ fontSize: '13px', marginTop: '4px' }}>
                              <span style={{ color: 'var(--text-muted)' }}>Salary: </span>
                              <span style={{ fontWeight: '600', color: 'var(--success)' }}>{selectedVac.salary}</span>
                            </div>
                          )}
                        </div>
                      );
                    })()}
                  </div>
                </div>

                {/* Ranked Matches */}
                <div className="card">
                  <div className="card-header">
                    <div>
                      <h3>Top Ranked Matches</h3>
                      <p>Sorted by matchmaking similarity & verified credentials</p>
                    </div>
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    {vacancyMatches.map((match, idx) => (
                      <div 
                        key={match.telegram_id} 
                        style={{ padding: '16px', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)', backgroundColor: 'var(--bg-main)', transition: 'all 0.2s' }}
                      >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                          <div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                              <span style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: '800' }}>#{idx+1}</span>
                              <span style={{ fontWeight: '700', fontSize: '15px' }}>{match.name}</span>
                            </div>
                            <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{match.target_role}</span>
                          </div>
                          
                          <div style={{ textAlign: 'right' }}>
                            <span className="badge badge-success" style={{ fontSize: '14px', padding: '6px 12px', background: match.match_score >= 70 ? 'var(--success-glow)' : 'var(--warning-glow)', color: match.match_score >= 70 ? 'var(--success)' : 'var(--warning)' }}>
                              {match.match_score}% Match
                            </span>
                          </div>
                        </div>

                        {/* Match Progress Bar */}
                        <div style={{ width: '100%', height: '6px', backgroundColor: 'var(--border-color)', borderRadius: '999px', overflow: 'hidden', marginBottom: '12px' }}>
                          <div 
                            style={{ 
                              width: `${match.match_score}%`, 
                              height: '100%', 
                              background: `linear-gradient(90deg, var(--primary) 0%, ${match.match_score >= 70 ? 'var(--success)' : 'var(--warning)'} 100%)` 
                            }}
                          ></div>
                        </div>

                        {/* Matched & Missing list */}
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                          {match.skills_matched.length > 0 && (
                            <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap', alignItems: 'center' }}>
                              <span style={{ fontSize: '11px', color: 'var(--success)', fontWeight: '600', marginRight: '4px' }}>Possesses:</span>
                              {match.skills_matched.map(skill => (
                                <span key={skill.name} className={`badge ${skill.verified ? 'badge-accent' : 'badge-primary'}`} style={{ fontSize: '10px', padding: '2px 6px' }}>
                                  {skill.verified ? '✅ ' : ''}{skill.name}
                                </span>
                              ))}
                            </div>
                          )}

                          {match.skills_missing.length > 0 && (
                            <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap', alignItems: 'center' }}>
                              <span style={{ fontSize: '11px', color: 'var(--danger)', fontWeight: '600', marginRight: '4px' }}>Gaps:</span>
                              {match.skills_missing.map(skill => (
                                <span key={skill} className="badge badge-danger" style={{ fontSize: '10px', padding: '2px 6px' }}>
                                  {skill}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>

                        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '12px' }}>
                          <button onClick={() => handleViewStudentDetail(match.telegram_id)} className="btn btn-outline" style={{ padding: '4px 8px', fontSize: '11px' }}>
                            Open Dossier
                          </button>
                        </div>
                      </div>
                    ))}
                    {vacancyMatches.length === 0 && (
                      <div style={{ textAlign: 'center', padding: '30px', color: 'var(--text-muted)' }}>
                        No match scoring could be computed. Adjust vacancy criteria.
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* TAB: WEAK AREAS */}
            {activeTab === 'weak-areas' && (
              <div className="card" style={{ maxWidth: '800px', margin: '0 auto', width: '100%' }}>
                <div className="card-header">
                  <div>
                    <h3>Talent Deficit Analysis</h3>
                    <p>Aggregated missing skills based on student target roles vs active employer vacancies</p>
                  </div>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                  <div style={{ fontSize: '14px', color: 'var(--text-muted)', lineHeight: '1.6' }}>
                    The graph below aggregates vacancies matching the students' desired career outcomes. A skill is flagged as a 
                    <strong> deficit gap</strong> if it is required by the matching vacancy but is currently absent or unverified in the 
                    students' profiles. Use this report to adapt course modules and coordinate focused skill workshops.
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginTop: '16px' }}>
                    {weakAreas.map((item, idx) => {
                      const maxMissing = weakAreas.length > 0 ? Math.max(...weakAreas.map(w => w.missing_count)) : 10;
                      const percentage = maxMissing > 0 ? (item.missing_count / maxMissing) * 100 : 0;
                      
                      return (
                        <div key={item.skill} style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', fontWeight: '600' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                              <span style={{ color: 'var(--text-muted)', fontWeight: '800' }}>#{idx+1}</span>
                              <span>{item.skill}</span>
                            </div>
                            <span style={{ color: 'var(--danger)' }}>{item.missing_count} student gaps</span>
                          </div>
                          <div style={{ width: '100%', height: '18px', backgroundColor: 'var(--bg-main)', border: '1px solid var(--border-color)', borderRadius: '4px', overflow: 'hidden', display: 'flex' }}>
                            <div 
                              style={{ 
                                width: `${percentage}%`, 
                                height: '100%', 
                                background: 'linear-gradient(90deg, var(--warning) 0%, var(--danger) 100%)',
                                display: 'flex',
                                alignItems: 'center',
                                paddingLeft: '8px',
                                fontSize: '10px',
                                fontWeight: '800',
                                color: 'white'
                              }}
                            >
                              {percentage > 15 && `${Math.round(percentage)}% Impact`}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                    {weakAreas.length === 0 && (
                      <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
                        No curriculum deficits flagged. All active vacancies matches perfectly.
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* TAB: TELEMETRY */}
            {activeTab === 'telemetry' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                <div className="dashboard-grid">
                  {/* Latency and Token Usage */}
                  <div className="card">
                    <div className="card-header">
                      <div>
                        <h3>LLM Reasoning Latency Trend</h3>
                        <p>Latency in seconds of consecutive agent turn responses</p>
                      </div>
                    </div>

                    <div style={{ padding: '10px 0' }}>
                      {telemetry.latency_trend.length > 0 ? (
                        <div>
                          {/* SVG Line / Bar Representation */}
                          <div style={{ height: '180px', display: 'flex', alignItems: 'flex-end', gap: '4px', borderLeft: '1px solid var(--border-color)', borderBottom: '1px solid var(--border-color)', paddingBottom: '8px', paddingLeft: '8px' }}>
                            {telemetry.latency_trend.map((l) => {
                              const maxVal = Math.max(...telemetry.latency_trend.map(t => t.latency_sec), 3);
                              const heightPercentage = (l.latency_sec / maxVal) * 100;
                              return (
                                <div 
                                  key={l.id} 
                                  className="bar-column primary-bar"
                                  style={{ height: `${heightPercentage}%`, flexGrow: 1, minWidth: '4px' }}
                                  title={`Turn #${l.id}: ${l.latency_sec}s at ${l.timestamp}`}
                                ></div>
                              );
                            })}
                          </div>
                          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: 'var(--text-muted)', marginTop: '6px' }}>
                            <span>Older turns</span>
                            <span>Latest turn</span>
                          </div>
                        </div>
                      ) : (
                        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
                          No turn execution records found in database.
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Token Trend */}
                  <div className="card">
                    <div className="card-header">
                      <div>
                        <h3>Token Trend per Turn</h3>
                        <p>Stack of input (blue) vs output (purple) tokens</p>
                      </div>
                    </div>

                    <div style={{ padding: '10px 0' }}>
                      {telemetry.token_trend.length > 0 ? (
                        <div>
                          <div style={{ height: '180px', display: 'flex', alignItems: 'flex-end', gap: '4px', borderLeft: '1px solid var(--border-color)', borderBottom: '1px solid var(--border-color)', paddingBottom: '8px', paddingLeft: '8px' }}>
                            {telemetry.token_trend.map((t) => {
                              const maxToken = Math.max(...telemetry.token_trend.map(x => x.input_tokens + x.output_tokens), 2000);
                              const inputHeight = (t.input_tokens / maxToken) * 100;
                              const outputHeight = (t.output_tokens / maxToken) * 100;
                              return (
                                <div key={t.id} style={{ display: 'flex', flexDirection: 'column', flexGrow: 1, minWidth: '4px', height: '100%', justifyContent: 'flex-end' }} title={`Turn #${t.id}: In=${t.input_tokens}, Out=${t.output_tokens}`}>
                                  <div style={{ height: `${outputHeight}%`, width: '100%', backgroundColor: 'var(--accent)', borderRadius: '2px 2px 0 0' }}></div>
                                  <div style={{ height: `${inputHeight}%`, width: '100%', backgroundColor: 'var(--primary)' }}></div>
                                </div>
                              );
                            })}
                          </div>
                          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: 'var(--text-muted)', marginTop: '6px' }}>
                            <span>Older turns</span>
                            <span>Latest turn</span>
                          </div>
                        </div>
                      ) : (
                        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
                          No tokens history logs loaded.
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Self Correction retry and guardrails hits logs */}
                <div className="dashboard-grid">
                  <div className="card">
                    <div className="card-header">
                      <h3>Self-Correction Retry Distribution</h3>
                      <p>Number of retries required to satisfy formatting/schema constraints</p>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                      {Object.entries(telemetry.retry_stats).map(([label, count]) => {
                        const maxCount = Math.max(...Object.values(telemetry.retry_stats), 1);
                        const widthPct = (count / maxCount) * 100;
                        return (
                          <div key={label} style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                            <span style={{ fontSize: '13px', width: '100px', flexShrink: 0 }}>{label}</span>
                            <div style={{ flexGrow: 1, height: '16px', backgroundColor: 'var(--bg-main)', border: '1px solid var(--border-color)', borderRadius: '4px', overflow: 'hidden' }}>
                              <div style={{ width: `${widthPct}%`, height: '100%', backgroundColor: 'var(--primary)' }}></div>
                            </div>
                            <span style={{ fontSize: '13px', fontWeight: '700', width: '40px' }}>{count}</span>
                          </div>
                        );
                      })}
                      {Object.keys(telemetry.retry_stats).length === 0 && (
                        <div style={{ color: 'var(--text-muted)', fontSize: '13px', textAlign: 'center' }}>No retry logs compiled.</div>
                      )}
                    </div>
                  </div>

                  <div className="card">
                    <div className="card-header">
                      <h3>Recent Safety Flag & Guardrail Logs</h3>
                      <p>Guardrail interventions and prompt injection audits</p>
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', maxHeight: '250px', overflowY: 'auto', paddingRight: '4px' }}>
                      {telemetry.risk_logs.map(log => (
                        <div key={log.id} style={{ border: '1px solid var(--border-color)', borderRadius: 'var(--radius-sm)', padding: '10px', backgroundColor: 'var(--bg-main)' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                            <span style={{ fontSize: '11px', fontWeight: '800', color: 'var(--text-muted)' }}>
                              STUDENT ID: {log.telegram_id}
                            </span>
                            <span className={`badge ${getSeverityBadge(log.severity)}`}>
                              {log.severity.toUpperCase()}
                            </span>
                          </div>
                          <div style={{ fontSize: '12px', fontWeight: '600', color: 'var(--text-main)', marginBottom: '2px' }}>
                            Category: {log.category}
                          </div>
                          <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                            {log.description}
                          </div>
                          <div style={{ fontSize: '10px', color: 'var(--text-muted)', textAlign: 'right', marginTop: '4px' }}>
                            {log.timestamp}
                          </div>
                        </div>
                      ))}
                      {telemetry.risk_logs.length === 0 && (
                        <div style={{ color: 'var(--text-muted)', fontSize: '13px', textAlign: 'center', padding: '30px' }}>
                          No safety flags or guardrail events detected. Healthy system!
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* TAB: STAFF MANAGEMENT */}
            {activeTab === 'staff-mgmt' && user?.role === 'super_admin' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                {/* Add Staff form */}
                <div className="card">
                  <div className="card-header">
                    <h3>Add Staff Member to Allowlist</h3>
                    <p>Only emails on this allowlist will be permitted to authenticate. Newly created staff will get a temporary password shown in an alert.</p>
                  </div>
                  
                  <form onSubmit={async (e) => {
                    e.preventDefault();
                    const form = e.currentTarget;
                    const email = (form.elements.namedItem('email') as HTMLInputElement).value;
                    const name = (form.elements.namedItem('name') as HTMLInputElement).value;
                    const role = (form.elements.namedItem('role') as HTMLSelectElement).value;
                    const dept = (form.elements.namedItem('dept') as HTMLSelectElement).value;
                    
                    const success = await handleAddStaff(email, name, role, dept);
                    if (success) {
                      form.reset();
                    }
                  }} style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', alignItems: 'end' }}>
                    <div>
                      <label style={{ display: 'block', fontSize: '12px', color: 'var(--text-muted)', marginBottom: '6px' }}>Email Address</label>
                      <input type="email" name="email" required placeholder="name@domain.com" style={{ width: '100%', padding: '10px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)', backgroundColor: 'var(--bg-main)', color: 'var(--text-main)' }} />
                    </div>
                    <div>
                      <label style={{ display: 'block', fontSize: '12px', color: 'var(--text-muted)', marginBottom: '6px' }}>Name</label>
                      <input type="text" name="name" required placeholder="Full Name" style={{ width: '100%', padding: '10px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)', backgroundColor: 'var(--bg-main)', color: 'var(--text-main)' }} />
                    </div>
                    <div>
                      <label style={{ display: 'block', fontSize: '12px', color: 'var(--text-muted)', marginBottom: '6px' }}>Role</label>
                      <select name="role" style={{ width: '100%', padding: '10px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)', backgroundColor: 'var(--bg-main)', color: 'var(--text-main)' }}>
                        <option value="career_staff">Career Staff</option>
                        <option value="super_admin">Super Admin</option>
                        <option value="academic_staff">Academic Staff</option>
                        <option value="teacher">Teacher</option>
                        <option value="viewer">Viewer</option>
                      </select>
                    </div>
                    <div>
                      <label style={{ display: 'block', fontSize: '12px', color: 'var(--text-muted)', marginBottom: '6px' }}>Department</label>
                      <select name="dept" style={{ width: '100%', padding: '10px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)', backgroundColor: 'var(--bg-main)', color: 'var(--text-main)' }}>
                        <option value="career">Career Center</option>
                        <option value="academic">Academic Affairs</option>
                        <option value="teaching">Faculty/Teaching</option>
                        <option value="all">Cross-departmental</option>
                      </select>
                    </div>
                    <div>
                      <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: '10px' }}>
                        Add Staff
                      </button>
                    </div>
                  </form>
                </div>

                {/* Staff List Table */}
                <div className="card">
                  <div className="card-header">
                    <h3>Authorized Staff List</h3>
                    <p>View, update role/department, or deactivate allowlisted staff members.</p>
                  </div>
                  
                  <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                      <thead>
                        <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left' }}>
                          <th style={{ padding: '12px 8px', color: 'var(--text-muted)' }}>Name</th>
                          <th style={{ padding: '12px 8px', color: 'var(--text-muted)' }}>Email</th>
                          <th style={{ padding: '12px 8px', color: 'var(--text-muted)' }}>Role</th>
                          <th style={{ padding: '12px 8px', color: 'var(--text-muted)' }}>Department</th>
                          <th style={{ padding: '12px 8px', color: 'var(--text-muted)' }}>Status</th>
                          <th style={{ padding: '12px 8px', color: 'var(--text-muted)' }}>Last Login</th>
                          <th style={{ padding: '12px 8px', color: 'var(--text-muted)', textAlign: 'right' }}>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {staffUsers.map((s) => (
                          <tr key={s.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                            <td style={{ padding: '12px 8px', fontWeight: '600' }}>{s.name}</td>
                            <td style={{ padding: '12px 8px', color: 'var(--text-muted)' }}>{s.email}</td>
                            <td style={{ padding: '12px 8px' }}>
                              <select 
                                value={s.role} 
                                onChange={(e) => handleUpdateStaff(s.id, { role: e.target.value })}
                                style={{ padding: '4px 8px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)', backgroundColor: 'var(--bg-main)', color: 'var(--text-main)', fontSize: '12px' }}
                              >
                                <option value="super_admin">Super Admin</option>
                                <option value="career_staff">Career Staff</option>
                                <option value="academic_staff">Academic Staff</option>
                                <option value="teacher">Teacher</option>
                                <option value="viewer">Viewer</option>
                              </select>
                            </td>
                            <td style={{ padding: '12px 8px' }}>
                              <select 
                                value={s.department} 
                                onChange={(e) => handleUpdateStaff(s.id, { department: e.target.value })}
                                style={{ padding: '4px 8px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)', backgroundColor: 'var(--bg-main)', color: 'var(--text-main)', fontSize: '12px' }}
                              >
                                <option value="career">Career</option>
                                <option value="academic">Academic</option>
                                <option value="teaching">Teaching</option>
                                <option value="all">All</option>
                              </select>
                            </td>
                            <td style={{ padding: '12px 8px' }}>
                              <span className={`badge ${s.is_active ? 'badge-success' : 'badge-danger'}`}>
                                {s.is_active ? 'Active' : 'Inactive'}
                              </span>
                            </td>
                            <td style={{ padding: '12px 8px', color: 'var(--text-muted)' }}>
                              {s.last_login ? new Date(s.last_login).toLocaleString() : 'Never'}
                            </td>
                            <td style={{ padding: '12px 8px', textAlign: 'right' }}>
                              {s.is_active ? (
                                <button 
                                  onClick={() => handleDeactivateStaff(s.id)}
                                  className="btn btn-outline"
                                  style={{ padding: '4px 8px', fontSize: '11px', color: 'var(--danger)', borderColor: 'var(--danger-glow)' }}
                                >
                                  Deactivate
                                </button>
                              ) : (
                                <button 
                                  onClick={() => handleUpdateStaff(s.id, { is_active: 1 })}
                                  className="btn btn-outline"
                                  style={{ padding: '4px 8px', fontSize: '11px', color: 'var(--primary)', borderColor: 'var(--primary-glow)' }}
                                >
                                  Reactivate
                                </button>
                              )}
                            </td>
                          </tr>
                        ))}
                        {staffUsers.length === 0 && (
                          <tr>
                            <td colSpan={7} style={{ textAlign: 'center', padding: '24px', color: 'var(--text-muted)' }}>No staff registered.</td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}

            {/* TAB: AUDIT LOGS */}
            {activeTab === 'audit-logs' && user?.role === 'super_admin' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                {/* Search / Filter bar */}
                <div className="card">
                  <div className="card-header">
                    <h3>Filter Audit Logs</h3>
                    <p>Narrow down access history and configuration modifications.</p>
                  </div>
                  
                  <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', alignItems: 'end' }}>
                    <div style={{ flex: 1, minWidth: '150px' }}>
                      <label style={{ display: 'block', fontSize: '12px', color: 'var(--text-muted)', marginBottom: '6px' }}>Actor Email</label>
                      <input 
                        type="text" 
                        value={auditLogsFilter.actor_id} 
                        onChange={(e) => setAuditLogsFilter(prev => ({ ...prev, actor_id: e.target.value }))}
                        placeholder="Search actor..." 
                        style={{ width: '100%', padding: '10px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)', backgroundColor: 'var(--bg-main)', color: 'var(--text-main)' }} 
                      />
                    </div>
                    <div style={{ flex: 1, minWidth: '150px' }}>
                      <label style={{ display: 'block', fontSize: '12px', color: 'var(--text-muted)', marginBottom: '6px' }}>Action</label>
                      <input 
                        type="text" 
                        value={auditLogsFilter.action} 
                        onChange={(e) => setAuditLogsFilter(prev => ({ ...prev, action: e.target.value }))}
                        placeholder="e.g. login, verify_student" 
                        style={{ width: '100%', padding: '10px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)', backgroundColor: 'var(--bg-main)', color: 'var(--text-main)' }} 
                      />
                    </div>
                    <div style={{ flex: 1, minWidth: '150px' }}>
                      <label style={{ display: 'block', fontSize: '12px', color: 'var(--text-muted)', marginBottom: '6px' }}>Target Type</label>
                      <input 
                        type="text" 
                        value={auditLogsFilter.target_type} 
                        onChange={(e) => setAuditLogsFilter(prev => ({ ...prev, target_type: e.target.value }))}
                        placeholder="e.g. student, staff" 
                        style={{ width: '100%', padding: '10px', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)', backgroundColor: 'var(--bg-main)', color: 'var(--text-main)' }} 
                      />
                    </div>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button 
                        onClick={() => { setAuditLogsPage(1); fetchAuditLogs(1); }} 
                        className="btn btn-primary"
                        style={{ padding: '10px 20px' }}
                      >
                        Filter
                      </button>
                      <button 
                        onClick={() => {
                          const cleared = { actor_id: '', action: '', target_type: '' };
                          setAuditLogsFilter(cleared);
                          setAuditLogsPage(1);
                          fetchAuditLogs(1, cleared);
                        }} 
                        className="btn btn-outline"
                        style={{ padding: '10px 20px' }}
                      >
                        Reset
                      </button>
                    </div>
                  </div>
                </div>

                {/* Audit Logs Table */}
                <div className="card">
                  <div className="card-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <h3>Security Audit Trail</h3>
                      <p>Full operational history. Total records: {auditLogsTotal}</p>
                    </div>
                    <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                      Page {auditLogsPage} of {Math.ceil(auditLogsTotal / 20) || 1}
                    </span>
                  </div>
                  
                  <div style={{ overflowX: 'auto' }}>
                    <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px' }}>
                      <thead>
                        <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left' }}>
                          <th style={{ padding: '12px 8px', color: 'var(--text-muted)' }}>Timestamp</th>
                          <th style={{ padding: '12px 8px', color: 'var(--text-muted)' }}>Actor</th>
                          <th style={{ padding: '12px 8px', color: 'var(--text-muted)' }}>Action</th>
                          <th style={{ padding: '12px 8px', color: 'var(--text-muted)' }}>Target</th>
                          <th style={{ padding: '12px 8px', color: 'var(--text-muted)' }}>Details</th>
                          <th style={{ padding: '12px 8px', color: 'var(--text-muted)' }}>IP / Client</th>
                        </tr>
                      </thead>
                      <tbody>
                        {auditLogs.map((log) => (
                          <tr key={log.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                            <td style={{ padding: '12px 8px', whiteSpace: 'nowrap', color: 'var(--text-muted)' }}>
                              {new Date(log.timestamp).toLocaleString()}
                            </td>
                            <td style={{ padding: '12px 8px' }}>
                              <div style={{ fontWeight: '600' }}>{log.actor_name || 'System'}</div>
                              <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{log.actor_email || log.actor_id}</div>
                            </td>
                            <td style={{ padding: '12px 8px' }}>
                              <span className="badge badge-accent" style={{ textTransform: 'uppercase', fontSize: '10px' }}>
                                {log.action}
                              </span>
                            </td>
                            <td style={{ padding: '12px 8px' }}>
                              {log.target_type ? (
                                <div>
                                  <span style={{ fontWeight: '600' }}>{log.target_type}</span>
                                  {log.target_id && <span style={{ fontSize: '11px', color: 'var(--text-muted)', marginLeft: '4px' }}>({log.target_id})</span>}
                                </div>
                              ) : (
                                <span style={{ color: 'var(--text-muted)' }}>-</span>
                              )}
                            </td>
                            <td style={{ padding: '12px 8px', color: 'var(--text-muted)', maxWidth: '250px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={log.details}>
                              {log.details || '-'}
                            </td>
                            <td style={{ padding: '12px 8px', fontSize: '11px', color: 'var(--text-muted)' }}>
                              <div>{log.ip_address || 'unknown'}</div>
                              <div style={{ fontSize: '9px', maxWidth: '150px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={log.user_agent}>
                                {log.user_agent}
                              </div>
                            </td>
                          </tr>
                        ))}
                        {auditLogs.length === 0 && (
                          <tr>
                            <td colSpan={6} style={{ textAlign: 'center', padding: '24px', color: 'var(--text-muted)' }}>No audit logs matched.</td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>

                  {/* Pagination Controls */}
                  {auditLogsTotal > 20 && (
                    <div style={{ display: 'flex', justifyContent: 'center', gap: '8px', marginTop: '16px', padding: '8px' }}>
                      <button 
                        disabled={auditLogsPage <= 1}
                        onClick={() => {
                          const prevPage = auditLogsPage - 1;
                          setAuditLogsPage(prevPage);
                          fetchAuditLogs(prevPage);
                        }}
                        className="btn btn-outline"
                        style={{ padding: '6px 12px', fontSize: '12px' }}
                      >
                        Previous
                      </button>
                      <button 
                        disabled={auditLogsPage * 20 >= auditLogsTotal}
                        onClick={() => {
                          const nextPage = auditLogsPage + 1;
                          setAuditLogsPage(nextPage);
                          fetchAuditLogs(nextPage);
                        }}
                        className="btn btn-outline"
                        style={{ padding: '6px 12px', fontSize: '12px' }}
                      >
                        Next
                      </button>
                    </div>
                  )}
                </div>
              </div>
            )}
          </>
        )}
      </main>

      {/* DETAILED STUDENT POPUP MODAL */}
      {selectedStudentId && studentDetail && (
        <div style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', backgroundColor: 'rgba(0,0,0,0.7)', zIndex: 1000, display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '24px' }}>
          <div className="card" style={{ maxWidth: '900px', width: '100%', maxHeight: '90%', overflowY: 'auto', backgroundColor: 'var(--bg-card)', border: '1px solid var(--border-color)' }}>
            
            {/* Modal Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '1px solid var(--border-color)', paddingBottom: '16px' }}>
              <div>
                <h3 style={{ margin: 0, fontSize: '22px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  {studentDetail.profile.name}
                  <span className={`badge ${
                    studentDetail.profile.lms_verification_status === 'verified' ? 'badge-success' :
                    studentDetail.profile.lms_verification_status === 'rejected' ? 'badge-danger' : 'badge-warning'
                  }`} style={{ fontSize: '11px' }}>
                    LMS: {(studentDetail.profile.lms_verification_status || 'pending').toUpperCase()}
                  </span>
                </h3>
                <p style={{ margin: '4px 0 0 0', color: 'var(--text-muted)', fontSize: '13px' }}>
                  Telegram ID: {studentDetail.profile.telegram_id} | Student ID: {studentDetail.profile.student_id || 'Not Provided'} | Phone: {studentDetail.profile.phone_number || 'Not Provided'}
                </p>
                <p style={{ margin: '4px 0 0 0', color: 'var(--text-muted)', fontSize: '13px' }}>
                  University: {studentDetail.profile.university || 'PDP University'} ({studentDetail.profile.faculty || 'N/A'}, Year {studentDetail.profile.year || 'N/A'})
                </p>
              </div>
              <button 
                onClick={() => { setSelectedStudentId(null); setStudentDetail(null); setLearningPlanText(null); }}
                className="btn btn-outline"
                style={{ padding: '6px 12px', borderRadius: 'var(--radius-sm)' }}
              >
                Close View
              </button>
            </div>

            {/* Modal Body */}
            {loadingDetail ? (
              <div className="spinner"></div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', padding: '10px 0' }}>
                
                {/* Interactive Action Buttons Panel */}
                <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', borderBottom: '1px solid var(--border-color)', paddingBottom: '16px', alignItems: 'center', width: '100%' }}>
                  <button 
                    onClick={() => handleMessageStudent(studentDetail.profile)} 
                    className="btn btn-primary"
                    style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '8px 14px', fontSize: '13px' }}
                  >
                    💬 Message Student
                  </button>
                  <button 
                    onClick={() => handleExportShortlist(studentDetail)} 
                    className="btn btn-accent"
                    style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '8px 14px', fontSize: '13px' }}
                  >
                    📥 Export Shortlist
                  </button>
                  <button 
                    onClick={() => handleScheduleMockInterview(studentDetail.profile)} 
                    className="btn btn-outline"
                    style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '8px 14px', fontSize: '13px' }}
                  >
                    📅 Schedule Mock Interview
                  </button>
                  <button 
                    onClick={() => handleGenerateLearningPlan(studentDetail)} 
                    className="btn btn-outline"
                    style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '8px 14px', fontSize: '13px' }}
                  >
                    🎯 Generate Learning Plan
                  </button>

                  {/* LMS Verification Actions for authorized staff */}
                  {['super_admin', 'career_staff'].includes(user?.role) && (
                    <div style={{ display: 'flex', gap: '8px', marginLeft: 'auto', borderLeft: '1px solid var(--border-color)', paddingLeft: '16px' }}>
                      {studentDetail.profile.lms_verification_status !== 'verified' && (
                        <button
                          onClick={() => handleVerifyStudent(studentDetail.profile.id, 'verified')}
                          className="btn btn-success"
                          style={{ display: 'flex', alignItems: 'center', gap: '4px', padding: '8px 14px', fontSize: '13px', backgroundColor: 'var(--success)', color: '#fff' }}
                        >
                          ✓ Verify LMS Profile
                        </button>
                      )}
                      {studentDetail.profile.lms_verification_status !== 'rejected' && (
                        <button
                          onClick={() => handleVerifyStudent(studentDetail.profile.id, 'rejected')}
                          className="btn btn-danger"
                          style={{ display: 'flex', alignItems: 'center', gap: '4px', padding: '8px 14px', fontSize: '13px', backgroundColor: 'var(--danger)', color: '#fff' }}
                        >
                          ✕ Reject Profile
                        </button>
                      )}
                    </div>
                  )}
                </div>

                {/* Customized Learning Path Output */}
                {learningPlanText && (
                  <div style={{ backgroundColor: 'var(--bg-main)', padding: '16px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)', position: 'relative' }}>
                    <button 
                      onClick={() => setLearningPlanText(null)}
                      style={{ position: 'absolute', top: '10px', right: '10px', background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '16px' }}
                    >
                      ✕
                    </button>
                    <div style={{ fontSize: '13px', color: 'var(--text-main)', lineHeight: '1.6', whiteSpace: 'pre-wrap' }}>
                      {learningPlanText}
                    </div>
                  </div>
                )}

                {/* Meta details */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
                  <div style={{ backgroundColor: 'var(--bg-main)', padding: '16px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
                    <span style={{ display: 'block', fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Target Role</span>
                    <strong style={{ fontSize: '15px' }}>{studentDetail.profile.target_role || 'General'}</strong>
                  </div>
                  <div style={{ backgroundColor: 'var(--bg-main)', padding: '16px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
                    <span style={{ display: 'block', fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Readiness Score</span>
                    <span className={`badge ${getReadinessColor(studentDetail.profile.readiness_score)}`} style={{ fontSize: '14px', marginTop: '4px' }}>
                      {(studentDetail.profile.readiness_score === 0 || studentDetail.profile.readiness_score === null || studentDetail.profile.readiness_score === undefined) ? 'Profile Incomplete' : `${studentDetail.profile.readiness_score}% Readiness`}
                    </span>
                  </div>
                  <div style={{ backgroundColor: 'var(--bg-main)', padding: '16px', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-color)' }}>
                    <span style={{ display: 'block', fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Verified Skills</span>
                    <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap', marginTop: '6px' }}>
                      {studentDetail.profile.verified_skills.map(s => (
                        <span key={s} className="badge badge-accent" style={{ fontSize: '9px' }}>✅ {s}</span>
                      ))}
                      {studentDetail.profile.verified_skills.length === 0 && <span style={{ color: 'var(--text-muted)', fontSize: '12px' }}>None</span>}
                    </div>
                  </div>
                </div>

                {/* Core Columns: Left=Quizzes & Resumes, Right=Skills & Assessment logs */}
                <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '24px' }}>
                  
                  {/* Left Column */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                    {/* Skill Passport Quizzes */}
                    <div style={{ border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)', padding: '16px', backgroundColor: 'var(--bg-main)' }}>
                      <h4 style={{ margin: '0 0 12px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <Award size={16} className="text-primary" />
                        Skill Passport (Interactive Quiz Attempts)
                      </h4>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        {studentDetail.quizzes.map((quiz, i) => (
                          <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-sm)', backgroundColor: 'var(--bg-card)', fontSize: '13px' }}>
                            <div>
                              <strong style={{ color: 'var(--text-main)' }}>{quiz.topic}</strong>
                              <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{quiz.timestamp}</div>
                            </div>
                            <div className="align-center">
                              <span className={`badge ${quiz.score >= 70 ? 'badge-success' : 'badge-warning'}`}>
                                Score: {quiz.score}/{quiz.total_questions || 5}
                              </span>
                            </div>
                          </div>
                        ))}
                        {studentDetail.quizzes.length === 0 && (
                          <div style={{ color: 'var(--text-muted)', fontSize: '12px', padding: '10px 0' }}>
                            No quiz attempts recorded for this user.
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Resumes uploaded */}
                    <div style={{ border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)', padding: '16px', backgroundColor: 'var(--bg-main)' }}>
                      <h4 style={{ margin: '0 0 12px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <FileText size={16} className="text-primary" />
                        Uploaded Resumes & ATS Feedbacks
                      </h4>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                        {studentDetail.resumes.map((resume, i) => (
                          <div key={i} style={{ border: '1px solid var(--border-color)', borderRadius: 'var(--radius-sm)', padding: '12px', backgroundColor: 'var(--bg-card)', fontSize: '13px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                              <span style={{ fontWeight: '600' }}>{resume.filename || 'resume.pdf'}</span>
                              <span className="badge badge-primary">{resume.timestamp}</span>
                            </div>
                            
                            {resume.score !== undefined && (
                              <div style={{ marginBottom: '8px' }}>
                                <span style={{ color: 'var(--text-muted)' }}>ATS Score: </span>
                                <span style={{ fontWeight: '700', color: 'var(--primary)' }}>{resume.score}%</span>
                              </div>
                            )}

                            {resume.feedback && (
                              <div style={{ backgroundColor: 'var(--bg-main)', padding: '8px', borderRadius: '4px', border: '1px solid var(--border-color)', fontSize: '12px', whiteSpace: 'pre-wrap', color: 'var(--text-muted)', maxHeight: '120px', overflowY: 'auto' }}>
                                {resume.feedback}
                              </div>
                            )}
                          </div>
                        ))}
                        {studentDetail.resumes.length === 0 && (
                          <div style={{ color: 'var(--text-muted)', fontSize: '12px', padding: '10px 0' }}>
                            No resumes submitted for ATS Review.
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Right Column */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                    {/* General Skill List & Gaps */}
                    <div style={{ border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)', padding: '16px', backgroundColor: 'var(--bg-main)' }}>
                      <h4 style={{ margin: '0 0 12px 0' }}>Skills Declaration & Curriculum Gaps</h4>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        <div>
                          <span style={{ display: 'block', fontSize: '11px', color: 'var(--text-muted)', marginBottom: '6px' }}>Verified Skills (Passed Quiz)</span>
                          <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                            {studentDetail.profile.verified_skills.map(s => (
                              <span key={s} className="badge badge-accent">✅ {s}</span>
                            ))}
                            {studentDetail.profile.verified_skills.length === 0 && <span style={{ color: 'var(--text-muted)', fontSize: '12px' }}>No verified skills</span>}
                          </div>
                        </div>

                        <div>
                          <span style={{ display: 'block', fontSize: '11px', color: 'var(--text-muted)', marginBottom: '6px' }}>Self-declared Skills (Unverified)</span>
                          <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                            {studentDetail.profile.unverified_skills.map(s => (
                              <span key={s} className="badge badge-primary">{s}</span>
                            ))}
                            {studentDetail.profile.unverified_skills.length === 0 && <span style={{ color: 'var(--text-muted)', fontSize: '12px' }}>No self-declared skills</span>}
                          </div>
                        </div>

                        <div>
                          <span style={{ display: 'block', fontSize: '11px', color: 'var(--text-muted)', marginBottom: '6px' }}>Curriculum Deficit Gaps</span>
                          <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                            {getStudentGaps().map(s => (
                              <span key={s} className="badge" style={{ fontSize: '10px', backgroundColor: 'var(--danger-glow)', color: 'var(--danger)', border: '1px solid var(--danger)', display: 'inline-flex', alignItems: 'center', gap: '3px' }}>
                                <AlertTriangle size={10} /> {s}
                              </span>
                            ))}
                            {getStudentGaps().length === 0 && <span style={{ color: 'var(--success)', fontSize: '12px' }}>🎉 No gaps detected! Ready for target role.</span>}
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* STAR Mock Interview Attempts */}
                    <div style={{ border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)', padding: '16px', backgroundColor: 'var(--bg-main)' }}>
                      <h4 style={{ margin: '0 0 12px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <MessageSquare size={16} className="text-primary" />
                        STAR Mock Interview Attempts
                      </h4>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', maxHeight: '250px', overflowY: 'auto' }}>
                        {studentDetail.interviews && studentDetail.interviews.map((interview, i) => (
                          <div key={i} style={{ border: '1px solid var(--border-color)', borderRadius: 'var(--radius-sm)', padding: '10px', backgroundColor: 'var(--bg-card)', fontSize: '12px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                              <strong style={{ color: 'var(--text-main)' }}>{interview.topic}</strong>
                              <span className={`badge ${interview.score >= 8 ? 'badge-success' : 'badge-warning'}`}>
                                Score: {interview.score}/{interview.max_score || 10}
                              </span>
                            </div>
                            <div style={{ fontSize: '10px', color: 'var(--text-muted)', marginBottom: '6px' }}>{interview.timestamp}</div>
                            
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', backgroundColor: 'var(--bg-main)', padding: '8px', borderRadius: '4px', border: '1px solid var(--border-color)' }}>
                              <div><strong>Situation:</strong> <span style={{ color: 'var(--text-muted)' }}>{interview.situation}</span></div>
                              <div><strong>Task:</strong> <span style={{ color: 'var(--text-muted)' }}>{interview.task}</span></div>
                              <div><strong>Action:</strong> <span style={{ color: 'var(--text-muted)' }}>{interview.action}</span></div>
                              <div><strong>Result:</strong> <span style={{ color: 'var(--text-muted)' }}>{interview.result}</span></div>
                            </div>
                          </div>
                        ))}
                        {(!studentDetail.interviews || studentDetail.interviews.length === 0) && (
                          <div style={{ color: 'var(--text-muted)', fontSize: '12px', padding: '10px 0' }}>
                            No mock interview attempts recorded.
                          </div>
                        )}
                      </div>
                    </div>

                    {/* RAG Core Assessments (Weak areas & feedback) */}
                    <div style={{ border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)', padding: '16px', backgroundColor: 'var(--bg-main)' }}>
                      <h4 style={{ margin: '0 0 12px 0' }}>Agent Skill Assessments Logs</h4>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxHeight: '250px', overflowY: 'auto' }}>
                        {studentDetail.assessments.map((a, index) => (
                          <div key={index} style={{ border: '1px solid var(--border-color)', borderRadius: 'var(--radius-sm)', padding: '10px', backgroundColor: 'var(--bg-card)', fontSize: '12px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px', fontWeight: '600' }}>
                              <span>{a.topic || 'Skill Audit'}</span>
                              <span className="badge badge-primary">{a.timestamp || 'N/A'}</span>
                            </div>
                            <div style={{ color: 'var(--text-muted)', whiteSpace: 'pre-wrap' }}>
                              {a.assessment_text || a.feedback || JSON.stringify(a)}
                            </div>
                          </div>
                        ))}
                        {studentDetail.assessments.length === 0 && (
                          <div style={{ color: 'var(--text-muted)', fontSize: '12px', padding: '10px 0' }}>
                            No structured skill passport assessments generated yet.
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                </div>

                {/* Recommended Vacancies Panel */}
                <div style={{ border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)', padding: '16px', backgroundColor: 'var(--bg-main)', width: '100%' }}>
                  <h4 style={{ margin: '0 0 12px 0', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Briefcase size={16} className="text-primary" />
                    Recommended Vacancies (Ranked Match Score)
                  </h4>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '16px' }}>
                    {studentDetail.recommended_vacancies && studentDetail.recommended_vacancies.map((vacancy, i) => (
                      <div key={i} style={{ border: '1px solid var(--border-color)', borderRadius: 'var(--radius-sm)', padding: '16px', backgroundColor: 'var(--bg-card)', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', position: 'relative' }}>
                        <div>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '8px' }}>
                            <strong style={{ color: 'var(--text-main)', fontSize: '14px' }}>{vacancy.title}</strong>
                            <span className={`badge ${vacancy.match_score >= 80 ? 'badge-success' : vacancy.match_score >= 50 ? 'badge-warning' : 'badge-danger'}`} style={{ fontSize: '11px' }}>
                              {vacancy.match_score}% Match
                            </span>
                          </div>
                          <div style={{ fontSize: '12px', color: 'var(--primary)', fontWeight: '600', marginBottom: '4px' }}>{vacancy.company}</div>
                          <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '12px' }}>📍 {vacancy.location || 'Remote'}</div>
                          
                          <div style={{ marginBottom: '12px' }}>
                            <span style={{ display: 'block', fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '4px' }}>Required Skills Match</span>
                            <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                              {vacancy.skills_required && vacancy.skills_required.map((s: string) => {
                                const isVerified = studentDetail.profile.verified_skills.some(vs => vs.toLowerCase().trim() === s.toLowerCase().trim());
                                const isUnverified = studentDetail.profile.unverified_skills.some(us => us.toLowerCase().trim() === s.toLowerCase().trim());
                                return (
                                  <span 
                                    key={s} 
                                    className="badge" 
                                    style={{ 
                                      fontSize: '9px',
                                      backgroundColor: isVerified ? 'var(--success-glow)' : isUnverified ? 'var(--primary-glow)' : 'var(--danger-glow)',
                                      color: isVerified ? 'var(--success)' : isUnverified ? 'var(--primary)' : 'var(--danger)',
                                      border: `1px solid ${isVerified ? 'var(--success)' : isUnverified ? 'var(--primary)' : 'var(--danger)'}`
                                    }}
                                  >
                                    {isVerified ? '✅ ' : isUnverified ? '👍 ' : '❌ '}{s}
                                  </span>
                                );
                              })}
                            </div>
                          </div>
                        </div>

                        {vacancy.salary && (
                          <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '8px', marginTop: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Est. Salary:</span>
                            <span style={{ fontSize: '12px', fontWeight: '600', color: 'var(--text-main)' }}>{vacancy.salary}</span>
                          </div>
                        )}
                      </div>
                    ))}
                    {(!studentDetail.recommended_vacancies || studentDetail.recommended_vacancies.length === 0) && (
                      <div style={{ color: 'var(--text-muted)', fontSize: '12px', padding: '10px 0', textAlign: 'center' }}>
                        No matching vacancies found.
                      </div>
                    )}
                  </div>
                </div>

              </div>
            )}

          </div>
        </div>
      )}
    </div>
  );
}

// ─── MOCK DATA FOR DEMO MODE FALLBACKS ───

const mockStudents: Profile[] = [
  {
    id: 1,
    telegram_id: '976284588',
    name: 'Mirjalol Shavkatov',
    university: 'PDP University',
    faculty: 'Software Engineering',
    year: '3',
    target_role: 'Python Backend Developer',
    verified_skills: ['Python', 'SQL', 'FastAPI'],
    unverified_skills: ['Docker', 'Git', 'ChromaDB'],
    readiness_score: 85
  },
  {
    id: 2,
    telegram_id: '123456789',
    name: 'Alisher Rustamov',
    university: 'Inha University in Tashkent',
    faculty: 'Computer Science',
    year: '4',
    target_role: 'Frontend Developer',
    verified_skills: ['React', 'JavaScript'],
    unverified_skills: ['TypeScript', 'HTML/CSS', 'Webpack'],
    readiness_score: 72
  },
  {
    id: 3,
    telegram_id: '987654321',
    name: 'Dilnoza Karimova',
    university: 'TUIT',
    faculty: 'Telecommunications',
    year: '2',
    target_role: 'Python Backend Developer',
    verified_skills: ['Python'],
    unverified_skills: ['Django', 'PostgreSQL'],
    readiness_score: 58
  },
  {
    id: 4,
    telegram_id: '555666777',
    name: 'Javohir Toshmatov',
    university: 'PDP University',
    faculty: 'Information Security',
    year: '3',
    target_role: 'Security Engineer',
    verified_skills: ['Linux', 'Network Security'],
    unverified_skills: ['Python', 'Cryptography'],
    readiness_score: 45
  },
  {
    id: 5,
    telegram_id: '888777666',
    name: 'Shahzoda Olimova',
    university: 'WIUT',
    faculty: 'Business Information Systems',
    year: '4',
    target_role: 'Data Analyst',
    verified_skills: ['SQL', 'Excel'],
    unverified_skills: ['Python', 'Tableau', 'PowerBI'],
    readiness_score: 80
  }
];

const mockVacancies: Vacancy[] = [
  {
    id: 'vac_python_1',
    title: 'Junior Python Developer',
    company: 'EPAM Systems',
    location: 'Tashkent (Hybrid)',
    skills_required: ['Python', 'SQL', 'FastAPI', 'Git', 'Docker'],
    description: 'Looking for a passionate junior developer to build robust enterprise microservices using Python and modern backend frameworks.',
    salary: '$800 - $1200'
  },
  {
    id: 'vac_react_1',
    title: 'React Frontend Developer',
    company: 'PDP Ecosystem',
    location: 'Tashkent (Onsite)',
    skills_required: ['React', 'JavaScript', 'TypeScript', 'HTML/CSS'],
    description: 'Join our product team to build high-performance education tech apps and beautiful dashboards.',
    salary: '$1000 - $1500'
  },
  {
    id: 'vac_data_1',
    title: 'Junior Data Analyst',
    company: 'Ucell',
    location: 'Tashkent (Onsite)',
    skills_required: ['SQL', 'Python', 'Excel', 'Tableau'],
    description: 'Help our business team transform petabytes of telecommunication metrics into actionable executive reports.',
    salary: '$600 - $900'
  }
];

const mockAssessments = [
  {
    telegram_id: 976284588,
    topic: 'Python Core',
    timestamp: '2026-05-22 15:30:11',
    assessment_text: 'Student demonstrates thorough understanding of decorators, context managers, and memory profiling. Self-correction and code validation capabilities are highly present.'
  },
  {
    telegram_id: 976284588,
    topic: 'FastAPI Integration',
    timestamp: '2026-05-22 16:10:05',
    assessment_text: 'Excellent knowledge of Pydantic models, async routing, and OAuth2 security dependencies. Fully ready to build commercial API layers.'
  },
  {
    telegram_id: 123456789,
    topic: 'React Context API',
    timestamp: '2026-05-21 11:20:00',
    assessment_text: 'Satisfactory state-management principles. Understands hooks but requires some training on react rendering performance optimization.'
  }
];

const mockResumes = [
  {
    telegram_id: 976284588,
    filename: 'Mirjalol_Resume_Backend.pdf',
    timestamp: '2026-05-22 14:15:22',
    score: 88,
    feedback: '• Found target keyword Match: "FastAPI", "SQL", "Python".\n• Missing keywords: "Docker", "CI/CD".\n• Formatting review: Font hierarchy is highly clean and ATS-parsable.'
  },
  {
    telegram_id: 123456789,
    filename: 'Alisher_Frontend_CV.pdf',
    timestamp: '2026-05-21 09:44:11',
    score: 75,
    feedback: '• High density of styled icons might cause issues on legacy ATS scanners.\n• Strong target keywords matches: "React", "JavaScript".\n• Suggested edits: Expand project descriptions with metrics.'
  }
];

const mockQuizzes = [
  {
    telegram_id: 976284588,
    topic: 'Python Programming',
    score: 5,
    total_questions: 5,
    timestamp: '2026-05-22 15:28:44'
  },
  {
    telegram_id: 976284588,
    topic: 'FastAPI Web APIs',
    score: 4,
    total_questions: 5,
    timestamp: '2026-05-22 16:05:12'
  },
  {
    telegram_id: 123456789,
    topic: 'React Hooks',
    score: 4,
    total_questions: 5,
    timestamp: '2026-05-21 11:15:20'
  },
  {
    telegram_id: 987654321,
    topic: 'Python Programming',
    score: 4,
    total_questions: 5,
    timestamp: '2026-05-22 10:44:30'
  }
];

const mockInterviews = [
  {
    telegram_id: '976284588',
    topic: 'Python Backend Developer mock interview',
    score: 8,
    max_score: 10,
    timestamp: '2026-05-22 15:35:00',
    situation: 'We needed to scale a legacy Django application handling 10k users/day.',
    task: 'My role was to optimize database queries and introduce a redis caching layer.',
    action: 'I analyzed slow queries using django-debug-toolbar, rewrote 15 complex JOINs, and implemented cache decorators.',
    result: 'Response time decreased by 40% and CPU utilization dropped by 25%.'
  },
  {
    telegram_id: '976284588',
    topic: 'FastAPI Integration mock interview',
    score: 9,
    max_score: 10,
    timestamp: '2026-05-22 16:15:10',
    situation: 'Implementing secure JWT authorization across multiple microservices.',
    task: 'Set up centralized OAuth2 token issue and validation workflow.',
    action: 'Constructed an async security dependency flow using FastAPI and PyJWT, utilizing Redis to store token blacklists.',
    result: 'Auth latency remained sub-5ms and prevented duplicate token re-use successfully.'
  },
  {
    telegram_id: '123456789',
    topic: 'React Hooks & State mock interview',
    score: 7,
    max_score: 10,
    timestamp: '2026-05-21 11:30:22',
    situation: 'Refactoring a multi-step user registration form that suffered from severe lag.',
    task: 'Improve input responsiveness and centralize step state management.',
    action: 'Replaced prop drilling with a Context Provider, memoized slow nested components with React.memo, and debounced key stroke validations.',
    result: 'Input lag reduced to zero and form became fully responsive.'
  }
];

const mockWeakAreas: WeakArea[] = [
  { skill: 'Docker', missing_count: 4 },
  { skill: 'TypeScript', missing_count: 3 },
  { skill: 'CI/CD (GitLab/GitHub Actions)', missing_count: 3 },
  { skill: 'Kubernetes', missing_count: 2 },
  { skill: 'FastAPI', missing_count: 2 },
  { skill: 'ChromaDB / Qdrant', missing_count: 1 }
];

const mockTelemetry: TelemetryData = {
  latency_trend: [
    { id: 1, latency_sec: 1.15, timestamp: '18:10:00' },
    { id: 2, latency_sec: 1.48, timestamp: '18:12:00' },
    { id: 3, latency_sec: 0.95, timestamp: '18:15:00' },
    { id: 4, latency_sec: 2.12, timestamp: '18:16:00' },
    { id: 5, latency_sec: 1.67, timestamp: '18:18:00' },
    { id: 6, latency_sec: 1.34, timestamp: '18:22:00' },
    { id: 7, latency_sec: 1.82, timestamp: '18:25:00' },
    { id: 8, latency_sec: 1.22, timestamp: '18:29:00' },
    { id: 9, latency_sec: 0.88, timestamp: '18:33:00' },
    { id: 10, latency_sec: 1.42, timestamp: '18:35:00' }
  ],
  token_trend: [
    { id: 1, input_tokens: 850, output_tokens: 280, timestamp: '18:10:00' },
    { id: 2, input_tokens: 920, output_tokens: 340, timestamp: '18:12:00' },
    { id: 3, input_tokens: 780, output_tokens: 210, timestamp: '18:15:00' },
    { id: 4, input_tokens: 1100, output_tokens: 410, timestamp: '18:16:00' },
    { id: 5, input_tokens: 990, output_tokens: 310, timestamp: '18:18:00' },
    { id: 6, input_tokens: 880, output_tokens: 290, timestamp: '18:22:00' },
    { id: 7, input_tokens: 1050, output_tokens: 380, timestamp: '18:25:00' },
    { id: 8, input_tokens: 840, output_tokens: 250, timestamp: '18:29:00' },
    { id: 9, input_tokens: 790, output_tokens: 190, timestamp: '18:33:00' },
    { id: 10, input_tokens: 950, output_tokens: 320, timestamp: '18:35:00' }
  ],
  guardrail_stats: {
    'profanity_detected': 3,
    'prompt_injection_blocked': 2,
    'hallucination_self_corrected': 9
  },
  retry_stats: {
    'Retries: 0': 420,
    'Retries: 1': 54,
    'Retries: 2': 11,
    'Retries: 3': 3
  },
  risk_logs: [
    {
      id: 1,
      telegram_id: '555666777',
      category: 'Prompt Injection',
      description: 'System instruction extraction attempt blocked by LLM guardrail validator.',
      severity: 'high',
      timestamp: '2026-05-22 18:16:44'
    },
    {
      id: 2,
      telegram_id: '987654321',
      category: 'Toxicity',
      description: 'Inappropriate language detected in assessment responses. Warning issued.',
      severity: 'medium',
      timestamp: '2026-05-22 16:44:12'
    },
    {
      id: 3,
      telegram_id: '123456789',
      category: 'API Out-of-bounds',
      description: 'Attempted to access non-authorized database records. Intercepted.',
      severity: 'critical',
      timestamp: '2026-05-21 11:55:01'
    }
  ]
};

export default App;
