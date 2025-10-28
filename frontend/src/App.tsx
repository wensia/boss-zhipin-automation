/**
 * 应用主入口
 */
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Toaster } from '@/components/ui/sonner';
import { Layout } from '@/components/layout';
import { Dashboard } from '@/pages/dashboard';
import { Tasks } from '@/pages/tasks';
import { Candidates } from '@/pages/candidates';
import { Templates } from '@/pages/templates';
import { Settings } from '@/pages/settings';
import Logs from '@/pages/logs';

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/tasks" element={<Tasks />} />
          <Route path="/candidates" element={<Candidates />} />
          <Route path="/templates" element={<Templates />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/logs" element={<Logs />} />
        </Routes>
      </Layout>
      <Toaster />
    </BrowserRouter>
  );
}

export default App;
