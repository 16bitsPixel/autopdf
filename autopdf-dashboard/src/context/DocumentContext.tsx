import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

type Document = {
  id: string;
  filename: string;
};

type DocumentContextType = {
  documents: Document[];
  refreshDocuments: () => Promise<void>;
};

const DocumentContext = createContext<DocumentContextType | undefined>(undefined);

export const DocumentProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [documents, setDocuments] = useState<Document[]>([]);

  const fetchDocuments = async () => {
    try {
      const response = await axios.get('http://localhost:8000/documents/');
      setDocuments(response.data);
    } catch (error) {
      console.error('Error fetching documents:', error);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  return (
    <DocumentContext.Provider value={{ documents, refreshDocuments: fetchDocuments }}>
      {children}
    </DocumentContext.Provider>
  );
};

export const useDocumentContext = () => {
  const context = useContext(DocumentContext);
  if (!context) throw new Error('useDocumentContext must be used within a DocumentProvider');
  return context;
};
