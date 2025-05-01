import { useRouter } from 'next/router';
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Header from '@/components/NavBar';
import { Card, CardContent, Typography, CircularProgress, Box } from '@mui/material';

interface FileSummary {
  document_id: string;
  pages: number;
  total_words: number;
  total_characters: number;
  summary: string;
}

const FileDetails: React.FC = () => {
  const router = useRouter();
  const { id } = router.query; // Get the File ID from the URL
  const [fileSummary, setFileSummary] = useState<FileSummary | null>(null);
  const [images, setImages] = useState<string[]>([]); // State to store image URLs
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    if (id) {
      const fetchFileSummary = async () => {
        try {
          // Fetch the CSV data and parse it
          const response = await axios.get('http://localhost:8000/outputs/summary/document_summaries.csv');
          const csvData = response.data;

          // Parse CSV into JSON
          const rows = csvData.split('\n').slice(1); // Skip the header row
          const summaries = rows.map((row: string) => {
            const [document_id, pages, total_words, total_characters, summary] = row.split(',');
            return {
              document_id,
              pages: Number(pages),
              total_words: Number(total_words),
              total_characters: Number(total_characters),
              summary: summary?.replace(/"/g, ''), // Remove quotes from the summary
            };
          });

          // Find the summary for the given document ID
          const summary = summaries.find((item) => item.document_id === id);
          setFileSummary(summary || null);
        } catch (error) {
          console.error('Error fetching file summary:', error);
        } finally {
          setLoading(false);
        }
      };

      const fetchImages = async () => {
        try {
          // List of image filenames (static paths)
          const imageFilenames = [
            'sentiment_distribution.png',
            'top_bigrams.png',
            'top_entities.png',
            'top_words.png',
            'wordcloud.png',
          ];
      
          // Generate URLs using the API endpoint and the `id`
          const imagePaths = imageFilenames.map(
            (filename) => `http://localhost:8000/outputs/${id}/${filename}`
          );
      
          setImages(imagePaths);
        } catch (error) {
          console.error('Error fetching images:', error);
        }
      };

      fetchFileSummary();
      fetchImages();
    }
  }, [id]);

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <CircularProgress />
      </div>
    );
  }

  if (!fileSummary) {
    return <p>File summary not found.</p>;
  }

  return (
    <div>
      <Header />
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
        <Card sx={{ width: "100vw", padding: 2, marginBottom: 4 }}>
          <CardContent>
            <Typography variant="h5" component="div" gutterBottom>
              File Summary
            </Typography>
            <Typography variant="body1">
              <strong>ID:</strong> {fileSummary.document_id}
            </Typography>
            <Typography variant="body1">
              <strong>Pages:</strong> {fileSummary.pages}
            </Typography>
            <Typography variant="body1">
              <strong>Total Words:</strong> {fileSummary.total_words}
            </Typography>
            <Typography variant="body1">
              <strong>Total Characters:</strong> {fileSummary.total_characters}
            </Typography>
            <Typography variant="body1" sx={{ marginTop: 2 }}>
              <strong>Summary:</strong> {fileSummary.summary}
            </Typography>
          </CardContent>
        </Card>

        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, justifyContent: 'center' }}>
          {images.map((image, index) => (
            <Card key={index} sx={{ width: 500, height: 500 }}>
              <CardContent sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
                <img
                  src={image} // Construct the image URL
                  alt={`Page ${index + 1}`}
                  style={{ maxWidth: '100%', maxHeight: '100%' }}
                />
              </CardContent>
            </Card>
          ))}
        </Box>
      </div>
    </div>
  );
};

export default FileDetails;