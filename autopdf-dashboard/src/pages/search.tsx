import React, { useState } from 'react';
import axios from 'axios';
import { Box, TextField, Button, Typography, Card, CardContent } from '@mui/material';
import Header from '@/components/NavBar';

const SemanticSearch: React.FC = () => {
  const [query, setQuery] = useState<string>('');
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async () => {
    if (!query.trim()) {
      setError('Please enter a query.');
      return;
    }

    setError(null);
    setLoading(true);

    try {
      const response = await axios.post('http://localhost:8000/semantic-search', { query });
      setResults(response.data.results);
    } catch (err) {
      console.error('Error fetching search results:', err);
      setError('Failed to fetch search results. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
        <Header />
        <Box sx={{ padding: 4 }}>
            <Typography variant="h4" gutterBottom>
                Search
            </Typography>
            <Box sx={{ display: 'flex', gap: 2, marginBottom: 4 }}>
                <TextField
                label="Enter your query"
                variant="outlined"
                fullWidth
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                />
                <Button variant="contained" color="primary" onClick={handleSearch} disabled={loading}>
                {loading ? 'Searching...' : 'Search'}
                </Button>
            </Box>
            {error && (
                <Typography color="error" sx={{ marginBottom: 2 }}>
                {error}
                </Typography>
            )}
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {results.map((result, index) => (
                <Card key={index} sx={{ padding: 2 }}>
                    <CardContent>
                    <Typography variant="body1" gutterBottom>
                        <strong>Content:</strong> {result.content}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                        <strong>Source:</strong> {result.metadata.source} | <strong>Page:</strong> {result.metadata.page}
                    </Typography>
                    <Typography variant="body2" color="textSecondary">
                        <strong>Score:</strong> {result.score.toFixed(4)}
                    </Typography>
                    </CardContent>
                </Card>
                ))}
            </Box>
        </Box>
    </div>
  );
};

export default SemanticSearch;