import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const api = {
  // Upload image for detection
  detectMedicine: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await axios.post(`${API_BASE_URL}/api/detect`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Camera capture
  processCameraImage: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await axios.post(`${API_BASE_URL}/api/camera`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Search medicine by name
  searchMedicine: async (query) => {
    const response = await axios.get(`${API_BASE_URL}/api/search`, {
      params: { q: query },
    });
    return response.data;
  },

  // Get medicine details
  getMedicineDetails: async (name) => {
    const response = await axios.get(`${API_BASE_URL}/api/medicine/${encodeURIComponent(name)}`);
    return response.data;
  },

  // Translate text to Nepali
  translateText: async (text) => {
    const response = await axios.post(`${API_BASE_URL}/api/translate`, {
      text: text,
    });
    return response.data;
  },

  // Get all medicines list
  getAllMedicines: async () => {
    const response = await axios.get(`${API_BASE_URL}/api/medicines/list`);
    return response.data;
  },

  // Get demo data
  getDemoData: async () => {
    const response = await axios.get(`${API_BASE_URL}/api/demo/paracetamol`);
    return response.data;
  },
};

export default api;
