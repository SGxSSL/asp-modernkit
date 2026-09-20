import apiClient from './api';

export const settingsService = {
  getAllSettings: (): Promise<Record<string, string>> =>
    apiClient.get('/settings').then((res) => res.data),
};
