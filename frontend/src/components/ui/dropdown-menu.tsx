/**
 * 下拉菜单组件 - 简化版
 */
import * as React from 'react';

interface DropdownMenuProps {
  children: React.ReactNode;
}

interface DropdownMenuTriggerProps {
  children: React.ReactNode;
}

interface DropdownMenuContentProps {
  children: React.ReactNode;
  align?: 'start' | 'center' | 'end';
}

interface DropdownMenuItemProps {
  children: React.ReactNode;
  onClick?: () => void;
  disabled?: boolean;
}

const DropdownMenuContext = React.createContext<{
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
}>({
  isOpen: false,
  setIsOpen: () => {},
});

export function DropdownMenu({ children }: DropdownMenuProps) {
  const [isOpen, setIsOpen] = React.useState(false);
  
  return (
    <DropdownMenuContext.Provider value={{ isOpen, setIsOpen }}>
      <div className="relative inline-block text-left">
        {children}
      </div>
    </DropdownMenuContext.Provider>
  );
}

export function DropdownMenuTrigger({ children }: DropdownMenuTriggerProps) {
  const { isOpen, setIsOpen } = React.useContext(DropdownMenuContext);
  
  return (
    <div onClick={() => setIsOpen(!isOpen)}>
      {children}
    </div>
  );
}

export function DropdownMenuContent({ children, align = 'end' }: DropdownMenuContentProps) {
  const { isOpen, setIsOpen } = React.useContext(DropdownMenuContext);
  const contentRef = React.useRef<HTMLDivElement>(null);
  
  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (contentRef.current && !contentRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    
    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen, setIsOpen]);
  
  if (!isOpen) return null;
  
  const alignClass = align === 'start' ? 'left-0' : align === 'center' ? 'left-1/2 -translate-x-1/2' : 'right-0';
  
  return (
    <div
      ref={contentRef}
      className={`absolute ${alignClass} z-50 mt-2 w-56 rounded-md border bg-white shadow-lg`}
    >
      <div className="py-1">
        {children}
      </div>
    </div>
  );
}

export function DropdownMenuItem({ children, onClick, disabled }: DropdownMenuItemProps) {
  const { setIsOpen } = React.useContext(DropdownMenuContext);

  const handleClick = () => {
    if (!disabled && onClick) {
      onClick();
      setIsOpen(false);
    }
  };

  return (
    <div
      onClick={handleClick}
      className={`flex items-center gap-2 px-4 py-2 text-sm cursor-pointer hover:bg-gray-100 ${
        disabled ? 'opacity-50 cursor-not-allowed' : ''
      }`}
    >
      {children}
    </div>
  );
}

export function DropdownMenuSeparator() {
  return <div className="my-1 h-px bg-gray-200" />;
}
