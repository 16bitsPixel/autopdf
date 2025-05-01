import React, { useState, useEffect } from 'react';
import { Box, Card, CardMedia, Typography } from '@mui/material';
import axios from 'axios';

export default function SummaryVisualizer() {
  const [images, setImages] = useState<string[]>([]);

  useEffect(() => {
    const fetchImages = async () => {
      try {
        // List of image filenames
        const imageFilenames = [
          'summary/overall_sentiment_distribution.png',
          'summary/overall_top_entities.png',
        ];

        // Generate URLs using the API endpoint
        const imagePaths = imageFilenames.map(
          (filename) => `http://localhost:8000/outputs/${filename}`
        );

        setImages(imagePaths);
      } catch (error) {
        console.error('Error fetching images:', error);
      }
    };

    fetchImages();
  }, []);

  return (
    <Card sx={{ padding: 3, margin: 2}}> {/* Single container */}
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
        {images.map((image, index) => (
          <Card key={index} sx={{ }}>
            <CardMedia
              component="img"
              height="500"
              image={image}
              alt={`Summary Image ${index + 1}`}
            />
          </Card>
        ))}
      </Box>
    </Card>
  );
}