import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { getAdminInfo } from '../services/api'
import { AdminSidebar } from '@/components/layout/AdminSidebar'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export default function AdminDashboard() {
  const [admin, setAdmin] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    getAdminInfo()
      .then(setAdmin)
      .catch(() => {
        ;['admin_token', 'admin_id', 'admin_email', 'admin_role'].forEach(k => localStorage.removeItem(k))
        navigate('/admin/login')
      })
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="min-h-screen flex items-center justify-center bg-background"><div className="text-muted-foreground">Loading...</div></div>

  return (
    <div className="flex min-h-screen bg-muted/30">
      <AdminSidebar />
      <main className="flex-1 md:ml-64 p-4 md:p-8">
        <div className="max-w-6xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold tracking-tight">Welcome back, {admin?.full_name}</h1>
            <p className="text-muted-foreground mt-1">Manage applications, users, and view analytics from here.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              { to: '/admin/analytics', icon: '📊', title: 'Analytics', desc: 'View system metrics and reports', color: 'border-t-blue-500' },
              { to: '/admin/applications', icon: '📋', title: 'Applications', desc: 'Manage credit applications', color: 'border-t-green-500' },
              { to: '/admin/users', icon: '👥', title: 'Admin Users', desc: 'Manage admin accounts', color: 'border-t-purple-500' },
            ].map(c => (
              <Link key={c.to} to={c.to} className="no-underline">
                <Card className={`border-t-4 ${c.color} cursor-pointer hover:-translate-y-1 transition-transform`}>
                  <CardHeader>
                    <div className="text-3xl mb-2">{c.icon}</div>
                    <CardTitle>{c.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">{c.desc}</p>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}
