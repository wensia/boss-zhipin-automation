import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Package, Play, Trash2, Copy, Calendar, TrendingUp } from 'lucide-react';
import { toast } from 'sonner';
import { useAutomationTemplates } from '@/hooks/useAutomationTemplates';
import type { AutomationTemplate } from '@/types/template';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
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

export default function AutomationTemplates() {
  const navigate = useNavigate();
  const { templates, loading, fetchTemplates, deleteTemplate, duplicateTemplate } = useAutomationTemplates();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [templateToDelete, setTemplateToDelete] = useState<AutomationTemplate | null>(null);

  useEffect(() => { fetchTemplates(); }, [fetchTemplates]);

  const handleDelete = async () => {
    if (!templateToDelete) return;
    try {
      await deleteTemplate(templateToDelete.id);
      toast.success('Template deleted');
      setDeleteDialogOpen(false);
      setTemplateToDelete(null);
    } catch (error) {
      toast.error('Failed to delete');
    }
  };

  const handleDuplicate = async (template: AutomationTemplate) => {
    try {
      await duplicateTemplate(template.id);
      toast.success('Template duplicated');
    } catch (error) {
      toast.error('Failed to duplicate');
    }
  };

  const handleRun = (template: AutomationTemplate) => {
    sessionStorage.setItem('selectedTemplate', JSON.stringify(template));
    navigate('/wizard');
    toast.info('Template loaded, please continue in wizard');
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('zh-CN');
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Package className="h-8 w-8 text-primary" />
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Automation Templates</h1>
            <p className="text-muted-foreground">Manage and reuse your automation configurations</p>
          </div>
        </div>
        <Button onClick={() => navigate('/wizard')}>Create New Template</Button>
      </div>

      {loading ? (
        <Card><CardContent className="py-12 text-center">Loading...</CardContent></Card>
      ) : templates.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Package className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <p className="text-muted-foreground mb-4">No templates yet</p>
            <Button onClick={() => navigate('/wizard')}>Create First Template</Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {templates.map((template) => (
            <Card key={template.id} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {template.name}
                  {template.usage_count > 5 && (
                    <Badge variant="secondary" className="text-xs">
                      <TrendingUp className="h-3 w-3 mr-1" />Popular
                    </Badge>
                  )}
                </CardTitle>
                {template.description && <CardDescription>{template.description}</CardDescription>}
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="text-sm space-y-1">
                  {template.job_name && <div><span className="font-medium">Job:</span> {template.job_name}</div>}
                  <div><span className="font-medium">Greetings:</span> {template.greeting_count}</div>
                  {template.expected_positions && template.expected_positions.length > 0 && (
                    <div><span className="font-medium">Positions:</span> {template.expected_positions.join(', ')}</div>
                  )}
                </div>
                <div className="flex items-center gap-4 text-xs text-muted-foreground pt-2 border-t">
                  <div className="flex items-center gap-1">
                    <Calendar className="h-3 w-3" />
                    <span>{formatDate(template.created_at)}</span>
                  </div>
                  <div>Used {template.usage_count} times</div>
                </div>
                <div className="flex gap-2 pt-2">
                  <Button size="sm" className="flex-1" onClick={() => handleRun(template)}>
                    <Play className="h-4 w-4 mr-1" />Run
                  </Button>
                  <Button size="sm" variant="outline" onClick={() => handleDuplicate(template)}>
                    <Copy className="h-4 w-4" />
                  </Button>
                  <Button size="sm" variant="outline" onClick={() => {
                    setTemplateToDelete(template);
                    setDeleteDialogOpen(true);
                  }}>
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Confirm Delete</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete "{templateToDelete?.name}"? This cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleDelete}>Delete</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
