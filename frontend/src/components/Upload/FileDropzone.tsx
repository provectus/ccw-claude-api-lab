import { useState, useCallback } from 'react';
import type { DragEvent } from 'react';
import {
  Box,
  Chip,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Typography,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import DeleteIcon from '@mui/icons-material/Delete';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';

interface FileDropzoneProps {
  files: File[];
  onFilesAdded: (files: File[]) => void;
  onFileRemoved: (index: number) => void;
  disabled?: boolean;
}

const ACCEPTED_EXTENSIONS = ['.xlsx', '.csv', '.pdf'];

function getFileTypeBadge(filename: string): { label: string; color: 'primary' | 'secondary' | 'info' } {
  const ext = filename.toLowerCase().slice(filename.lastIndexOf('.'));
  if (ext === '.xlsx') return { label: 'NAV Data', color: 'primary' };
  if (ext === '.csv') return { label: 'History/Benchmarks', color: 'secondary' };
  if (ext === '.pdf') return { label: 'Market Commentary', color: 'info' };
  return { label: 'File', color: 'primary' };
}

function formatFileSize(bytes: number): string {
  if (bytes >= 1e6) return `${(bytes / 1e6).toFixed(1)} MB`;
  if (bytes >= 1e3) return `${(bytes / 1e3).toFixed(1)} KB`;
  return `${bytes} B`;
}

function isAcceptedFile(file: File): boolean {
  const ext = file.name.toLowerCase().slice(file.name.lastIndexOf('.'));
  return ACCEPTED_EXTENSIONS.includes(ext);
}

const FileDropzone = ({ files, onFilesAdded, onFileRemoved, disabled = false }: FileDropzoneProps) => {
  const [dragOver, setDragOver] = useState(false);

  const handleDragOver = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) setDragOver(true);
  }, [disabled]);

  const handleDragLeave = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(false);
  }, []);

  const handleDrop = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOver(false);
    if (disabled) return;

    const droppedFiles = Array.from(e.dataTransfer.files).filter(isAcceptedFile);
    if (droppedFiles.length > 0) {
      onFilesAdded(droppedFiles);
    }
  }, [disabled, onFilesAdded]);

  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = Array.from(e.target.files ?? []).filter(isAcceptedFile);
    if (selected.length > 0) {
      onFilesAdded(selected);
    }
    // Reset input so re-selecting the same file works
    e.target.value = '';
  }, [onFilesAdded]);

  return (
    <Box>
      {/* Drop zone */}
      <Box
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => {
          if (!disabled) document.getElementById('file-upload-input')?.click();
        }}
        sx={{
          border: 2,
          borderStyle: 'dashed',
          borderColor: dragOver ? 'secondary.main' : 'divider',
          borderRadius: 2,
          p: 4,
          textAlign: 'center',
          cursor: disabled ? 'default' : 'pointer',
          bgcolor: dragOver ? 'action.hover' : 'transparent',
          transition: 'all 0.2s ease',
          opacity: disabled ? 0.5 : 1,
          '&:hover': disabled ? {} : { borderColor: 'secondary.main', bgcolor: 'action.hover' },
        }}
      >
        <CloudUploadIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
        <Typography variant="body1" color="text.secondary">
          Drag & drop files here, or click to browse
        </Typography>
        <Typography variant="caption" color="text.secondary">
          Accepted: .xlsx, .csv, .pdf
        </Typography>
      </Box>

      <input
        id="file-upload-input"
        type="file"
        multiple
        accept=".xlsx,.csv,.pdf"
        style={{ display: 'none' }}
        onChange={handleInputChange}
      />

      {/* File list */}
      {files.length > 0 && (
        <List dense sx={{ mt: 1 }}>
          {files.map((file, i) => {
            const badge = getFileTypeBadge(file.name);
            return (
              <ListItem
                key={`${file.name}-${i}`}
                secondaryAction={
                  <IconButton
                    edge="end"
                    size="small"
                    onClick={() => onFileRemoved(i)}
                    disabled={disabled}
                  >
                    <DeleteIcon fontSize="small" />
                  </IconButton>
                }
              >
                <ListItemIcon sx={{ minWidth: 36 }}>
                  <InsertDriveFileIcon fontSize="small" />
                </ListItemIcon>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="body2">{file.name}</Typography>
                      <Chip label={badge.label} color={badge.color} size="small" variant="outlined" />
                    </Box>
                  }
                  secondary={formatFileSize(file.size)}
                />
              </ListItem>
            );
          })}
        </List>
      )}
    </Box>
  );
};

export default FileDropzone;
