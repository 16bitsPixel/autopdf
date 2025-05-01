import React, { useState } from 'react';
import axios from 'axios';
import { Box, TextField, Button, Typography, Card, CardContent } from '@mui/material';
import Header from '@/components/NavBar';

const QAChatbot: React.FC = () => {
  const [question, setQuestion] = useState<string>('');
  const [response, setResponse] = useState<string | null>(null);
  const [sources, setSources] = useState<string[] | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleAskQuestion = async () => {
    if (!question.trim()) {
      setError('Please enter a question.');
      return;
    }

    setError(null);
    setLoading(true);
    setResponse(null);
    setSources(null);

    try {
      const res = await axios.post('http://localhost:8000/document-qa', { question });
      const { answer } = res.data;

      // Parse the response to extract the answer and sources
      const [responseText, sourcesText] = answer.split('\nSources: ');
      setResponse(responseText.replace('Response: ', '').trim());
      setSources(sourcesText ? sourcesText.replace(/[\[\]']/g, '').split(', ') : []);
    } catch (err) {
      console.error('Error fetching response:', err);
      setError('Failed to fetch response. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
        <Header />
        <Box sx={{ padding: 4 }}>
        <Typography variant="h4" gutterBottom>
            QA Chatbot
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, marginBottom: 4 }}>
            <TextField
            label="Ask a question"
            variant="outlined"
            fullWidth
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            />
            <Button variant="contained" color="primary" onClick={handleAskQuestion} disabled={loading}>
            {loading ? 'Asking...' : 'Ask'}
            </Button>
        </Box>
        {error && (
            <Typography color="error" sx={{ marginBottom: 2 }}>
            {error}
            </Typography>
        )}
        {response && (
            <Card sx={{ marginBottom: 4 }}>
            <CardContent>
                <Typography variant="h6" gutterBottom>
                Answer
                </Typography>
                <Typography variant="body1">{response}</Typography>
                {sources && sources.length > 0 && (
                <>
                    <Typography variant="h6" gutterBottom sx={{ marginTop: 2 }}>
                    Sources
                    </Typography>
                    <ul>
                    {sources.map((source, index) => (
                        <li key={index}>
                        <Typography variant="body2">{source}</Typography>
                        </li>
                    ))}
                    </ul>
                </>
                )}
            </CardContent>
            </Card>
        )}
        </Box>
    </div>
  );
};

export default QAChatbot;