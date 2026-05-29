import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Alert,
  Autocomplete,
  Box,
  Card,
  CardContent,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  TextField,
  Typography,
} from '@mui/material';
import DescriptionIcon from '@mui/icons-material/Description';
import TableChartIcon from '@mui/icons-material/TableChart';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import InsertDriveFileIcon from '@mui/icons-material/InsertDriveFile';
import type { DemoScenario } from '@/types/pipeline';
import type { FundMetadata } from '@/types';
import { getScenarios, runPipeline } from '@/services/api';
import { usePipelineStore } from '@/stores/pipelineStore';
import { useUploadStore } from '@/stores/uploadStore';
import FileDropzone from './FileDropzone';
import FundMetadataForm from './FundMetadataForm';

function fileIcon(filename: string) {
  const ext = filename.split('.').pop()?.toLowerCase() ?? '';
  if (ext === 'pdf') return <PictureAsPdfIcon color="error" />;
  if (['xlsx', 'xls', 'csv'].includes(ext)) return <TableChartIcon color="success" />;
  if (['doc', 'docx'].includes(ext)) return <DescriptionIcon color="primary" />;
  return <InsertDriveFileIcon color="action" />;
}

const UploadPage = () => {
  const navigate = useNavigate();
  const startPipeline = usePipelineStore((s) => s.startPipeline);

  const files = useUploadStore((s) => s.files);
  const addFiles = useUploadStore((s) => s.addFiles);
  const removeFile = useUploadStore((s) => s.removeFile);
  const scenario = useUploadStore((s) => s.scenario);
  const setScenario = useUploadStore((s) => s.setScenario);
  const uploading = useUploadStore((s) => s.uploading);
  const uploadError = useUploadStore((s) => s.error);

  const [scenarios, setScenarios] = useState<DemoScenario[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getScenarios()
      .then((res) => setScenarios(res.data.scenarios))
      .catch(() => {});
  }, []);

  const handleScenarioChange = useCallback(
    (_: unknown, value: DemoScenario | null) => {
      setScenario(value);
      setError(null);
    },
    [setScenario],
  );

  const handleSubmit = useCallback(
    async (metadata: FundMetadata) => {
      setSubmitting(true);
      setError(null);

      try {
        if (scenario) {
          const res = await runPipeline({
            file_paths: scenario.file_paths,
            fund_metadata: { ...metadata, ...scenario.fund_metadata },
          });
          startPipeline(res.data.pipeline_id);
          navigate('/review');
        } else if (files.length > 0) {
          const uploadId = await useUploadStore.getState().uploadFiles(metadata);
          const res = await runPipeline({
            upload_id: uploadId,
            fund_metadata: metadata as unknown as Record<string, unknown>,
          });
          startPipeline(res.data.pipeline_id);
          navigate('/review');
        } else {
          setError('Please select a demo scenario or upload files.');
        }
      } catch (err) {
        const msg = err instanceof Error ? err.message : 'Failed to start review';
        setError(msg);
      } finally {
        setSubmitting(false);
      }
    },
    [scenario, files, startPipeline, navigate],
  );

  const initialFormValues: Partial<FundMetadata> | undefined = scenario?.fund_metadata
    ? {
        fund_name: (scenario.fund_metadata.fund_name as string) ?? '',
        fund_type: (scenario.fund_metadata.fund_type as FundMetadata['fund_type']) ?? 'HedgeFund',
        strategy: (scenario.fund_metadata.strategy as string) ?? '',
        base_currency: (scenario.fund_metadata.base_currency as string) ?? 'USD',
        nav_date: (scenario.fund_metadata.nav_date as string) ?? '',
        reported_aum: (scenario.fund_metadata.reported_aum as number) ?? null,
      }
    : undefined;

  const hasInput = scenario !== null || files.length > 0;

  return (
    <Box sx={{ maxWidth: 900, mx: 'auto' }}>
      <Typography variant="h5" fontWeight={600} gutterBottom>
        Fund Data Upload
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Upload fund NAV data files or select a pre-configured demo scenario to start the review pipeline.
      </Typography>

      {(error || uploadError) && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error || uploadError}
        </Alert>
      )}

      {scenarios.length > 0 && (
        <Card variant="outlined" sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1.5 }}>
              Demo Scenario
            </Typography>
            <Autocomplete
              options={scenarios}
              getOptionLabel={(s) => s.name}
              value={scenario}
              onChange={handleScenarioChange}
              renderInput={(params) => (
                <TextField
                  {...params}
                  size="small"
                  placeholder="Select a pre-configured demo scenario..."
                />
              )}
              renderOption={(props, option) => {
                const { key, ...rest } = props;
                return (
                  <li key={key} {...rest}>
                    <Box>
                      <Typography variant="body2" fontWeight={600}>{option.name}</Typography>
                      <Typography variant="caption" color="text.secondary">{option.description}</Typography>
                    </Box>
                  </li>
                );
              }}
              isOptionEqualToValue={(a, b) => a.id === b.id}
            />
          </CardContent>
        </Card>
      )}

      {scenario ? (
        <Card variant="outlined" sx={{ mb: 3 }}>
          <CardContent sx={{ pb: '12px !important' }}>
            <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 0.5 }}>
              Included Files
            </Typography>
            <List dense disablePadding>
              {scenario.file_paths.map((fp) => {
                const name = fp.split('/').pop() ?? fp;
                return (
                  <ListItem key={fp} disableGutters sx={{ py: 0.25 }}>
                    <ListItemIcon sx={{ minWidth: 36 }}>{fileIcon(name)}</ListItemIcon>
                    <ListItemText
                      primary={name}
                      primaryTypographyProps={{ variant: 'body2' }}
                    />
                  </ListItem>
                );
              })}
            </List>
          </CardContent>
        </Card>
      ) : (
        <Card variant="outlined" sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="subtitle1" fontWeight={600} sx={{ mb: 1.5 }}>
              Upload Files
            </Typography>
            <FileDropzone
              files={files}
              onFilesAdded={addFiles}
              onFileRemoved={removeFile}
              disabled={uploading || submitting}
            />
          </CardContent>
        </Card>
      )}

      <Divider sx={{ mb: 3 }} />

      <Card variant="outlined">
        <CardContent>
          <FundMetadataForm
            key={scenario?.id ?? 'manual'}
            onSubmit={handleSubmit}
            initialValues={initialFormValues}
            submitLabel={scenario ? `Review: ${scenario.name}` : 'Upload & Review'}
            submitting={submitting || uploading}
            disabled={!hasInput}
          />
        </CardContent>
      </Card>
    </Box>
  );
};

export default UploadPage;
