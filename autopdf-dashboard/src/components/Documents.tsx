import React, { useState, useEffect } from 'react';
import { Box, Card, CardContent, Typography, Button } from '@mui/material';
import { useDocumentContext } from '../context/DocumentContext';
import { useRouter } from 'next/router';
import axios from 'axios';

export default function Documents() {
    const [cards, setCards] = useState<{ id: string; filename: string }[]>([]);
    const [message, setMessage] = useState<string>('');
    const { refreshDocuments } = useDocumentContext();
    const router = useRouter(); // Use Next.js router
  
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
  
    const handleCardClick = (id: string) => {
      router.push(`/documents/${id}`); // Navigate to the new page with the File ID
    };
  
    const handleDelete = async (id: string) => {
      try {
        await axios.delete('http://localhost:8000/delete_pdf/', {
          data: { id },
        });
    
        // Remove the deleted file from the cards state
        setCards((prevCards) => prevCards.filter((card) => card.id !== id));
    
        await refreshDocuments(); // Optionally re-fetch documents if needed
      } catch (error) {
        console.error('Error deleting document:', error.response?.data?.error || error.message);
      }
    };
  
    return (
      <Box sx={{ display: 'flex', gap: 2, overflowX: 'auto', padding: 2 }}>
        {cards.map((card) => (
          <Card
            key={card.id}
            sx={{
              width: 200,
              height: 200,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: 1,
              cursor: 'pointer', // Add pointer cursor for better UX
            }}
            onClick={() => handleCardClick(card.id)} // Add click handler for navigation
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
                  textOverflow: 'ellipsis',
                  textAlign: 'center',
                  width: '100%',
                }}
              >
                {card.filename}
              </Typography>
            </CardContent>
            <Button
              variant="contained"
              color="error"
              size="small"
              onClick={(e) => {
                e.stopPropagation(); // Prevent card click from triggering
                handleDelete(card.id);
              }}
            >
              Delete
            </Button>
          </Card>
        ))}
      </Box>
    );
  }