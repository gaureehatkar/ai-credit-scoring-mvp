import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { getApplications, getCurrentUser } from '../services/api'
import type { ApplicationResponse } from '../types'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { formatCurrency } from '@/lib/utils'
import { PlusCircle, FileText, Clock, CheckCircle2, XCircle, AlertCircle, LogOut } from 'lucide-react'

const statusConfig: Record<string, { color: string; icon: React.ElementType; label: string }> = {
  pending: { color: 'bg-amber-500/10 text-amber-600 border-amber-500/20', icon: Clock, label: 'Pending' },
  under_review: { color: 'bg-blue-500/10 text-blue-600 border-blue-500/20', icon: AlertCircle, label: 'Under Review' },
  approved: { color: 'bg-green-500/10 text-green-600 border-green-500/20', icon: CheckCircle2, label: 'Approved' },
  rejected: { color: 'bg-red-500/10 text-red-600 border-red-500/20', icon: XCircle, label: 'Rejected' },
}

export default function Dashboard() {
  const [applications, setApplications] = useState<ApplicationResponse[]>([])
  const [user, setUser] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => { loadData() }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const [userData, appsData] = await Promise.all([getCurrentUser(), getApplications()])
      setUser(userData)
      setApplications(appsData)
    } catch (error) {
      console.error('Failed to load data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('jwt_token')
    localStorage.removeItem('user_role')
    navigate('/login')
  }

  if (loading) return <div className="min-h-screen flex items-center justify-center bg-background"><div className="text-muted-foreground">Loading...</div></div>

  return (
    <div className="min-h-screen flex flex-col bg-background">
      <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/80 backdrop-blur-xl">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-primary-foreground font-bold text-lg">S</div>
            <span className="font-bold text-lg tracking-tight">Saral Credit</span>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right hidden sm:block">
              <div className="text-sm font-medium">{user?.full_name}</div>
            </div>
            <Avatar>
              <AvatarFallback className="bg-primary/10 text-primary text-xs">
                {user?.full_name?.split(' ').map((n: string) => n[0]).join('').toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <Button variant="ghost" size="icon" onClick={handleLogout} className="text-muted-foreground hover:text-foreground">
              <LogOut className="w-5 h-5" />
            </Button>
          </div>
        </div>
      </header>

      <main className="flex-1 container mx-auto px-4 py-8">
        <div className="space-y-8">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Welcome back, {user?.full_name?.split(' ')[0]}</h1>
              <p className="text-muted-foreground mt-1">Here's an overview of your applications and credit status.</p>
            </div>
            <div className="flex items-center gap-3">
              <Button variant="ghost" size="sm" onClick={loadData} className="gap-2">🔄 Refresh</Button>
              <Link to="/apply"><Button className="gap-2"><PlusCircle className="w-4 h-4" />New Application</Button></Link>
            </div>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Recent Applications</CardTitle>
              <CardDescription>Your latest credit requests and their current status</CardDescription>
            </CardHeader>
            <CardContent>
              {applications.length === 0 ? (
                <div className="text-center py-12">
                  <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mx-auto mb-4">
                    <FileText className="w-8 h-8 text-muted-foreground" />
                  </div>
                  <h3 className="text-lg font-medium">No applications yet</h3>
                  <p className="text-muted-foreground mt-1 mb-6">Start your first application to get your credit score.</p>
                  <Link to="/apply"><Button>Start Application</Button></Link>
                </div>
              ) : (
                <div className="space-y-4">
                  {applications.map(app => {
                    const config = statusConfig[app.status] || statusConfig.pending
                    const StatusIcon = config.icon
                    return (
                      <div key={app.application_id} className="flex flex-col sm:flex-row sm:items-center justify-between p-4 rounded-xl border border-border/50 bg-muted/20 hover:bg-muted/50 transition-colors">
                        <div className="flex items-start gap-4 mb-4 sm:mb-0">
                          <div className={`p-2 rounded-full mt-1 ${config.color.split(' ')[0]} ${config.color.split(' ')[1]}`}>
                            <StatusIcon className="w-5 h-5" />
                          </div>
                          <div>
                            <div className="font-semibold text-lg">{formatCurrency(app.requested_amount)}</div>
                            <div className="text-sm text-muted-foreground capitalize">{app.applicant_type} • {new Date(app.created_at).toLocaleDateString()}</div>
                          </div>
                        </div>
                        <div className="flex items-center justify-between sm:justify-end gap-6 w-full sm:w-auto border-t sm:border-t-0 border-border/50 pt-4 sm:pt-0">
                          {app.credit_score && (
                            <div className="text-center sm:text-right">
                              <div className="text-xs text-muted-foreground uppercase tracking-wider font-semibold">Score</div>
                              <div className="font-bold text-xl text-primary">{Math.round(app.credit_score)}</div>
                            </div>
                          )}
                          {app.risk_category && (
                            <span className={`inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold capitalize ${
                              app.risk_category === 'low' ? 'bg-green-500/10 text-green-600 border-green-500/20' :
                              app.risk_category === 'medium' ? 'bg-amber-500/10 text-amber-600 border-amber-500/20' :
                              'bg-red-500/10 text-red-600 border-red-500/20'
                            }`}>{app.risk_category} risk</span>
                          )}
                          <Badge variant="outline" className={config.color}>{config.label}</Badge>
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </main>

      <footer className="border-t border-border/40 py-6 bg-card/50">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          © {new Date().getFullYear()} Saral Credit. Empowering the underbanked.
        </div>
      </footer>
    </div>
  )
}
