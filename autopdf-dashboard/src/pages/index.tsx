import React from 'react';
import Header from '@/components/NavBar';
import Documents from '@/components/Documents';
import SummaryVisualizer from '@/components/SummaryVisualizer';
import { DocumentProvider } from '@/context/DocumentContext';
import DocumentUpload from '@/components/DocumentUpload';

const Home: React.FC = () => {
    return (
        <div>
          <DocumentProvider>
          <Header />
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
              <DocumentUpload />
              <Documents />
              <SummaryVisualizer />
            </div>
          </DocumentProvider>
        </div>
    );
};

export default Home;