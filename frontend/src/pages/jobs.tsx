/**
 * 已沟通职位列表页面
 */
import { useState, useEffect } from 'react';
import { RefreshCw, Briefcase } from 'lucide-react';
import { toast } from 'sonner';

import { useJobs } from '@/hooks/useJobs';
import type { Job } from '@/types';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';

export default function Jobs() {
  const { getJobs, loading } = useJobs();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [total, setTotal] = useState(0);

  /**
   * 加载职位列表
   */
  const loadJobs = async () => {
    try {
      const response = await getJobs();

      if (response.success) {
        setJobs(response.jobs);
        setTotal(response.total);
        toast.success(response.message || '职位列表加载成功');
      } else {
        toast.error(response.message || '加载职位列表失败');
        setJobs([]);
        setTotal(0);
      }
    } catch (error) {
      console.error('加载职位列表失败:', error);
      toast.error('加载职位列表失败，请稍后重试');
      setJobs([]);
      setTotal(0);
    }
  };

  useEffect(() => {
    loadJobs();
  }, []);

  /**
   * 获取职位状态标签
   */
  const getJobStatusBadge = (job: Job) => {
    if (job.jobOnlineStatus === 1) {
      return <Badge variant="default">在线</Badge>;
    }
    return <Badge variant="secondary">离线</Badge>;
  };

  /**
   * 获取职位类型标签
   */
  const getJobTypeLabel = (jobType: number) => {
    const typeMap: Record<number, string> = {
      0: '全职',
      1: '兼职',
      2: '实习',
      3: '劳务外包',
    };
    return typeMap[jobType] || '其他';
  };

  return (
    <div className="space-y-6">
      {/* 头部 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Briefcase className="h-8 w-8 text-primary" />
          <div>
            <h1 className="text-3xl font-bold tracking-tight">已沟通职位</h1>
            <p className="text-muted-foreground">
              查看已经沟通过的职位列表，方便跟进招聘进度
            </p>
          </div>
        </div>
        <Button onClick={loadJobs} disabled={loading}>
          <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
          刷新
        </Button>
      </div>

      {/* 统计卡片 */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">总职位数</CardTitle>
            <Briefcase className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{total}</div>
            <p className="text-xs text-muted-foreground">
              已沟通的职位总数
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">在线职位</CardTitle>
            <Badge variant="default">在线</Badge>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {jobs.filter(job => job.jobOnlineStatus === 1).length}
            </div>
            <p className="text-xs text-muted-foreground">
              当前在线的职位数量
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">离线职位</CardTitle>
            <Badge variant="secondary">离线</Badge>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {jobs.filter(job => job.jobOnlineStatus !== 1).length}
            </div>
            <p className="text-xs text-muted-foreground">
              当前离线的职位数量
            </p>
          </CardContent>
        </Card>
      </div>

      {/* 职位列表 */}
      <Card>
        <CardHeader>
          <CardTitle>职位列表</CardTitle>
          <CardDescription>
            显示所有已经沟通过的职位，包括职位名称、薪资、地址等信息
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
              <span className="ml-3 text-muted-foreground">加载中...</span>
            </div>
          ) : jobs.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <Briefcase className="h-12 w-12 text-muted-foreground mb-4" />
              <p className="text-lg font-medium text-muted-foreground">
                暂无职位数据
              </p>
              <p className="text-sm text-muted-foreground mt-2">
                请先登录并与候选人沟通，才能查看职位列表
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>职位名称</TableHead>
                    <TableHead>薪资</TableHead>
                    <TableHead>地址</TableHead>
                    <TableHead>类型</TableHead>
                    <TableHead>状态</TableHead>
                    <TableHead className="max-w-md">职位描述</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {jobs.map((job) => (
                    <TableRow key={job.encryptJobId}>
                      <TableCell className="font-medium">
                        {job.jobName}
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">{job.salaryDesc}</Badge>
                      </TableCell>
                      <TableCell>{job.address}</TableCell>
                      <TableCell>
                        <Badge variant="secondary">
                          {getJobTypeLabel(job.jobType)}
                        </Badge>
                      </TableCell>
                      <TableCell>{getJobStatusBadge(job)}</TableCell>
                      <TableCell className="max-w-md">
                        <p className="text-sm text-muted-foreground truncate">
                          {job.description || '无描述'}
                        </p>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 底部提示 */}
      {jobs.length > 0 && (
        <Card className="bg-muted/50">
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">
              💡 提示：此列表显示您在 Boss 直聘上已经沟通过的职位。如需更新列表，请点击右上角的刷新按钮。
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
