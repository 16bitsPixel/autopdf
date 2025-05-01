import { styled } from '@mui/material/styles';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import DocumentUpload from './DocumentUpload';

export default function Header() {
  return (
    <Box>
      <AppBar position="sticky" sx={{ backgroundColor: '046B99', color: 'white' }}>
        <Toolbar sx={{ justifyContent: 'space-between' }}>
          {/* Left side: AutoPDF, Search, QA */}
          <Box sx={{ display: 'flex', gap: 5, alignItems: 'center' }}>
            <Typography
              variant="h4"
              noWrap
              component="div"
              sx={{ display: { xs: 'none', md: 'block' } }}
            >
              AutoPDF
            </Typography>
            <Typography
              variant="h5"
              noWrap
              component="div"
              sx={{ display: { xs: 'none', md: 'block' } }}
            >
              Search
            </Typography>
            <Typography
              variant="h5"
              noWrap
              component="div"
              sx={{ display: { xs: 'none', md: 'block' } }}
            >
              QA
            </Typography>
          </Box>

          {/* Right side: DocumentUpload */}
          <DocumentUpload />
        </Toolbar>
      </AppBar>
    </Box>
  );
}