import { styled } from '@mui/material/styles';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import { useRouter } from 'next/router';

export default function Header() {
  const router = useRouter();
  return (
    <Box>
      <AppBar position="sticky" sx={{ backgroundColor: '046B99', color: 'white' }}>
        <Toolbar sx={{ justifyContent: 'space-between' }}>
          {/* Left side: AutoPDF, Search, QA */}
          <Box sx={{ display: 'flex', gap: 3, alignItems: 'center' }}>
            <Typography
              variant="h4"
              noWrap
              component="div"
              sx={{ display: { xs: 'none', md: 'block' } }}
              onClick={() => router.push('/')}
            >
              AutoPDF
            </Typography>
            <Typography
              variant="h5"
              noWrap
              component="div"
              sx={{ display: { xs: 'none', md: 'block' } }}
              onClick={() => router.push('/search')}
            >
              Search
            </Typography>
            <Typography
              variant="h5"
              noWrap
              component="div"
              sx={{ display: { xs: 'none', md: 'block' } }}
              onClick={() => router.push('/chat')}
            >
              Chat
            </Typography>
            <Typography
              variant="h5"
              noWrap
              component="div"
              sx={{ display: { xs: 'none', md: 'block' } }}
              onClick={() => router.push('/translate')}
            >
              Translate
            </Typography>
          </Box>

          {/* Right side: DocumentUpload */}
        </Toolbar>
      </AppBar>
    </Box>
  );
}