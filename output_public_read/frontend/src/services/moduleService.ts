import apiClient from './api';
import { ModuleDto } from '../types';

export const moduleService = {
  getAllActiveModules: (): Promise<ModuleDto[]> =>
    apiClient.get('/modules').then((res) => res.data),
};
