import React, { useState, useEffect } from 'react';
import { Box, Card, CardContent, Typography, Button } from '@mui/material';
import { useDocumentContext } from '../context/DocumentContext';
import axios from 'axios';

export default function Documents() {
  const [cards, setCards] = useState<{ id: string; filename: string }[]>([]);
  const [message, setMessage] = useState<string>('');
  const { documents, refreshDocuments } = useDocumentContext();

  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        const response = await axios.get('http://localhost:8000/documents/');
        setCards(response.data);
      } catch (error) {
        console.error('Error fetching documents:', error);
      }
    };

    fetchDocuments();
  }, []);

  const handleDelete = async (id: string) => {
    try {
      await axios.delete('http://localhost:8000/delete_pdf/', {
        data: { id },
      });
      await refreshDocuments(); // Re-fetch after delete
    } catch (error) {
      console.error('Error deleting document:', error.response?.data?.error || error.message);
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
    <Box sx={{ display: 'flex', gap: 2, overflowX: 'auto', padding: 2 }}>
      {documents.map((card) => (
        <Card
          key={card.id}
          sx={{
            width: 200,
            height: 200, // Fixed square size for all cards
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: 1,
          }}
        >
          <CardContent
            sx={{
              width: '100%',
              flexGrow: 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: 1,
            }}
          >
            <Typography
              variant="h6"
              component="div"
              sx={{
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis', // Truncate text with ellipses
                textAlign: 'center',
                width: '100%', // Ensure text stays within the card
              }}
            >
              {card.filename}
            </Typography>
          </CardContent>
          <Button
            variant="contained"
            color="error"
            size="small"
            onClick={() => handleDelete(card.id)}
          >
            Delete
          </Button>
        </Card>
      ))}
    </Box>
  );
}