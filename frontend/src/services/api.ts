import axios from 'axios';
import type {
  PipelineRunResponse,
  PipelineStatusResponse,
  PipelineAssessmentResponse,
  PipelineEventsResponse,
  PipelineListResponse,
  ScenariosResponse,
} from '@/types/pipeline';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  headers: { 'Content-Type': 'application/json' },
});

// -- Health --
export const getHealth = () => api.get('/health');

// -- Pipeline --

export interface RunPipelineRequest {
  file_paths?: string[];
  upload_id?: string;
  fund_metadata?: Record<string, unknown>;
}

export const runPipeline = (request: RunPipelineRequest) =>
  api.post<PipelineRunResponse>('/pipeline/run', request);

export const getPipelineStatus = (pipelineId: string) =>
  api.get<PipelineStatusResponse>(`/pipeline/${pipelineId}/status`);

export const getPipelineAssessment = (pipelineId: string) =>
  api.get<PipelineAssessmentResponse>(`/pipeline/${pipelineId}/assessment`);

export const getPipelineEvents = (pipelineId: string) =>
  api.get<PipelineEventsResponse>(`/pipeline/${pipelineId}/events`);

export const listPipelines = () =>
  api.get<PipelineListResponse>('/pipeline/list');

export const getScenarios = () =>
  api.get<ScenariosResponse>('/pipeline/scenarios');

// -- Uploads --
export const uploadFiles = (formData: FormData) =>
  api.post('/uploads', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });

export const listUploads = () => api.get('/uploads');

export const deleteUpload = (uploadId: string) =>
  api.delete(`/uploads/${uploadId}`);

// -- Stats --
export const getStats = () => api.get('/stats');

// -- Schemas --
export const listSchemas = () => api.get('/schemas');

export const getSchema = (name: string) => api.get(`/schemas/${name}`);

export default api;
