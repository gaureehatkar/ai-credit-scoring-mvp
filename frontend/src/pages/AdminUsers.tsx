import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getAdminUsers, createAdminUser, updateAdminUser, deactivateAdminUser } from '../services/api'
import { AdminSidebar } from '@/components/layout/AdminSidebar'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { X } from 'lucide-react'

interface AdminUser {
  admin_id: number; email: string; full_name: string;
  role: string; permissions: string[]; is_active: boolean; created_at: string;
}

export default function AdminUsers() {
  const [users, setUsers] = useState<AdminUser[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreate, setShowCreate] = useState(false)
  const [selectedUser, setSelectedUser] = useState<AdminUser | null>(null)
  const [createForm, setCreateForm] = useState({ email: '', password: '', full_name: '', role: 'admin', permissions: [] as string[] })
  const [updateForm, setUpdateForm] = useState({ full_name: '', role: '', permissions: [] as string[] })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const navigate = useNavigate()
  const isSuperAdmin = localStorage.getItem('admin_role') === 'super_admin'

  useEffect(() => { loadUsers() }, [])

  const loadUsers = async () => {
    setLoading(true)
    try { setUsers(await getAdminUsers()) }
    catch (err: any) { if (err.response?.status === 401) { localStorage.removeItem('admin_token'); navigate('/admin/login') } }
    finally { setLoading(false) }
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault(); setError(''); setSuccess(''); setSubmitting(true)
    try {
      await createAdminUser(createForm)
      setSuccess('Admin user created')
      setCreateForm({ email: '', password: '', full_name: '', role: 'admin', permissions: [] })
      setShowCreate(false); loadUsers()
    } catch (err: any) { setError(err.response?.data?.detail || 'Failed') }
    finally { setSubmitting(false) }
  }

  const handleUpdate = async (e: React.FormEvent) => {
    e.preventDefault(); if (!selectedUser) return
    setError(''); setSuccess(''); setSubmitting(true)
    try {
      await updateAdminUser(selectedUser.admin_id, updateForm)
      setSuccess('Updated successfully'); setSelectedUser(null); loadUsers()
    } catch (err: any) { setError(err.response?.data?.detail || 'Failed') }
    finally { setSubmitting(false) }
  }

  const handleDeactivate = async (id: number) => {
    if (!confirm('Deactivate this admin user?')) return
    try { await deactivateAdminUser(id); loadUsers() }
    catch (err: any) { setError(err.response?.data?.detail || 'Failed') }
  }

  return (
    <div className="flex min-h-screen bg-muted/30">
      <AdminSidebar />
      <main className="flex-1 md:ml-64 p-4 md:p-8">
        <div className="max-w-6xl mx-auto space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Admin Users</h1>
              <p className="text-muted-foreground mt-1">Manage admin accounts and permissions</p>
            </div>
            {isSuperAdmin && <Button size="sm" onClick={() => setShowCreate(true)}>+ Add Admin</Button>}
          </div>

          {!isSuperAdmin && <div className="bg-blue-500/10 text-blue-600 border border-blue-500/20 rounded-lg p-3 text-sm">Only super admins can manage admin users.</div>}
          {error && <div className="bg-destructive/10 text-destructive border border-destructive/20 rounded-lg p-3 text-sm">{error}</div>}
          {success && <div className="bg-green-500/10 text-green-600 border border-green-500/20 rounded-lg p-3 text-sm">{success}</div>}

          <Card>
            <CardContent className="p-0">
              {loading ? (
                <div className="text-center py-12 text-muted-foreground">Loading...</div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b bg-muted/50">
                        <th className="h-10 px-4 text-left text-xs font-medium text-muted-foreground uppercase">Name</th>
                        <th className="h-10 px-4 text-left text-xs font-medium text-muted-foreground uppercase">Email</th>
                        <th className="h-10 px-4 text-left text-xs font-medium text-muted-foreground uppercase">Role</th>
                        <th className="h-10 px-4 text-left text-xs font-medium text-muted-foreground uppercase">Status</th>
                        <th className="h-10 px-4 text-left text-xs font-medium text-muted-foreground uppercase">Created</th>
                        {isSuperAdmin && <th className="h-10 px-4 text-right text-xs font-medium text-muted-foreground uppercase">Actions</th>}
                      </tr>
                    </thead>
                    <tbody>
                      {users.map(u => (
                        <tr key={u.admin_id} className="border-b hover:bg-muted/50 transition-colors">
                          <td className="p-4 font-semibold">{u.full_name}</td>
                          <td className="p-4 text-muted-foreground text-sm">{u.email}</td>
                          <td className="p-4">
                            <Badge variant="outline" className="bg-blue-500/10 text-blue-600 border-blue-500/20">
                              {u.role === 'super_admin' ? 'Super Admin' : 'Admin'}
                            </Badge>
                          </td>
                          <td className="p-4">
                            <Badge variant="outline" className={u.is_active ? 'bg-green-500/10 text-green-600 border-green-500/20' : 'bg-red-500/10 text-red-600 border-red-500/20'}>
                              {u.is_active ? 'Active' : 'Inactive'}
                            </Badge>
                          </td>
                          <td className="p-4 text-muted-foreground text-sm">{new Date(u.created_at).toLocaleDateString()}</td>
                          {isSuperAdmin && (
                            <td className="p-4 text-right">
                              <div className="flex justify-end gap-2">
                                <Button variant="ghost" size="sm" onClick={() => { setSelectedUser(u); setUpdateForm({ full_name: u.full_name, role: u.role, permissions: u.permissions }); setError('') }}>Edit</Button>
                                {u.is_active && <Button variant="ghost" size="sm" className="text-destructive hover:text-destructive" onClick={() => handleDeactivate(u.admin_id)}>Deactivate</Button>}
                              </div>
                            </td>
                          )}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </main>

      {/* Create Modal */}
      {showCreate && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-card rounded-xl p-6 w-full max-w-md shadow-2xl border border-border">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-bold">Create Admin User</h3>
              <button onClick={() => setShowCreate(false)} className="text-muted-foreground hover:text-foreground"><X className="w-5 h-5" /></button>
            </div>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="space-y-2"><Label>Full Name</Label><Input value={createForm.full_name} onChange={e => setCreateForm({ ...createForm, full_name: e.target.value })} required /></div>
              <div className="space-y-2"><Label>Email</Label><Input type="email" value={createForm.email} onChange={e => setCreateForm({ ...createForm, email: e.target.value })} required /></div>
              <div className="space-y-2"><Label>Password</Label><Input type="password" value={createForm.password} onChange={e => setCreateForm({ ...createForm, password: e.target.value })} required minLength={8} /></div>
              <div className="space-y-2">
                <Label>Role</Label>
                <Select value={createForm.role} onValueChange={v => setCreateForm({ ...createForm, role: v })}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="admin">Admin</SelectItem>
                    <SelectItem value="super_admin">Super Admin</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              {error && <p className="text-sm text-destructive">{error}</p>}
              <div className="flex gap-3">
                <Button type="submit" className="flex-1" disabled={submitting}>{submitting ? 'Creating...' : 'Create'}</Button>
                <Button type="button" variant="outline" className="flex-1" onClick={() => setShowCreate(false)}>Cancel</Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {selectedUser && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-card rounded-xl p-6 w-full max-w-md shadow-2xl border border-border">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-bold">Edit {selectedUser.full_name}</h3>
              <button onClick={() => setSelectedUser(null)} className="text-muted-foreground hover:text-foreground"><X className="w-5 h-5" /></button>
            </div>
            <form onSubmit={handleUpdate} className="space-y-4">
              <div className="space-y-2"><Label>Full Name</Label><Input value={updateForm.full_name} onChange={e => setUpdateForm({ ...updateForm, full_name: e.target.value })} required /></div>
              <div className="space-y-2">
                <Label>Role</Label>
                <Select value={updateForm.role} onValueChange={v => setUpdateForm({ ...updateForm, role: v })}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="admin">Admin</SelectItem>
                    <SelectItem value="super_admin">Super Admin</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              {error && <p className="text-sm text-destructive">{error}</p>}
              <div className="flex gap-3">
                <Button type="submit" className="flex-1" disabled={submitting}>{submitting ? 'Saving...' : 'Save'}</Button>
                <Button type="button" variant="outline" className="flex-1" onClick={() => setSelectedUser(null)}>Cancel</Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}
