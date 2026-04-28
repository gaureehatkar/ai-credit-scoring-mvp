import { Link, useLocation } from 'react-router-dom'
import { useNavigate } from 'react-router-dom'
import { LayoutDashboard, FileText, Users, BarChart3, LogOut } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Button } from '@/components/ui/button'

const navLinks = [
  { href: '/admin/analytics', icon: LayoutDashboard, label: 'Dashboard' },
  { href: '/admin/applications', icon: FileText, label: 'Applications' },
  { href: '/admin/users', icon: Users, label: 'Admin Users' },
]

export function AdminSidebar() {
  const location = useLocation()
  const navigate = useNavigate()
  const adminEmail = localStorage.getItem('admin_email') || 'Admin'
  const adminRole = localStorage.getItem('admin_role') || 'admin'

  const handleLogout = () => {
    ;['admin_token', 'admin_id', 'admin_email', 'admin_role'].forEach(k => localStorage.removeItem(k))
    navigate('/admin/login')
  }

  return (
    <aside className="hidden md:flex w-64 flex-col fixed inset-y-0 z-50 bg-sidebar text-sidebar-foreground border-r border-sidebar-border">
      <div className="p-6 flex flex-col h-full">
        <div className="flex items-center gap-2 mb-8">
          <div className="w-8 h-8 rounded-lg bg-sidebar-primary flex items-center justify-center text-sidebar-primary-foreground font-bold text-lg">S</div>
          <span className="font-bold text-xl tracking-tight">Saral Admin</span>
        </div>

        <nav className="flex flex-col gap-1 flex-1">
          {navLinks.map(({ href, icon: Icon, label }) => (
            <Link key={href} to={href}>
              <div className={cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-medium transition-colors cursor-pointer',
                location.pathname === href
                  ? 'bg-sidebar-accent text-sidebar-accent-foreground'
                  : 'text-sidebar-foreground/80 hover:bg-sidebar-accent/50 hover:text-sidebar-foreground'
              )}>
                <Icon className="w-5 h-5" />
                {label}
              </div>
            </Link>
          ))}
        </nav>

        <div className="border-t border-sidebar-border pt-4 mt-4">
          <div className="flex items-center gap-3 p-2 rounded-lg bg-sidebar-accent/30 mb-3">
            <Avatar className="h-9 w-9">
              <AvatarFallback className="bg-sidebar-primary text-sidebar-primary-foreground text-xs">
                {adminEmail.substring(0, 2).toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium truncate">{adminEmail}</div>
              <div className="text-xs text-sidebar-foreground/60">{adminRole === 'super_admin' ? 'Super Admin' : 'Admin'}</div>
            </div>
          </div>
          <Button variant="ghost" className="w-full justify-start gap-2 text-sidebar-foreground/60 hover:text-sidebar-foreground hover:bg-sidebar-accent/50" onClick={handleLogout}>
            <LogOut className="w-4 h-4" />
            Sign out
          </Button>
        </div>
      </div>
    </aside>
  )
}
