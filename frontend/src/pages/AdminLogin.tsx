import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { adminLogin } from '../services/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardFooter } from '@/components/ui/card'
import { Loader2, ShieldCheck } from 'lucide-react'

export default function AdminLogin() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const response = await adminLogin(email, password)
      localStorage.setItem('admin_token', response.access_token)
      localStorage.setItem('admin_id', response.admin_id.toString())
      localStorage.setItem('admin_email', response.email)
      localStorage.setItem('admin_role', response.role)
      navigate('/admin/dashboard')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Admin login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-sidebar text-sidebar-foreground relative overflow-hidden">
      <div className="absolute top-[-10%] left-[-10%] w-96 h-96 bg-sidebar-primary/20 rounded-full blur-[100px]" />
      <div className="absolute bottom-[-10%] right-[-10%] w-96 h-96 bg-sidebar-accent/50 rounded-full blur-[100px]" />
      <div className="w-full max-w-[400px] z-10 p-6">
        <div className="text-center mb-8 flex flex-col items-center">
          <div className="w-16 h-16 rounded-2xl bg-sidebar-primary flex items-center justify-center text-sidebar-primary-foreground mb-6 shadow-xl">
            <ShieldCheck className="w-8 h-8" />
          </div>
          <h2 className="text-3xl font-bold tracking-tight">Saral Admin</h2>
          <p className="text-sidebar-foreground/60 mt-2">Secure access for credit officers</p>
        </div>
        <Card className="border-sidebar-border bg-sidebar/50 backdrop-blur-xl shadow-2xl">
          <form onSubmit={handleSubmit}>
            <CardContent className="pt-6 space-y-4">
              <div className="space-y-2 text-left">
                <Label htmlFor="email" className="text-sidebar-foreground/80">Officer Email</Label>
                <Input id="email" type="email" value={email} onChange={e => setEmail(e.target.value)} required className="bg-sidebar-accent/50 border-sidebar-border text-sidebar-foreground" />
              </div>
              <div className="space-y-2 text-left">
                <Label htmlFor="password" className="text-sidebar-foreground/80">Password</Label>
                <Input id="password" type="password" value={password} onChange={e => setPassword(e.target.value)} required className="bg-sidebar-accent/50 border-sidebar-border text-sidebar-foreground" />
              </div>
              {error && <p className="text-sm text-destructive">{error}</p>}
            </CardContent>
            <CardFooter className="pb-6">
              <Button type="submit" className="w-full h-11 text-base font-medium bg-sidebar-primary hover:bg-sidebar-primary/90 text-sidebar-primary-foreground" disabled={loading}>
                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Authenticate'}
              </Button>
            </CardFooter>
          </form>
        </Card>
        <div className="mt-8 text-center">
          <Link to="/login" className="text-sm text-sidebar-foreground/60 hover:text-sidebar-foreground transition-colors">
            ← Return to Applicant Portal
          </Link>
        </div>
      </div>
    </div>
  )
}
