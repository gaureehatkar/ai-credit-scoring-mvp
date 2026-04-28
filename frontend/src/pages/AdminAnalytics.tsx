import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { getDashboardMetrics, getCreditScoreDistribution } from '../services/api'
import { AdminSidebar } from '@/components/layout/AdminSidebar'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function AdminAnalytics() {
  const [metrics, setMetrics] = useState<any>(null)
  const [scoreDistribution, setScoreDistribution] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [period, setPeriod] = useState(30)
  const navigate = useNavigate()

  useEffect(() => { loadAnalytics() }, [period])

  const loadAnalytics = async () => {
    setLoading(true)
    try {
      const [m, d] = await Promise.all([getDashboardMetrics(period), getCreditScoreDistribution(period)])
      setMetrics(m)
      setScoreDistribution(d)
    } catch (err: any) {
      if (err.response?.status === 401) { localStorage.removeItem('admin_token'); navigate('/admin/login') }
    } finally { setLoading(false) }
  }

  const maxCount = scoreDistribution.length ? Math.max(...scoreDistribution.map((d: any) => d.count), 1) : 1

  const approvalByRisk = [
    { name: 'Low Risk', approved: 85, rejected: 15 },
    { name: 'Medium Risk', approved: 45, rejected: 55 },
    { name: 'High Risk', approved: 10, rejected: 90 },
  ]

  return (
    <div className="flex min-h-screen bg-muted/30">
      <AdminSidebar />
      <main className="flex-1 md:ml-64 p-4 md:p-8">
        <div className="max-w-6xl mx-auto space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
              <p className="text-muted-foreground mt-1">System metrics and performance overview</p>
            </div>
            <Select value={String(period)} onValueChange={v => setPeriod(Number(v))}>
              <SelectTrigger className="w-[140px] bg-card"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="7">Last 7 days</SelectItem>
                <SelectItem value="30">Last 30 days</SelectItem>
                <SelectItem value="90">Last 90 days</SelectItem>
                <SelectItem value="365">Last year</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {loading ? (
            <div className="text-center py-12 text-muted-foreground">Loading...</div>
          ) : metrics && (
            <>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card className="border-l-4 border-l-blue-500">
                  <CardHeader className="pb-2"><CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Total Applications</CardTitle></CardHeader>
                  <CardContent><div className="text-4xl font-bold">{metrics.total_applications}</div></CardContent>
                </Card>
                <Card className="border-l-4 border-l-green-500">
                  <CardHeader className="pb-2"><CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Approval Rate</CardTitle></CardHeader>
                  <CardContent><div className="text-4xl font-bold">{metrics.approval_rate.toFixed(1)}%</div></CardContent>
                </Card>
                <Card className="border-l-4 border-l-purple-500">
                  <CardHeader className="pb-2"><CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Avg Credit Score</CardTitle></CardHeader>
                  <CardContent><div className="text-4xl font-bold">{Math.round(metrics.average_credit_score)}</div></CardContent>
                </Card>
              </div>

              <div className="grid lg:grid-cols-2 gap-6">
                <Card>
                  <CardHeader><CardTitle>Risk Distribution</CardTitle></CardHeader>
                  <CardContent className="space-y-3">
                    {[
                      { label: 'Low Risk', value: metrics.risk_distribution.low, bg: 'bg-green-500/10', text: 'text-green-600', bar: 'bg-green-500' },
                      { label: 'Medium Risk', value: metrics.risk_distribution.medium, bg: 'bg-amber-500/10', text: 'text-amber-600', bar: 'bg-amber-500' },
                      { label: 'High Risk', value: metrics.risk_distribution.high, bg: 'bg-red-500/10', text: 'text-red-600', bar: 'bg-red-500' },
                    ].map(r => (
                      <div key={r.label} className={`flex justify-between items-center p-3 rounded-lg ${r.bg}`}>
                        <span className={`font-semibold ${r.text}`}>{r.label}</span>
                        <span className={`text-2xl font-bold ${r.text}`}>{r.value}</span>
                      </div>
                    ))}
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader><CardTitle>Approval Rate by Risk Band</CardTitle></CardHeader>
                  <CardContent>
                    <div className="h-[220px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={approvalByRisk} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="hsl(214 32% 91%)" />
                          <XAxis dataKey="name" fontSize={11} tickLine={false} axisLine={false} />
                          <YAxis fontSize={11} tickLine={false} axisLine={false} />
                          <Tooltip contentStyle={{ backgroundColor: 'white', borderColor: 'hsl(214 32% 91%)', borderRadius: '8px' }} />
                          <Bar dataKey="approved" stackId="a" fill="hsl(142 71% 45%)" radius={[0, 0, 4, 4]} />
                          <Bar dataKey="rejected" stackId="a" fill="hsl(0 84% 60%)" radius={[4, 4, 0, 0]} />
                        </BarChart>
                      </ResponsiveContainer>
                    </div>
                  </CardContent>
                </Card>

                <Card className="lg:col-span-2">
                  <CardHeader><CardTitle>Credit Score Distribution</CardTitle></CardHeader>
                  <CardContent>
                    {scoreDistribution.length === 0 ? (
                      <div className="text-center py-8 text-muted-foreground">No data for this period.</div>
                    ) : (
                      <div className="space-y-3">
                        {scoreDistribution.map((item: any) => (
                          <div key={item.range} className="flex items-center gap-3">
                            <span className="w-20 text-sm font-medium text-right flex-shrink-0">{item.range}</span>
                            <div className="flex-1 h-7 bg-muted rounded overflow-hidden">
                              <div
                                className="h-full bg-primary rounded flex items-center px-2 transition-all duration-500"
                                style={{ width: `${(item.count / maxCount) * 100}%` }}
                              >
                                {item.count > 0 && <span className="text-xs text-white font-semibold">{item.count}</span>}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>

              {metrics.timestamp && (
                <p className="text-xs text-muted-foreground">Last updated: {new Date(metrics.timestamp).toLocaleString()}</p>
              )}
            </>
          )}
        </div>
      </main>
    </div>
  )
}
