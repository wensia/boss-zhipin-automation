/**
 * 候选人列表页面
 */
import { useEffect, useState } from 'react';
import { Search } from 'lucide-react';
import { Input } from '@/components/ui/input';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useCandidates } from '@/hooks/useCandidates';
import type { Candidate, CandidateStatus } from '@/types';

export function Candidates() {
  const { getCandidates, loading } = useCandidates();
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<CandidateStatus | ''>('');

  const loadCandidates = async () => {
    try {
      const params: any = {};
      if (statusFilter) params.status = statusFilter;
      if (searchQuery) params.search = searchQuery;

      const data = await getCandidates(params);
      setCandidates(data);
    } catch (error) {
      console.error('Failed to load candidates:', error);
    }
  };

  useEffect(() => {
    loadCandidates();
  }, [statusFilter]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    loadCandidates();
  };

  const getStatusBadge = (status: CandidateStatus) => {
    const statusConfig = {
      new: { label: '新候选人', className: 'bg-blue-100 text-blue-700' },
      contacted: { label: '已联系', className: 'bg-green-100 text-green-700' },
      replied: { label: '已回复', className: 'bg-purple-100 text-purple-700' },
      interested: { label: '感兴趣', className: 'bg-yellow-100 text-yellow-700' },
      rejected: { label: '已拒绝', className: 'bg-red-100 text-red-700' },
      archived: { label: '已归档', className: 'bg-gray-100 text-gray-700' },
    };

    const config = statusConfig[status];
    return (
      <span className={`px-2 py-1 rounded text-xs font-medium ${config.className}`}>
        {config.label}
      </span>
    );
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">候选人管理</h1>
        <p className="text-muted-foreground mt-2">查看和管理所有候选人信息</p>
      </div>

      <div className="flex gap-4">
        <form onSubmit={handleSearch} className="flex-1 flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              placeholder="搜索姓名、职位、公司..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>
        </form>
        <Select
          value={statusFilter}
          onValueChange={(value: string) => setStatusFilter(value as CandidateStatus | '')}
        >
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="筛选状态" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="">全部</SelectItem>
            <SelectItem value="new">新候选人</SelectItem>
            <SelectItem value="contacted">已联系</SelectItem>
            <SelectItem value="replied">已回复</SelectItem>
            <SelectItem value="interested">感兴趣</SelectItem>
            <SelectItem value="rejected">已拒绝</SelectItem>
            <SelectItem value="archived">已归档</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>姓名</TableHead>
              <TableHead>职位</TableHead>
              <TableHead>公司</TableHead>
              <TableHead>状态</TableHead>
              <TableHead>活跃时间</TableHead>
              <TableHead>添加时间</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading && candidates.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center text-muted-foreground">
                  加载中...
                </TableCell>
              </TableRow>
            ) : candidates.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center text-muted-foreground">
                  暂无候选人
                </TableCell>
              </TableRow>
            ) : (
              candidates.map((candidate) => (
                <TableRow key={candidate.id}>
                  <TableCell className="font-medium">{candidate.name}</TableCell>
                  <TableCell>{candidate.position}</TableCell>
                  <TableCell>{candidate.company || '-'}</TableCell>
                  <TableCell>{getStatusBadge(candidate.status)}</TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {candidate.active_time || '-'}
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {new Date(candidate.created_at).toLocaleString('zh-CN')}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
