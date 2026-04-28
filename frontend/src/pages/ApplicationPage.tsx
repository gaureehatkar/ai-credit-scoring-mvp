import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { submitApplication, getCreditScore } from '../services/api'
import type { CreditApplication, AlternativeData, SHAPExplanation } from '../types'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { ArrowLeft, CheckCircle2, TrendingUp, TrendingDown, Info, Loader2, Lightbulb } from 'lucide-react'

function EMICalculator({ loanAmount }: { loanAmount: number }) {
  const [principal, setPrincipal] = useState(loanAmount)
  const [rate, setRate] = useState(12)
  const [tenure, setTenure] = useState(24)
  const r = rate / 12 / 100
  const emi = r === 0 ? principal / tenure : (principal * r * Math.pow(1 + r, tenure)) / (Math.pow(1 + r, tenure) - 1)
  const total = emi * tenure
  const interest = total - principal

  return (
    <Card className="mt-6">
      <CardHeader className="pb-3">
        <CardTitle className="text-base">📊 EMI Calculator</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-3 gap-3">
          <div className="space-y-1">
            <Label className="text-xs">Loan Amount (₹)</Label>
            <Input type="number" value={principal} onChange={e => setPrincipal(Number(e.target.value))} className="h-8 text-sm" />
          </div>
          <div className="space-y-1">
            <Label className="text-xs">Interest Rate (% p.a.)</Label>
            <Input type="number" value={rate} onChange={e => setRate(Number(e.target.value))} step={0.5} className="h-8 text-sm" />
          </div>
          <div className="space-y-1">
            <Label className="text-xs">Tenure (months)</Label>
            <Input type="number" value={tenure} onChange={e => setTenure(Number(e.target.value))} className="h-8 text-sm" />
          </div>
        </div>
        <div className="grid grid-cols-3 gap-3">
          <div className="bg-blue-500 text-white p-3 rounded-lg text-center">
            <div className="text-xs opacity-85 mb-1">Monthly EMI</div>
            <div className="text-lg font-bold">₹{Math.round(emi).toLocaleString()}</div>
          </div>
          <div className="bg-destructive text-destructive-foreground p-3 rounded-lg text-center">
            <div className="text-xs opacity-85 mb-1">Total Interest</div>
            <div className="text-lg font-bold">₹{Math.round(interest).toLocaleString()}</div>
          </div>
          <div className="bg-green-600 text-white p-3 rounded-lg text-center">
            <div className="text-xs opacity-85 mb-1">Total Payment</div>
            <div className="text-lg font-bold">₹{Math.round(total).toLocaleString()}</div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

function ImprovementSuggestions({ explanations, altData, creditScore }: {
  explanations: SHAPExplanation[]
  altData: AlternativeData
  creditScore: number
}) {
  const suggestions: { icon: string; title: string; detail: string; priority: 'high' | 'medium' | 'low' }[] = []

  // Find the worst negative SHAP factors (used for rule-based suggestions below)
  explanations.filter(e => e.shap_value < 0).sort((a, b) => a.shap_value - b.shap_value)

  // Rule-based suggestions from actual data
  const debtRatioFactor = explanations.find(e => e.feature_name === 'DebtRatio' || e.feature_name === 'debt_ratio_log')
  if (debtRatioFactor && debtRatioFactor.shap_value < 0) {
    suggestions.push({
      icon: '💳',
      title: 'Reduce your debt-to-income ratio',
      detail: 'Your loan amount is high relative to your income. Try requesting a smaller amount or increasing your income before applying.',
      priority: 'high'
    })
  }

  const lateFactor = explanations.find(e => e.feature_name === 'total_late_payments' || e.feature_name === 'NumberOfTimes90DaysLate')
  if (lateFactor && lateFactor.shap_value < 0) {
    suggestions.push({
      icon: '📅',
      title: 'Improve your payment consistency',
      detail: 'Late payments are the biggest negative factor. Set up auto-pay for bills and loans to avoid missing due dates.',
      priority: 'high'
    })
  }

  if ((altData.loan_repayment_history_score || 5) < 7) {
    suggestions.push({
      icon: '🏦',
      title: 'Build a stronger repayment track record',
      detail: 'Your loan repayment history score is below average. Repay any existing microfinance or informal loans on time for 6+ months.',
      priority: 'high'
    })
  }

  if ((altData.utility_bill_payment_score || 5) < 7) {
    suggestions.push({
      icon: '💡',
      title: 'Pay utility bills on time consistently',
      detail: 'Electricity, water, and phone bills paid on time signal financial discipline. Set reminders or auto-pay for these.',
      priority: 'medium'
    })
  }

  if ((altData.existing_loan_count || 0) > 2) {
    suggestions.push({
      icon: '🔗',
      title: 'Close some existing loans first',
      detail: `You have ${altData.existing_loan_count} active loans. Paying off 1-2 before applying again will significantly improve your debt ratio.`,
      priority: 'high'
    })
  }

  if ((altData.savings_account_balance || 0) < 10000) {
    suggestions.push({
      icon: '💰',
      title: 'Build an emergency savings buffer',
      detail: 'Having ₹10,000+ in savings shows financial stability. Even saving ₹500/month consistently helps your profile.',
      priority: 'medium'
    })
  }

  if ((altData.employment_stability_years || 0) < 1) {
    suggestions.push({
      icon: '📈',
      title: 'Stay in your current job/gig for longer',
      detail: 'Employment stability under 1 year is a risk signal. Staying in the same role for 1-2 years improves your score significantly.',
      priority: 'medium'
    })
  }

  if ((altData.gig_platform_rating || 0) > 0 && (altData.gig_platform_rating || 5) < 4.0) {
    suggestions.push({
      icon: '⭐',
      title: 'Improve your gig platform rating',
      detail: 'A rating below 4.0 hurts your score. Focus on customer satisfaction, on-time deliveries, and completing more orders.',
      priority: 'medium'
    })
  }

  if ((altData.upi_transaction_frequency || 0) < 15) {
    suggestions.push({
      icon: '📱',
      title: 'Use UPI more frequently',
      detail: 'More UPI transactions show active financial participation. Use UPI for daily purchases, groceries, and bill payments.',
      priority: 'low'
    })
  }

  if (creditScore >= 650) {
    suggestions.push({
      icon: '🎯',
      title: 'You\'re close to a low-risk score',
      detail: `Your score of ${Math.round(creditScore)} is ${700 - Math.round(creditScore)} points away from the low-risk threshold (700). Focus on the high-priority items above.`,
      priority: 'low'
    })
  }

  // Always add a general tip
  suggestions.push({
    icon: '🔄',
    title: 'Re-apply after 3-6 months of improvement',
    detail: 'Credit scores respond to consistent behavior over time. Implement these changes and re-apply after 3-6 months for a better outcome.',
    priority: 'low'
  })

  const priorityOrder = { high: 0, medium: 1, low: 2 }
  const sorted = suggestions.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]).slice(0, 6)

  const priorityColors = {
    high: 'bg-red-500/10 text-red-600 border-red-500/20',
    medium: 'bg-amber-500/10 text-amber-600 border-amber-500/20',
    low: 'bg-blue-500/10 text-blue-600 border-blue-500/20',
  }

  return (
    <Card className="mt-6 border-primary/20">
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <Lightbulb className="w-4 h-4 text-amber-500" />
          How to Improve Your Credit Score
        </CardTitle>
        <CardDescription>Personalized suggestions based on your profile</CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {sorted.map((s, i) => (
          <div key={i} className="flex gap-3 p-3 rounded-lg bg-muted/40 border border-border/50">
            <div className="text-xl flex-shrink-0 mt-0.5">{s.icon}</div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1 flex-wrap">
                <span className="text-sm font-semibold">{s.title}</span>
                <Badge variant="outline" className={`text-xs ${priorityColors[s.priority]}`}>
                  {s.priority === 'high' ? '🔴 High Impact' : s.priority === 'medium' ? '🟡 Medium Impact' : '🔵 Good to have'}
                </Badge>
              </div>
              <p className="text-xs text-muted-foreground leading-relaxed">{s.detail}</p>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  )
}

function ScoreExplanation({ explanations }: { explanations: SHAPExplanation[] }) {
  const labels: Record<string, string> = {
    MonthlyIncome: 'Monthly Income', monthly_income_log: 'Income (scaled)',
    DebtRatio: 'Debt Ratio', age: 'Age', NumberOfTimes90DaysLate: 'Severe Late Payments',
    NumberOfOpenCreditLinesAndLoans: 'Credit Lines', total_late_payments: 'Total Late Payments',
  }
  const top = explanations.slice(0, 6)
  const maxAbs = Math.max(...top.map(e => Math.abs(e.shap_value)), 0.01)

  return (
    <Card className="mt-6">
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2"><Info className="w-4 h-4 text-primary" />Why this score? (SHAP Analysis)</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {top.map((exp, i) => {
          const pos = exp.shap_value > 0
          return (
            <div key={i} className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">{labels[exp.feature_name] || exp.feature_name}</span>
              <div className="flex items-center gap-2">
                {pos ? <TrendingUp className="w-3 h-3 text-green-500" /> : <TrendingDown className="w-3 h-3 text-red-500" />}
                <span className={pos ? 'text-green-600 font-medium' : 'text-red-600 font-medium'}>
                  {pos ? '+' : ''}{exp.shap_value.toFixed(1)}
                </span>
                <div className="w-20 h-1.5 bg-muted rounded-full overflow-hidden">
                  <div className={`h-full rounded-full ${pos ? 'bg-green-500' : 'bg-red-500'}`} style={{ width: `${Math.abs(exp.shap_value) / maxAbs * 100}%` }} />
                </div>
              </div>
            </div>
          )
        })}
      </CardContent>
    </Card>
  )
}

export default function ApplicationPage() {
  const navigate = useNavigate()
  const [applicantType, setApplicantType] = useState<'unbanked' | 'underbanked'>('underbanked')
  const [fullName, setFullName] = useState('')
  const [age, setAge] = useState(25)
  const [phoneNumber, setPhoneNumber] = useState('')
  const [address, setAddress] = useState('')
  const [requestedAmount, setRequestedAmount] = useState(50000)
  const [loanPurpose, setLoanPurpose] = useState('')
  const [altData, setAltData] = useState<AlternativeData>({
    monthly_income: 25000, employment_type: 'gig_worker',
    monthly_expenses: 15000, employment_stability_years: 2,
    number_of_dependents: 2, existing_loan_count: 0,
    loan_repayment_history_score: 7, utility_bill_payment_score: 7,
    gig_platform_rating: 4.5, upi_transaction_frequency: 30, savings_account_balance: 10000
  })
  const [docLinks, setDocLinks] = useState({
    income_proof: '',
    employment_proof: '',
    bank_statement: '',
    gig_profile: '',
    utility_bill: '',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState<any>(null)
  const [shap, setShap] = useState<SHAPExplanation[]>([])
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(''); setLoading(true)
    if (!docLinks.income_proof.trim()) {
      setError('Income proof document link is required.')
      setLoading(false)
      return
    }
    const application: CreditApplication = {
      applicant_type: applicantType, full_name: fullName, age,
      phone_number: phoneNumber, address, requested_amount: requestedAmount,
      loan_purpose: loanPurpose, alternative_data: altData,
      document_links: Object.fromEntries(Object.entries(docLinks).filter(([, v]) => v.trim() !== ''))
    }
    try {
      const response = await submitApplication(application)
      setResult(response)
      try {
        const scoreDetail = await getCreditScore(response.application_id)
        setShap(scoreDetail.shap_explanations || [])
      } catch {}
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Application submission failed')
    } finally { setLoading(false) }
  }

  if (result) {
    const score = Math.round(result.credit_score || 0)
    const riskColor = result.risk_category === 'low' ? 'bg-green-500/10 text-green-600 border-green-500/20' :
      result.risk_category === 'medium' ? 'bg-amber-500/10 text-amber-600 border-amber-500/20' :
      'bg-red-500/10 text-red-600 border-red-500/20'

    return (
      <div className="min-h-screen bg-background">
        <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/80 backdrop-blur-xl">
          <div className="container mx-auto px-4 h-16 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-primary-foreground font-bold text-lg">S</div>
              <span className="font-bold text-lg tracking-tight">Saral Credit</span>
            </div>
            <Button variant="ghost" size="sm" onClick={() => navigate('/dashboard')} className="gap-2">
              <ArrowLeft className="w-4 h-4" />Dashboard
            </Button>
          </div>
        </header>
        <main className="container mx-auto px-4 py-8 max-w-2xl">
          <div className="text-center mb-8">
            <div className="w-20 h-20 bg-green-500/10 rounded-full flex items-center justify-center mx-auto text-green-500 mb-6">
              <CheckCircle2 className="w-10 h-10" />
            </div>
            <h2 className="text-3xl font-bold">Application Received</h2>
            <p className="text-muted-foreground mt-2">Here is your AI-generated preliminary credit profile.</p>
          </div>

          <Card className="border-primary/20 bg-primary/5">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">Saral Score</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-end gap-4 mb-4">
                <div className="text-6xl font-bold text-primary">{score}</div>
                <div className="pb-2">
                  <Badge variant="outline" className={riskColor}>{result.risk_category?.toUpperCase()} RISK</Badge>
                </div>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between py-2 border-b border-border/50">
                  <span className="text-muted-foreground">Status</span>
                  <span className="font-medium capitalize">{result.status.replace('_', ' ')}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-border/50">
                  <span className="text-muted-foreground">Application ID</span>
                  <span className="font-medium">#{result.application_id}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-border/50">
                  <span className="text-muted-foreground">Est. Interest Rate</span>
                  <span className="font-medium">{result.risk_category === 'low' ? '12%' : result.risk_category === 'medium' ? '18%' : '24%'} p.a.</span>
                </div>
              </div>
              <p className="text-xs text-muted-foreground mt-4">Your application is under review. You will receive an email once a decision is made.</p>
            </CardContent>
          </Card>

          {shap.length > 0 && <ScoreExplanation explanations={shap} />}
          <ImprovementSuggestions explanations={shap} altData={altData} creditScore={result.credit_score || 0} />
          <EMICalculator loanAmount={result.requested_amount || requestedAmount} />

          <Button className="w-full mt-6" onClick={() => navigate('/dashboard')}>View All Applications →</Button>
        </main>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/80 backdrop-blur-xl">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-primary-foreground font-bold text-lg">S</div>
            <span className="font-bold text-lg tracking-tight">Saral Credit</span>
          </div>
          <Button variant="ghost" size="sm" onClick={() => navigate('/dashboard')} className="gap-2">
            <ArrowLeft className="w-4 h-4" />Dashboard
          </Button>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 max-w-3xl">
        <div className="mb-8">
          <h1 className="text-3xl font-bold tracking-tight">New Credit Application</h1>
          <p className="text-muted-foreground mt-2">Get an instant AI-powered credit decision based on your true financial footprint.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <Card>
            <CardHeader><CardTitle>Basic Profile</CardTitle><CardDescription>Tell us about yourself and what you're building.</CardDescription></CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Applicant Type</Label>
                <Select value={applicantType} onValueChange={(v: any) => setApplicantType(v)}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="underbanked">Digital Earner (UPI / Gig Worker)</SelectItem>
                    <SelectItem value="unbanked">Cash First (Community / Microfinance)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2"><Label>Full Name</Label><Input value={fullName} onChange={e => setFullName(e.target.value)} required /></div>
                <div className="space-y-2"><Label>Age</Label><Input type="number" value={age} onChange={e => setAge(Number(e.target.value))} min={18} max={100} required /></div>
                <div className="space-y-2"><Label>Phone Number</Label><Input type="tel" value={phoneNumber} onChange={e => setPhoneNumber(e.target.value)} required /></div>
                <div className="space-y-2">
                  <Label>Requested Amount (₹)</Label>
                  <Input type="number" value={requestedAmount} onChange={e => setRequestedAmount(Number(e.target.value))} min={1000} required />
                </div>
              </div>
              <div className="space-y-2"><Label>Address</Label><Input value={address} onChange={e => setAddress(e.target.value)} required /></div>
              <div className="space-y-2">
                <Label>Loan Purpose</Label>
                <Select value={loanPurpose} onValueChange={setLoanPurpose} required>
                  <SelectTrigger><SelectValue placeholder="Select purpose" /></SelectTrigger>
                  <SelectContent>
                    {['Business', 'Education', 'Medical', 'Home Improvement', 'Agriculture', 'Vehicle', 'Personal', 'Other'].map(p => (
                      <SelectItem key={p} value={p}>{p}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Financial Footprint</CardTitle><CardDescription>We use alternative data to build your credit profile.</CardDescription></CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Monthly Income (₹)</Label>                <Input type="number" value={altData.monthly_income || ''} onChange={e => setAltData({ ...altData, monthly_income: Number(e.target.value) })} />
              </div>
              <div className="grid md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Monthly Expenses (₹)</Label>
                  <Input type="number" value={altData.monthly_expenses || ''} onChange={e => setAltData({ ...altData, monthly_expenses: Number(e.target.value) })} placeholder="Rent, food, bills..." />
                </div>
                <div className="space-y-2">
                  <Label>Number of Dependents</Label>
                  <Input type="number" value={altData.number_of_dependents ?? ''} onChange={e => setAltData({ ...altData, number_of_dependents: Number(e.target.value) })} min={0} max={20} />
                </div>
                <div className="space-y-2">
                  <Label>Employment Stability (years)</Label>
                  <Input type="number" step="0.5" value={altData.employment_stability_years || ''} onChange={e => setAltData({ ...altData, employment_stability_years: Number(e.target.value) })} min={0} placeholder="Years in current job/gig" />
                </div>
                <div className="space-y-2">
                  <Label>Existing Active Loans</Label>
                  <Input type="number" value={altData.existing_loan_count ?? ''} onChange={e => setAltData({ ...altData, existing_loan_count: Number(e.target.value) })} min={0} placeholder="Number of current loans" />
                </div>
                <div className="space-y-2">
                  <Label>Loan Repayment History (0-10)</Label>
                  <Input type="number" step="0.5" value={altData.loan_repayment_history_score || ''} onChange={e => setAltData({ ...altData, loan_repayment_history_score: Number(e.target.value) })} min={0} max={10} placeholder="10 = always on time" />
                </div>
                <div className="space-y-2">
                  <Label>Utility Bill Payment Score (0-10)</Label>
                  <Input type="number" step="0.5" value={altData.utility_bill_payment_score || ''} onChange={e => setAltData({ ...altData, utility_bill_payment_score: Number(e.target.value) })} min={0} max={10} placeholder="10 = never missed" />
                </div>
              </div>
              {applicantType === 'underbanked' && (
                <div className="grid md:grid-cols-3 gap-4">
                  <div className="space-y-2"><Label>Gig Platform Rating (0-5)</Label><Input type="number" step="0.1" value={altData.gig_platform_rating || ''} onChange={e => setAltData({ ...altData, gig_platform_rating: Number(e.target.value) })} min={0} max={5} /></div>
                  <div className="space-y-2"><Label>UPI Transactions/Month</Label><Input type="number" value={altData.upi_transaction_frequency || ''} onChange={e => setAltData({ ...altData, upi_transaction_frequency: Number(e.target.value) })} /></div>
                  <div className="space-y-2"><Label>Savings Balance (₹)</Label><Input type="number" value={altData.savings_account_balance || ''} onChange={e => setAltData({ ...altData, savings_account_balance: Number(e.target.value) })} /></div>
                </div>
              )}
              {applicantType === 'unbanked' && (
                <div className="grid md:grid-cols-3 gap-4">
                  <div className="space-y-2"><Label>Remittance Frequency/yr</Label><Input type="number" value={altData.remittance_frequency || ''} onChange={e => setAltData({ ...altData, remittance_frequency: Number(e.target.value) })} /></div>
                  <div className="space-y-2"><Label>Community Score (0-10)</Label><Input type="number" step="0.1" value={altData.community_verification_score || ''} onChange={e => setAltData({ ...altData, community_verification_score: Number(e.target.value) })} min={0} max={10} /></div>
                  <div className="space-y-2"><Label>Microfinance Repayments</Label><Input type="number" value={altData.microfinance_repayment_count || ''} onChange={e => setAltData({ ...altData, microfinance_repayment_count: Number(e.target.value) })} /></div>
                </div>
              )}
            </CardContent>
            <CardFooter className="flex flex-col gap-3">
              {error && <p className="text-sm text-destructive w-full">{error}</p>}
              <Button type="submit" className="w-full h-11 text-base" disabled={loading}>
                {loading ? <><Loader2 className="w-5 h-5 animate-spin mr-2" />Processing...</> : 'Submit Application'}
              </Button>
            </CardFooter>
          </Card>

          {/* Supporting Documents Card */}
          <Card className="border-amber-500/30 bg-amber-500/5">
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                📎 Supporting Documents
              </CardTitle>
              <CardDescription>
                Upload your documents to Google Drive / Dropbox, make them publicly accessible, and paste the link here. Income proof is required.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {/* Required */}
              <div className="space-y-1">
                <Label className="text-xs">Income Proof <span className="text-destructive">*</span></Label>
                <Input
                  type="url"
                  placeholder="Salary slip, bank statement link (required)..."
                  value={docLinks.income_proof}
                  onChange={e => setDocLinks({ ...docLinks, income_proof: e.target.value })}
                  className="text-sm"
                  required
                />
              </div>
              {/* Optional */}
              {[
                { key: 'employment_proof', label: 'Employment Proof', placeholder: 'Offer letter, gig platform screenshot...' },
                { key: 'bank_statement', label: 'Bank Statement', placeholder: 'Last 3 months bank statement link...' },
                { key: 'gig_profile', label: 'Gig Platform Profile', placeholder: 'Swiggy/Zomato/Uber profile link...' },
                { key: 'utility_bill', label: 'Utility Bill', placeholder: 'Electricity/water bill link...' },
              ].map(({ key, label, placeholder }) => (
                <div key={key} className="space-y-1">
                  <Label className="text-xs">{label} <span className="text-muted-foreground text-xs">(optional)</span></Label>
                  <Input
                    type="url"
                    placeholder={placeholder}
                    value={docLinks[key as keyof typeof docLinks]}
                    onChange={e => setDocLinks({ ...docLinks, [key]: e.target.value })}
                    className="text-sm"
                  />
                </div>
              ))}
            </CardContent>
          </Card>
        </form>

        <EMICalculator loanAmount={requestedAmount} />
      </main>
    </div>
  )
}
