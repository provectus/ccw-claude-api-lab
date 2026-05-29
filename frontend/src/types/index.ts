// Re-export pipeline types
export * from './pipeline';

/** Uploaded file metadata. */
export interface UploadedFile {
  id: string;
  filename: string;
  size: number;
  mimeType: string;
  uploadedAt: string;
}

/** An upload set (one or more files submitted together). */
export interface Upload {
  id: string;
  files: UploadedFile[];
  createdAt: string;
}

/** Dashboard statistics (matches GET /api/stats response). */
export interface DashboardStats {
  pipelines_run: number;
  pipelines_completed: number;
  files_processed: number;
  records_validated: number;
  avg_completion_time_seconds: number;
  last_run: string | null;
}

/** Fund metadata for upload form. */
export interface FundMetadata {
  fund_name: string;
  fund_type: 'HedgeFund' | 'PrivateEquity' | 'RealAssets' | 'Traditional';
  strategy: string;
  base_currency: string;
  nav_date: string;
  reported_aum: number | null;
}
