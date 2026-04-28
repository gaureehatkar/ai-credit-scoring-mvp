import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams, Link } from 'react-router-dom'
import api from '../services/api'
import { Button } from '@/components/ui/button'
import { Loader2, CheckCircle2, XCircle } from 'lucide-react'

export default function VerifyEmail() {
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [message, setMessage] = useState('')
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()

  useEffect(() => {
    const token = searchParams.get('token')
    if (!token) { setStatus('error'); setMessage('Invalid verification link.'); return }
    api.get(`/api/v1/auth/verify-email?token=${token}`)
      .then(res => { setStatus('success'); setMessage(res.data.message); setTimeout(() => navigate('/login'), 3000) })
      .catch(err => { setStatus('error'); setMessage(err.response?.data?.detail || 'Verification failed.') })
  }, [])

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="w-full max-w-md text-center">
        <div className="flex items-center justify-center gap-2 mb-12">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-primary-foreground font-bold text-xl">S</div>
          <span className="font-bold text-xl tracking-tight">Saral Credit</span>
        </div>
        {status === 'loading' && (
          <div className="space-y-6">
            <Loader2 className="w-12 h-12 animate-spin text-primary mx-auto" />
            <h1 className="text-2xl font-semibold">Verifying your email...</h1>
            <p className="text-muted-foreground">Please wait while we confirm your email address.</p>
          </div>
        )}
        {status === 'success' && (
          <div className="space-y-6">
            <div className="w-20 h-20 bg-green-500/10 rounded-full flex items-center justify-center mx-auto text-green-500">
              <CheckCircle2 className="w-10 h-10" />
            </div>
            <div>
              <h1 className="text-2xl font-semibold">Email Verified!</h1>
              <p className="text-muted-foreground mt-2">{message}</p>
              <p className="text-sm text-muted-foreground mt-1">Redirecting to login...</p>
            </div>
          </div>
        )}
        {status === 'error' && (
          <div className="space-y-6">
            <div className="w-20 h-20 bg-red-500/10 rounded-full flex items-center justify-center mx-auto text-red-500">
              <XCircle className="w-10 h-10" />
            </div>
            <div>
              <h1 className="text-2xl font-semibold">Verification Failed</h1>
              <p className="text-muted-foreground mt-2">{message}</p>
            </div>
            <Link to="/register"><Button variant="outline" className="w-full">Back to Register</Button></Link>
          </div>
        )}
      </div>
    </div>
  )
}
