import apiClient from './api';
import { PageDto } from '../types';

export const pageService = {
  getPageByFileName: (fileName: string): Promise<PageDto> =>
    apiClient.get(`/pages/${fileName}`).then((res) => res.data),

  getAllActivePages: (): Promise<PageDto[]> =>
    apiClient.get('/pages').then((res) => res.data),
};
