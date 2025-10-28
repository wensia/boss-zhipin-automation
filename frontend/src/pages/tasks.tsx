/**
 * 任务管理页面
 */
import { useEffect, useState } from 'react';
import { toast } from 'sonner';
import { Plus, Play, Pause, X, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { useAutomation } from '@/hooks/useAutomation';
import { useTemplates } from '@/hooks/useTemplates';
import type { AutomationTask, AutomationTaskCreate, TaskStatus } from '@/types';

export function Tasks() {
  const {
    getTasks,
    createTask,
    startTask,
    pauseTask,
    cancelTask,
    deleteTask,
    loading,
  } = useAutomation();
  const { getActiveTemplates } = useTemplates();

  const [tasks, setTasks] = useState<AutomationTask[]>([]);
  const [templates, setTemplates] = useState<any[]>([]);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [taskToDelete, setTaskToDelete] = useState<number | null>(null);
  const [newTask, setNewTask] = useState<AutomationTaskCreate>({
    search_keywords: '',
    greeting_template_id: 0,
    max_contacts: 50,
    delay_min: 2,
    delay_max: 5,
  });

  const loadTasks = async () => {
    try {
      const data = await getTasks();
      setTasks(data);
    } catch (error) {
      console.error('Failed to load tasks:', error);
    }
  };

  const loadTemplates = async () => {
    try {
      const data = await getActiveTemplates();
      setTemplates(data);
    } catch (error) {
      console.error('Failed to load templates:', error);
    }
  };

  useEffect(() => {
    loadTasks();
    loadTemplates();

    // 每 5 秒刷新一次任务状态
    const interval = setInterval(loadTasks, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleCreateTask = async () => {
    try {
      await createTask(newTask);
      setIsCreateDialogOpen(false);
      setNewTask({
        search_keywords: '',
        greeting_template_id: 0,
        max_contacts: 50,
        delay_min: 2,
        delay_max: 5,
      });
      await loadTasks();
    } catch (error) {
      console.error('Failed to create task:', error);
    }
  };

  const handleStartTask = async (id: number) => {
    try {
      await startTask(id);
      await loadTasks();
    } catch (error) {
      console.error('Failed to start task:', error);
    }
  };

  const handlePauseTask = async (id: number) => {
    try {
      await pauseTask(id);
      await loadTasks();
    } catch (error) {
      console.error('Failed to pause task:', error);
    }
  };

  const handleCancelTask = async (id: number) => {
    try {
      await cancelTask(id);
      await loadTasks();
    } catch (error) {
      console.error('Failed to cancel task:', error);
    }
  };

  const handleDeleteTask = (id: number) => {
    setTaskToDelete(id);
    setShowDeleteDialog(true);
  };

  const confirmDeleteTask = async () => {
    if (taskToDelete === null) return;

    try {
      await deleteTask(taskToDelete);
      await loadTasks();
      toast.success('任务已删除');
    } catch (error) {
      console.error('Failed to delete task:', error);
      toast.error('删除失败');
    } finally {
      setShowDeleteDialog(false);
      setTaskToDelete(null);
    }
  };

  const getStatusBadge = (status: TaskStatus) => {
    const statusConfig = {
      pending: { label: '待处理', className: 'bg-gray-100 text-gray-700' },
      running: { label: '运行中', className: 'bg-blue-100 text-blue-700' },
      paused: { label: '已暂停', className: 'bg-yellow-100 text-yellow-700' },
      completed: { label: '已完成', className: 'bg-green-100 text-green-700' },
      failed: { label: '失败', className: 'bg-red-100 text-red-700' },
      cancelled: { label: '已取消', className: 'bg-gray-100 text-gray-700' },
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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">任务管理</h1>
          <p className="text-muted-foreground mt-2">管理自动化招聘任务</p>
        </div>

        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              创建任务
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[500px]">
            <DialogHeader>
              <DialogTitle>创建新任务</DialogTitle>
              <DialogDescription>
                填写任务信息，系统将自动搜索候选人并发送问候消息
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="keywords">搜索关键词</Label>
                <Input
                  id="keywords"
                  placeholder="例如：Python开发工程师"
                  value={newTask.search_keywords}
                  onChange={(e) =>
                    setNewTask({ ...newTask, search_keywords: e.target.value })
                  }
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="template">问候模板</Label>
                <Select
                  value={newTask.greeting_template_id.toString()}
                  onValueChange={(value: string) =>
                    setNewTask({
                      ...newTask,
                      greeting_template_id: parseInt(value),
                    })
                  }
                >
                  <SelectTrigger id="template">
                    <SelectValue placeholder="选择模板" />
                  </SelectTrigger>
                  <SelectContent>
                    {templates.map((template) => (
                      <SelectItem key={template.id} value={template.id.toString()}>
                        {template.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="grid gap-2">
                <Label htmlFor="max_contacts">最大联系数</Label>
                <Input
                  id="max_contacts"
                  type="number"
                  min="1"
                  max="200"
                  value={newTask.max_contacts}
                  onChange={(e) =>
                    setNewTask({
                      ...newTask,
                      max_contacts: parseInt(e.target.value),
                    })
                  }
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="delay_min">最小延迟（秒）</Label>
                  <Input
                    id="delay_min"
                    type="number"
                    min="1"
                    max="10"
                    value={newTask.delay_min}
                    onChange={(e) =>
                      setNewTask({
                        ...newTask,
                        delay_min: parseInt(e.target.value),
                      })
                    }
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="delay_max">最大延迟（秒）</Label>
                  <Input
                    id="delay_max"
                    type="number"
                    min="2"
                    max="30"
                    value={newTask.delay_max}
                    onChange={(e) =>
                      setNewTask({
                        ...newTask,
                        delay_max: parseInt(e.target.value),
                      })
                    }
                  />
                </div>
              </div>
            </div>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setIsCreateDialogOpen(false)}
              >
                取消
              </Button>
              <Button onClick={handleCreateTask} disabled={loading}>
                创建
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>关键词</TableHead>
              <TableHead>状态</TableHead>
              <TableHead>进度</TableHead>
              <TableHead>找到/联系/成功</TableHead>
              <TableHead>创建时间</TableHead>
              <TableHead className="text-right">操作</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {tasks.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="text-center text-muted-foreground">
                  暂无任务
                </TableCell>
              </TableRow>
            ) : (
              tasks.map((task) => (
                <TableRow key={task.id}>
                  <TableCell className="font-medium">{task.id}</TableCell>
                  <TableCell>{task.search_keywords}</TableCell>
                  <TableCell>{getStatusBadge(task.status)}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-blue-500 transition-all"
                          style={{ width: `${task.progress}%` }}
                        />
                      </div>
                      <span className="text-sm text-muted-foreground">
                        {task.progress}%
                      </span>
                    </div>
                  </TableCell>
                  <TableCell className="text-sm">
                    {task.total_found} / {task.total_contacted} /{' '}
                    {task.total_success}
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {new Date(task.created_at).toLocaleString('zh-CN')}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-2">
                      {task.status === 'pending' && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleStartTask(task.id)}
                        >
                          <Play className="h-4 w-4" />
                        </Button>
                      )}
                      {task.status === 'running' && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handlePauseTask(task.id)}
                        >
                          <Pause className="h-4 w-4" />
                        </Button>
                      )}
                      {(task.status === 'pending' ||
                        task.status === 'running' ||
                        task.status === 'paused') && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleCancelTask(task.id)}
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      )}
                      {task.status !== 'running' && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDeleteTask(task.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* 删除任务确认对话框 */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>确认删除任务</AlertDialogTitle>
            <AlertDialogDescription>
              确定要删除这个任务吗？此操作无法撤销。
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>取消</AlertDialogCancel>
            <AlertDialogAction onClick={confirmDeleteTask}>确认删除</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
