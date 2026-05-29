// Upload state management (session-only, not persisted)

import { create } from 'zustand';
import type { DemoScenario } from '@/types/pipeline';
import type { FundMetadata } from '@/types';
import { uploadFiles as uploadFilesApi } from '@/services/api';

interface UploadState {
  files: File[];
  uploadId: string | null;
  uploading: boolean;
  error: string | null;
  scenario: DemoScenario | null;
}

interface UploadActions {
  setFiles: (files: File[]) => void;
  addFiles: (files: File[]) => void;
  removeFile: (index: number) => void;
  setScenario: (scenario: DemoScenario | null) => void;
  uploadFiles: (metadata: FundMetadata) => Promise<string>;
  clearFiles: () => void;
  reset: () => void;
}

type UploadStore = UploadState & UploadActions;

const initialState: UploadState = {
  files: [],
  uploadId: null,
  uploading: false,
  error: null,
  scenario: null,
};

export const useUploadStore = create<UploadStore>()((set, get) => ({
  ...initialState,

  setFiles: (files) => set({ files, error: null }),

  addFiles: (newFiles) =>
    set((state) => ({ files: [...state.files, ...newFiles], error: null })),

  removeFile: (index) =>
    set((state) => ({
      files: state.files.filter((_, i) => i !== index),
    })),

  setScenario: (scenario) => set({ scenario }),

  uploadFiles: async (metadata: FundMetadata) => {
    const { files } = get();
    set({ uploading: true, error: null });
    try {
      const formData = new FormData();
      for (const file of files) {
        formData.append('files', file);
      }
      // Attach metadata as a JSON field
      formData.append('metadata', JSON.stringify(metadata));

      const res = await uploadFilesApi(formData);
      const uploadId = res.data.upload_id;
      set({ uploadId, uploading: false });
      return uploadId;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Upload failed';
      set({ uploading: false, error: message });
      throw err;
    }
  },

  clearFiles: () => set({ files: [], uploadId: null, error: null }),

  reset: () => set(initialState),
}));
