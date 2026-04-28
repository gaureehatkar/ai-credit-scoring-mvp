import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getAdminApplications, updateApplicationStatus } from '../services/api'
import { AdminSidebar } from '@/components/layout/AdminSidebar'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { formatCurrency } from '@/lib/utils'
import { Search, CheckCircle, XCircle, X } from 'lucide-react'

interface Application {
  application_id: number; user_id: number; applicant_type: string; status: string;
  requested_amount: number; credit_score?: number; risk_category?: string; created_at: string;
  document_links?: Record<string, string>;
  consistency_flags?: string[];
}

const statusColors: Record<string, string> = {
  pending: 'bg-amber-500/10 text-amber-600 border-amber-500/20',
  under_review: 'bg-blue-500/10 text-blue-600 border-blue-500/20',
  approved: 'bg-green-500/10 text-green-600 border-green-500/20',
  rejected: 'bg-red-500/10 text-red-600 border-red-500/20',
}

export default function AdminApplications() {
  const [applications, setApplications] = useState<Application[]>([])
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState('')
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedApp, setSelectedApp] = useState<Application | null>(null)
  const [updateForm, setUpdateForm] = useState({ status: '', notes: '', reason: '' })
  const [updating, setUpdating] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [page, setPage] = useState(0)
  const navigate = useNavigate()
  const limit = 20

  useEffect(() => { loadApplications() }, [page, statusFilter])

  const loadApplications = async () => {
    setLoading(true)
    try {
      const data = await getAdminApplications(page * limit, limit, statusFilter || undefined)
      setApplications(data)
    } catch (err: any) {
      if (err.response?.status === 401) { localStorage.removeItem('admin_token'); navigate('/admin/login') }
    } finally { setLoading(false) }
  }

  const openModal = (app: Application) => {
    setSelectedApp(app)
    setUpdateForm({ status: app.status, notes: '', reason: '' })
    setError(''); setSuccess('')
  }

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedApp) return
    setUpdating(true); setError(''); setSuccess('')
    try {
      await updateApplicationStatus(selectedApp.application_id, updateForm.status, updateForm.notes || undefined, updateForm.reason || undefined)
      setSuccess('Status updated successfully')
      loadApplications()
      setTimeout(() => { setSelectedApp(null); setSuccess('') }, 1500)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to update status')
    } finally { setUpdating(false) }
  }

  const filtered = applications.filter(app =>
    searchTerm === '' || app.application_id.toString().includes(searchTerm) || app.user_id.toString().includes(searchTerm)
  )

  return (
    <div className="flex min-h-screen bg-muted/30">
      <AdminSidebar />
      <main className="flex-1 md:ml-64 p-4 md:p-8">
        <div className="max-w-6xl mx-auto space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Applications</h1>
              <p className="text-muted-foreground mt-1">Review AI credit decisions and manage applications.</p>
            </div>
            <div className="flex items-center gap-2">
              <div className="relative">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input placeholder="Search by ID..." className="pl-9 w-[200px] bg-card" value={searchTerm} onChange={e => setSearchTerm(e.target.value)} />
              </div>
              <Select value={statusFilter} onValueChange={v => { setStatusFilter(v === 'all' ? '' : v); setPage(0) }}>
                <SelectTrigger className="w-[140px] bg-card"><SelectValue placeholder="All statuses" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All statuses</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="under_review">Under Review</SelectItem>
                  <SelectItem value="approved">Approved</SelectItem>
                  <SelectItem value="rejected">Rejected</SelectItem>
                </SelectContent>
              </Select>
              <Button variant="ghost" size="sm" onClick={loadApplications}>🔄</Button>
            </div>
          </div>

          <Card>
            <CardContent className="p-0">
              {loading && filtered.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">Loading...</div>
              ) : filtered.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">No applications found.</div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="h-10 px-4 text-left text-xs font-medium text-muted-foreground uppercase">ID</th>
                        <th className="h-10 px-4 text-left text-xs font-medium text-muted-foreground uppercase">User</th>
                        <th className="h-10 px-4 text-left text-xs font-medium text-muted-foreground uppercase">Type</th>
                        <th className="h-10 px-4 text-left text-xs font-medium text-muted-foreground uppercase">Amount</th>
                        <th className="h-10 px-4 text-left text-xs font-medium text-muted-foreground uppercase">Score</th>
                        <th className="h-10 px-4 text-left text-xs font-medium text-muted-foreground uppercase">Risk</th>
                        <th className="h-10 px-4 text-left text-xs font-medium text-muted-foreground uppercase">Status</th>
                        <th className="h-10 px-4 text-left text-xs font-medium text-muted-foreground uppercase">Date</th>
                        <th className="h-10 px-4 text-right text-xs font-medium text-muted-foreground uppercase">Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filtered.map(app => (
                        <tr key={app.application_id} className="border-b hover:bg-muted/50 transition-colors">
                          <td className="p-4 font-semibold">#{app.application_id}</td>
                          <td className="p-4 text-muted-foreground text-sm">User {app.user_id}</td>
                          <td className="p-4 capitalize text-sm">{app.applicant_type}</td>
                          <td className="p-4 text-sm">{formatCurrency(app.requested_amount)}</td>
                          <td className="p-4 font-bold text-primary">{app.credit_score ? Math.round(app.credit_score) : '—'}</td>
                          <td className="p-4">
                            {app.risk_category ? (
                              <Badge variant="outline" className={
                                app.risk_category === 'low' ? 'bg-green-500/10 text-green-600 border-green-500/20' :
                                app.risk_category === 'medium' ? 'bg-amber-500/10 text-amber-600 border-amber-500/20' :
                                'bg-red-500/10 text-red-600 border-red-500/20'
                              }>{app.risk_category}</Badge>
                            ) : '—'}
                          </td>
                          <td className="p-4">
                            <Badge variant="outline" className={statusColors[app.status] || ''}>{app.status.replace('_', ' ')}</Badge>
                          </td>
                          <td className="p-4 text-muted-foreground text-sm">{new Date(app.created_at).toLocaleDateString()}</td>
                          <td className="p-4 text-right">
                            <div className="flex justify-end items-center gap-2">
                              {app.consistency_flags && app.consistency_flags.length > 0 && (
                                <span title={`${app.consistency_flags.length} warning(s)`} className="text-red-500 text-xs font-bold">🚨</span>
                              )}
                              {app.document_links && Object.keys(app.document_links).length > 0 && (
                                <span title="Has supporting documents" className="text-blue-500 text-xs">📎</span>
                              )}
                              <Button variant="ghost" size="sm" onClick={() => openModal(app)}>Review</Button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  <div className="flex justify-between items-center p-4 border-t">
                    <Button variant="ghost" size="sm" onClick={() => setPage(Math.max(0, page - 1))} disabled={page === 0}>← Prev</Button>
                    <span className="text-sm text-muted-foreground">Page {page + 1}</span>
                    <Button variant="ghost" size="sm" onClick={() => setPage(page + 1)} disabled={applications.length < limit}>Next →</Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </main>

      {selectedApp && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-card rounded-xl p-6 w-full max-w-lg shadow-2xl border border-border">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-bold">Review Application #{selectedApp.application_id}</h3>
              <button onClick={() => setSelectedApp(null)} className="text-muted-foreground hover:text-foreground"><X className="w-5 h-5" /></button>
            </div>
            <div className="bg-muted/50 rounded-lg p-4 mb-4 space-y-2 text-sm">
              <div className="flex justify-between"><span className="text-muted-foreground">User ID</span><span>{selectedApp.user_id}</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Amount</span><span>{formatCurrency(selectedApp.requested_amount)}</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Credit Score</span><span className="font-bold text-primary">{selectedApp.credit_score ? Math.round(selectedApp.credit_score) : '—'}</span></div>
              <div className="flex justify-between"><span className="text-muted-foreground">Current Status</span><Badge variant="outline" className={statusColors[selectedApp.status] || ''}>{selectedApp.status.replace('_', ' ')}</Badge></div>
            </div>

            {/* Consistency Flags */}
            {selectedApp.consistency_flags && selectedApp.consistency_flags.length > 0 && (
              <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 mb-4">
                <div className="text-sm font-semibold text-red-600 mb-2">🚨 Data Consistency Warnings</div>
                <div className="space-y-1">
                  {selectedApp.consistency_flags.map((flag: string, i: number) => (
                    <div key={i} className="text-xs text-red-600">{flag}</div>
                  ))}
                </div>
              </div>
            )}

            {/* Document Links */}
            {selectedApp.document_links && Object.keys(selectedApp.document_links).length > 0 && (
              <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-3 mb-4">
                <div className="text-sm font-semibold text-blue-600 mb-2">📎 Supporting Documents</div>
                <div className="space-y-1">
                  {Object.entries(selectedApp.document_links).map(([key, url]) => (
                    <div key={key} className="flex justify-between items-center text-xs">
                      <span className="text-muted-foreground capitalize">{key.replace('_', ' ')}</span>
                      <a href={url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline truncate max-w-[200px]">
                        View Document →
                      </a>
                    </div>
                  ))}
                </div>
              </div>
            )}
            <form onSubmit={handleUpdate} className="space-y-4">
              <div className="space-y-2">
                <Label>New Status</Label>
                <Select value={updateForm.status} onValueChange={v => setUpdateForm({ ...updateForm, status: v })}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="pending">Pending</SelectItem>
                    <SelectItem value="under_review">Under Review</SelectItem>
                    <SelectItem value="approved">Approved</SelectItem>
                    <SelectItem value="rejected">Rejected</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Reason (optional)</Label>
                <Input value={updateForm.reason} onChange={e => setUpdateForm({ ...updateForm, reason: e.target.value })} placeholder="e.g. Credit score above threshold" />
              </div>
              <div className="space-y-2">
                <Label>Notes (optional)</Label>
                <Input value={updateForm.notes} onChange={e => setUpdateForm({ ...updateForm, notes: e.target.value })} placeholder="Additional notes" />
              </div>
              {error && <p className="text-sm text-destructive">{error}</p>}
              {success && <p className="text-sm text-green-600">{success}</p>}
              <div className="flex gap-3">
                <Button type="submit" className="flex-1 gap-2" disabled={updating}>
                  <CheckCircle className="w-4 h-4" />{updating ? 'Updating...' : 'Update Status'}
                </Button>
                <Button type="button" variant="outline" className="flex-1 gap-2" onClick={() => setSelectedApp(null)} disabled={updating}>
                  <XCircle className="w-4 h-4" />Cancel
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
