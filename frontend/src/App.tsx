/**
 * 应用主入口
 */
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Toaster } from '@/components/ui/sonner';
import { Layout } from '@/components/layout';
import { Dashboard } from '@/pages/dashboard';
import { Templates } from '@/pages/templates';
import { Settings } from '@/pages/settings';
import Logs from '@/pages/logs';
import Jobs from '@/pages/jobs';
import AutomationWizard from '@/pages/automation-wizard';
import Accounts from '@/pages/accounts';
import NotificationSettings from '@/pages/notification-settings';
import AutomationTemplates from '@/pages/automation-templates';

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/wizard" element={<AutomationWizard />} />
          <Route path="/accounts" element={<Accounts />} />
          <Route path="/templates" element={<Templates />} />
          <Route path="/automation-templates" element={<AutomationTemplates />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/notification" element={<NotificationSettings />} />
          <Route path="/logs" element={<Logs />} />
          <Route path="/jobs" element={<Jobs />} />
        </Routes>
      </Layout>
      <Toaster />
    </BrowserRouter>
  );
}

export default App;
