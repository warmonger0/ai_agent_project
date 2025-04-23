import api from './api';

export const fetchHealthStatus = async () => {
  const response = await api.get('/health');
  return response.data;
};
