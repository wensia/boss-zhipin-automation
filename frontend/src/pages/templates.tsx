/**
 * 模板管理页面
 */
import { useEffect, useState } from 'react';
import { toast } from 'sonner';
import { Plus, Trash2, Copy } from 'lucide-react';
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
import { Textarea } from '@/components/ui/textarea';
import { useTemplates } from '@/hooks/useTemplates';
import type { GreetingTemplate, GreetingTemplateCreate } from '@/types';

export function Templates() {
  const {
    getTemplates,
    createTemplate,
    deleteTemplate,
    duplicateTemplate,
    activateTemplate,
    deactivateTemplate,
    loading,
  } = useTemplates();

  const [templates, setTemplates] = useState<GreetingTemplate[]>([]);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [templateToDelete, setTemplateToDelete] = useState<number | null>(null);
  const [newTemplate, setNewTemplate] = useState<GreetingTemplateCreate>({
    name: '',
    content: '',
    is_active: true,
  });

  const loadTemplates = async () => {
    try {
      const data = await getTemplates();
      setTemplates(data);
    } catch (error) {
      console.error('Failed to load templates:', error);
    }
  };

  useEffect(() => {
    loadTemplates();
  }, []);

  const handleCreateTemplate = async () => {
    try {
      await createTemplate(newTemplate);
      setIsCreateDialogOpen(false);
      setNewTemplate({ name: '', content: '', is_active: true });
      await loadTemplates();
    } catch (error) {
      console.error('Failed to create template:', error);
    }
  };

  const handleToggleActive = async (template: GreetingTemplate) => {
    try {
      if (template.is_active) {
        await deactivateTemplate(template.id);
      } else {
        await activateTemplate(template.id);
      }
      await loadTemplates();
    } catch (error) {
      console.error('Failed to toggle template:', error);
    }
  };

  const handleDuplicate = async (id: number) => {
    try {
      await duplicateTemplate(id);
      await loadTemplates();
    } catch (error) {
      console.error('Failed to duplicate template:', error);
    }
  };

  const handleDelete = (id: number) => {
    setTemplateToDelete(id);
    setShowDeleteDialog(true);
  };

  const confirmDelete = async () => {
    if (templateToDelete === null) return;

    try {
      await deleteTemplate(templateToDelete);
      await loadTemplates();
      toast.success('模板已删除');
    } catch (error) {
      console.error('Failed to delete template:', error);
      toast.error('删除失败');
    } finally {
      setShowDeleteDialog(false);
      setTemplateToDelete(null);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">模板管理</h1>
          <p className="text-muted-foreground mt-2">
            管理问候消息模板，支持变量：{'{name}'}, {'{position}'}, {'{company}'}
          </p>
        </div>

        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              创建模板
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[600px]">
            <DialogHeader>
              <DialogTitle>创建新模板</DialogTitle>
              <DialogDescription>创建一个新的问候消息模板</DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="name">模板名称</Label>
                <Input
                  id="name"
                  placeholder="例如：通用问候模板"
                  value={newTemplate.name}
                  onChange={(e) =>
                    setNewTemplate({ ...newTemplate, name: e.target.value })
                  }
                />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="content">模板内容</Label>
                <Textarea
                  id="content"
                  placeholder={`你好 {name}，看到你是 {position}，我们这里有一个很好的机会...`}
                  value={newTemplate.content}
                  onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) =>
                    setNewTemplate({ ...newTemplate, content: e.target.value })
                  }
                  rows={6}
                />
                <p className="text-xs text-muted-foreground">
                  支持变量：{'{name}'} - 姓名, {'{position}'} - 职位,{' '}
                  {'{company}'} - 公司
                </p>
              </div>
            </div>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setIsCreateDialogOpen(false)}
              >
                取消
              </Button>
              <Button onClick={handleCreateTemplate} disabled={loading}>
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
              <TableHead>模板名称</TableHead>
              <TableHead>内容预览</TableHead>
              <TableHead>状态</TableHead>
              <TableHead>使用次数</TableHead>
              <TableHead>创建时间</TableHead>
              <TableHead className="text-right">操作</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {templates.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center text-muted-foreground">
                  暂无模板
                </TableCell>
              </TableRow>
            ) : (
              templates.map((template) => (
                <TableRow key={template.id}>
                  <TableCell className="font-medium">{template.name}</TableCell>
                  <TableCell className="max-w-md">
                    <div className="truncate text-sm text-muted-foreground">
                      {template.content}
                    </div>
                  </TableCell>
                  <TableCell>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleToggleActive(template)}
                    >
                      <span
                        className={`px-2 py-1 rounded text-xs font-medium ${
                          template.is_active
                            ? 'bg-green-100 text-green-700'
                            : 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        {template.is_active ? '已启用' : '已禁用'}
                      </span>
                    </Button>
                  </TableCell>
                  <TableCell>{template.usage_count}</TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {new Date(template.created_at).toLocaleString('zh-CN')}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDuplicate(template.id)}
                      >
                        <Copy className="h-4 w-4" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleDelete(template.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* 删除模板确认对话框 */}
      <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>确认删除模板</AlertDialogTitle>
            <AlertDialogDescription>
              确定要删除这个模板吗？此操作无法撤销。
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>取消</AlertDialogCancel>
            <AlertDialogAction onClick={confirmDelete}>确认删除</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
