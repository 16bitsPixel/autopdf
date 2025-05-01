import React, { useState } from 'react';
import axios from 'axios';
import { useDocumentContext } from '../context/DocumentContext';

const DocumentUpload: React.FC = () => {
    const [file, setFile] = useState<File | null>(null);
    const [message, setMessage] = useState<string>('');
    const [documentIds, setDocumentIds] = useState<string[]>([]);
    const { refreshDocuments } = useDocumentContext();

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = event.target.files?.[0];
        if (selectedFile) {
            setFile(selectedFile);
        }
    };

    const handleUpload = async () => {
        if (!file) {
          setMessage('Please select a file to upload.');
          return;
        }
      
        const formData = new FormData();
        formData.append('file', file);
      
        try {
          const response = await axios.post('http://localhost:8000/upload_pdf/', formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          });
          setMessage(response.data.message);
          console.log('Uploaded PDF ID:', response.data.id);
      
          await refreshDocuments(); // 💡 Refresh Documents here
      
          // Optionally also run EDA
          await runBatchEDA([response.data.id]);
        } catch (error) {
          setMessage('Error uploading file: ' + (error.response?.data?.error || error.message));
        }
      };

    const fetchDocumentIds = async () => {
        try {
            const response = await axios.get('http://localhost:8000/documents/');
            const ids = response.data.map((doc: { id: string }) => doc.id);
            setDocumentIds(ids);
            setMessage('Retrieved document IDs successfully.');
            console.log('Document IDs:', ids);

            // Run Batch EDA after fetching document IDs
            await runBatchEDA(ids);
        } catch (error) {
            setMessage('Error fetching document IDs: ' + (error.response?.data?.error || error.message));
        }
    };

    const runBatchEDA = async (ids: string[]) => {
        if (ids.length === 0) {
            setMessage('No document IDs available to run EDA.');
            return;
        }
    
        try {
            console.log('Sending document IDs to /run_batch_eda/:', ids); // Debugging log
            const response = await axios.post(
                'http://localhost:8000/run_batch_eda/',
                ids, // Send the array directly
                {
                    headers: {
                        'Content-Type': 'application/json', // Explicitly set the content type
                    },
                }
            );
            setMessage(response.data.message);
            console.log('Batch EDA Results:', response.data.document_stats);
        } catch (error) {
            console.error('Error running batch EDA:', error.response?.data || error.message);
            setMessage('Error running batch EDA: ' + (error.response?.data?.error || error.message));
        }
    };

    return (
        <div>
            <input type="file" accept="application/pdf" onChange={handleFileChange} />
            <button onClick={handleUpload}>Upload</button>
            {message && <p>{message}</p>}
        </div>
    );
};

export default DocumentUpload;