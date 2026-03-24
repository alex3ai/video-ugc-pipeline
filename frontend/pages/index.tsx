import Head from 'next/head';
import Header from '../components/Header';
import { useState } from 'react';

export default function Home() {
  const [campaignName, setCampaignName] = useState('');
  const [briefingText, setBriefingText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage('');

    try {
      const response = await fetch('/api/campaigns', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: campaignName, briefing_text: briefingText }),
      });

      if (response.ok) {
        setMessage('Campanha criada com sucesso!');
        setBriefingText('');
      } else {
        const errorData = await response.json();
        setMessage(`Erro: ${errorData.detail || 'Falha ao criar campanha'}`);
      }
    } catch (error) {
      setMessage(`Erro: ${(error as Error).message || 'Falha ao criar campanha'}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="container mx-auto px-4 py-8 max-w-3xl">
        <h1 className="text-4xl font-bold mb-8 text-center">Video UGC Pipeline</h1>
        
        <p className="text-lg mb-8 text-center">
          Submeta seu briefing para geração automática de vídeos personalizados
        </p>
        
        <form onSubmit={handleSubmit} className="w-full max-w-2xl bg-white p-6 rounded-lg shadow-md">
          <div className="mb-6">
            <label htmlFor="campaignName" className="block text-lg font-medium mb-2">
              Nome da Campanha
            </label>
            <input
              id="campaignName"
              type="text"
              value={campaignName}
              onChange={(e) => setCampaignName(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Ex: Campanha Verão 2026"
              required
            />
          </div>

          <div className="mb-6">
            <label htmlFor="briefingText" className="block text-lg font-medium mb-2">
              Briefing do Vídeo
            </label>
            <textarea
              id="briefingText"
              value={briefingText}
              onChange={(e) => setBriefingText(e.target.value)}
              rows={6}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Descreva detalhadamente o que você deseja no vídeo..."
              required
              minLength={50}
              maxLength={2000}
            />
            <p className="mt-1 text-sm text-gray-500">
              O briefing deve ter entre 50 e 2000 caracteres.
            </p>
          </div>
          
          <button
            type="submit"
            disabled={isLoading}
            className={`w-full py-3 px-4 rounded-lg text-white font-semibold ${
              isLoading ? 'bg-blue-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {isLoading ? 'Processando...' : 'Gerar Vídeo'}
          </button>
        </form>
        
        {message && (
          <div className={`mt-6 p-4 rounded-lg w-full max-w-2xl text-center ${
            message.includes('Erro') ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
          }`}>
            {message}
          </div>
        )}
      </main>

      <footer className="mt-12 pt-8 border-t border-gray-200 text-center text-gray-600 bg-white">
        <p>© {new Date().getFullYear()} Video UGC Pipeline - Todos os direitos reservados</p>
      </footer>
    </div>
  );
}