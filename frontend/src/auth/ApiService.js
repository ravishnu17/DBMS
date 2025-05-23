import { axiosInstance } from "./authInstance";

//post,put
export const addUpdateAPI = async (method,url,data, config ={})=> {
    try {
        if(method === "PUT"){
            const response = await axiosInstance.put(url,data, config);
            return response
        }
        else if(method === "POST"){
            const response = await axiosInstance.post(url,data, config);
            return response
        }
    } catch (error) {
      console.error('API Error:', error);
    }
  };
  
//get
export const getAPI = async (url)=> {
    try {
      const response = await axiosInstance.get(url);
      return response
    } catch (error) {
      console.error('API Error:', error);
    }
  };

//delete
export const deleteAPI = async (url)=> {
    try {
      const response = await axiosInstance.delete(url);
      return response
    } catch (error) {
      console.error('API Error:', error);
    }
  };
