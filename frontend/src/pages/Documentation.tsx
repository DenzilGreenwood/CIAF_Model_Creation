import React, { useState, useRef, useEffect } from 'react';
import { Search, ChevronRight, Menu, X, Download } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

// Import all documentation files
const docFiles = {
  'Quick Start': {
    'icon': '⚡',
    'items': {
      '5-Minute Flow': '/docs/01-quickstart/5min-compliance-flow.md',
      'API Authentication': '/docs/01-quickstart/api-auth.md',
      'Environment Setup': '/docs/01-quickstart/environment-setup.md',
    }
  },
  'LCM Deep Dive': {
    'icon': '🔬',
    'items': {
      'Philosophy': '/docs/02-lcm-deepdive/philosophy.md',
      'Proof Lifecycle': '/docs/02-lcm-deepdive/proof-lifecycle.md',
      'Verification Logic': '/docs/02-lcm-deepdive/verification-logic.md',
    }
  },
  'Industry Frameworks': {
    'icon': '🏢',
    'items': {
      'Policy Mapping Guide': '/docs/03-industry-frameworks/policy-mapping-guide.md',
    }
  },
  'Observability': {
    'icon': '📊',
    'items': {
      'Dashboard Guide': '/docs/04-observability/dashboard-guide.md',
    }
  },
  'Auditor\'s View': {
    'icon': '⚖️',
    'items': {
      'Manual Verification': '/docs/05-auditors-view/manual-verification.md',
      'Expert Testimony': '/docs/05-auditors-view/testimony.md',
    }
  }
};

const Documentation: React.FC = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [currentDoc, setCurrentDoc] = useState<string | null>(null);
  const [content, setContent] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const searchInputRef = useRef<HTMLInputElement>(null);

  // Load markdown file
  const loadDocument = async (path: string) => {
    setLoading(true);
    try {
      const response = await fetch(path);
      const text = await response.text();
      setContent(text);
      setCurrentDoc(path);
      setSearchQuery('');
      setSearchResults([]);
    } catch (error) {
      console.error('Error loading document:', error);
      setContent('# Error\n\nFailed to load document. Please check the file path.');
    } finally {
      setLoading(false);
    }
  };

  // Search functionality
  const handleSearch = (query: string) => {
    setSearchQuery(query);

    if (!query.trim()) {
      setSearchResults([]);
      return;
    }

    const results = [];
    const lowerQuery = query.toLowerCase();

    Object.entries(docFiles).forEach(([category, section]) => {
      Object.entries(section.items as Record<string, string>).forEach(([title, path]) => {
        if (title.toLowerCase().includes(lowerQuery) || category.toLowerCase().includes(lowerQuery)) {
          results.push({
            title,
            category,
            path,
            icon: section.icon
          });
        }
      });
    });

    setSearchResults(results.slice(0, 10)); // Limit to 10 results
  };

  // Export to PDF (simple text export)
  const exportToPDF = () => {
    const element = document.getElementById('doc-content');
    if (!element) return;

    const text = element.innerText;
    const blob = new Blob([text], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `ciaf-doc-${Date.now()}.txt`;
    link.click();
  };

  return (
    <div className="flex h-[calc(100vh-64px)] bg-white dark:bg-gray-900">
      {/* Sidebar */}
      <div
        className={`${
          sidebarOpen ? 'w-64' : 'w-0'
        } bg-gray-50 dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 transition-all duration-300 overflow-hidden flex flex-col`}
      >
        {/* Search */}
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="relative">
            <Search className="absolute left-2 top-3 text-gray-400" size={18} />
            <input
              ref={searchInputRef}
              type="text"
              placeholder="Search docs..."
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
              className="w-full pl-8 pr-3 py-2 rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
            />
          </div>
        </div>

        {/* Search Results or Navigation */}
        <div className="flex-1 overflow-y-auto">
          {searchResults.length > 0 ? (
            <div className="p-4">
              <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 mb-3">Search Results</p>
              {searchResults.map((result) => (
                <button
                  key={result.path}
                  onClick={() => loadDocument(result.path)}
                  className="w-full text-left px-3 py-2 mb-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition"
                >
                  <p className="text-sm font-medium text-gray-900 dark:text-white">{result.title}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">{result.category}</p>
                </button>
              ))}
            </div>
          ) : (
            <nav className="p-4 space-y-6">
              {Object.entries(docFiles).map(([category, section]) => (
                <div key={category}>
                  <p className="text-xs font-bold text-gray-500 dark:text-gray-400 uppercase mb-3">
                    {section.icon} {category}
                  </p>
                  <div className="space-y-2">
                    {Object.entries(section.items as Record<string, string>).map(([title, path]) => (
                      <button
                        key={path}
                        onClick={() => loadDocument(path)}
                        className={`w-full text-left px-3 py-2 rounded text-sm transition ${
                          currentDoc === path
                            ? 'bg-blue-100 dark:bg-blue-900 text-blue-900 dark:text-blue-100 font-medium'
                            : 'text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700'
                        }`}
                      >
                        {title}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </nav>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Top Bar */}
        <div className="border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 px-6 py-4 flex items-center justify-between">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition"
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>

          {currentDoc && (
            <button
              onClick={exportToPDF}
              className="flex items-center gap-2 px-4 py-2 rounded bg-blue-600 text-white hover:bg-blue-700 transition text-sm"
            >
              <Download size={16} />
              Export
            </button>
          )}
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto">
          {loading ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-gray-500 dark:text-gray-400">Loading...</div>
            </div>
          ) : currentDoc ? (
            <div
              id="doc-content"
              className="max-w-4xl mx-auto px-8 py-8 prose dark:prose-invert prose-sm sm:prose lg:prose-lg"
            >
              <ReactMarkdown
                components={{
                  h1: ({ node, ...props }) => <h1 className="text-4xl font-bold mt-8 mb-4 text-gray-900 dark:text-white" {...props} />,
                  h2: ({ node, ...props }) => <h2 className="text-3xl font-bold mt-6 mb-3 text-gray-900 dark:text-white border-b border-gray-200 dark:border-gray-700 pb-2" {...props} />,
                  h3: ({ node, ...props }) => <h3 className="text-2xl font-bold mt-5 mb-2 text-gray-900 dark:text-white" {...props} />,
                  p: ({ node, ...props }) => <p className="text-gray-700 dark:text-gray-300 mb-4 leading-relaxed" {...props} />,
                  ul: ({ node, ...props }) => <ul className="list-disc list-inside space-y-2 mb-4 text-gray-700 dark:text-gray-300" {...props} />,
                  ol: ({ node, ...props }) => <ol className="list-decimal list-inside space-y-2 mb-4 text-gray-700 dark:text-gray-300" {...props} />,
                  code: ({ node, inline, ...props }) => {
                    if (inline) {
                      return <code className="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded text-red-600 dark:text-red-400 font-mono text-sm" {...props} />;
                    }
                    return <code className="block bg-gray-100 dark:bg-gray-800 p-4 rounded overflow-x-auto text-sm font-mono text-gray-900 dark:text-gray-100 mb-4" {...props} />;
                  },
                  pre: ({ node, ...props }) => <pre className="bg-gray-100 dark:bg-gray-800 p-4 rounded overflow-x-auto mb-4" {...props} />,
                  blockquote: ({ node, ...props }) => <blockquote className="border-l-4 border-blue-400 pl-4 italic text-gray-600 dark:text-gray-400 my-4" {...props} />,
                  table: ({ node, ...props }) => <table className="w-full border-collapse border border-gray-300 dark:border-gray-600 mb-4" {...props} />,
                  td: ({ node, ...props }) => <td className="border border-gray-300 dark:border-gray-600 px-4 py-2" {...props} />,
                  th: ({ node, ...props }) => <th className="border border-gray-300 dark:border-gray-600 px-4 py-2 bg-gray-100 dark:bg-gray-700 font-bold" {...props} />,
                }}
              >
                {content}
              </ReactMarkdown>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-gray-500 dark:text-gray-400">
              <ChevronRight size={48} className="mb-4 opacity-50" />
              <p className="text-lg">Select a document from the sidebar to get started</p>
              <p className="text-sm mt-2">Browse documentation for CIAF setup, API usage, and compliance guides</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Documentation;
