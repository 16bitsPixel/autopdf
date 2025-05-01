import React, { useState } from 'react';
import axios from 'axios';
import { Box, Button, Typography, CircularProgress } from '@mui/material';
import Header from '@/components/NavBar';

const TranslatePDF: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [translatedFileUrl, setTranslatedFileUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files[0]) {
      setFile(event.target.files[0]);
      setTranslatedFileUrl(null); // Reset the translated file URL
      setError(null); // Clear any previous errors
    }
  };

  const handleTranslate = async () => {
    if (!file) {
      setError('Please select a PDF file to upload.');
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/translate-pdf', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        responseType: 'blob', // Ensure the response is treated as a file
      });

      // Create a URL for the translated file
      const url = window.URL.createObjectURL(new Blob([response.data]));
      setTranslatedFileUrl(url);
    } catch (err) {
      console.error('Error translating PDF:', err);
      setError('Failed to translate the PDF. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
        <Header />
        <Box sx={{ padding: 4, textAlign: 'center' }}>
        <Typography variant="h4" gutterBottom>
            Translate PDF to Spanish
        </Typography>
        <Box sx={{ marginBottom: 2 }}>
            <input
            type="file"
            accept="application/pdf"
            onChange={handleFileChange}
            style={{ marginBottom: '16px' }}
            />
        </Box>
        <Button
            variant="contained"
            color="primary"
            onClick={handleTranslate}
            disabled={loading || !file}
        >
            {loading ? <CircularProgress size={24} /> : 'Translate PDF'}
        </Button>
        {error && (
            <Typography color="error" sx={{ marginTop: 2 }}>
            {error}
            </Typography>
        )}
        {translatedFileUrl && (
            <Box sx={{ marginTop: 4 }}>
            <Typography variant="h6" gutterBottom>
                Translation Complete!
            </Typography>
            <Button
                variant="contained"
                color="secondary"
                href={translatedFileUrl}
                download="translated_output.pdf"
            >
                Download Translated PDF
            </Button>
            </Box>
        )}
        </Box>
    </div>
  );
};

export default TranslatePDF;