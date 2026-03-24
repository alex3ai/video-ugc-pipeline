import Head from 'next/head';
import Header from '../components/Header';
import { useEffect, useState } from 'react';

interface Job {
  id: string;
  status: string;
  created_at: string;
  video_url?: string;
}

interface Campaign {
  id: string;
  name: string;
  briefing_text: string;
  jobs: Job[];
}

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCampaigns = async () => {
      try {
        const response = await fetch('/api/campaigns-list');
        if (!response.ok) {
          throw new Error('Failed to fetch campaigns');
        }
        const data = await response.json();
        setCampaigns(data.data || []);
      } catch (err) {
        setError((err as Error).message);
      } finally {
        setLoading(false);
      }
    };

    fetchCampaigns();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="flex justify-center items-center h-screen">
          <Head>
            <title>Carregando Campanhas</title>
          </Head>
          <p>Carregando...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="flex justify-center items-center h-screen">
          <Head>
            <title>Erro</title>
          </Head>
          <p>Erro: {error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <div className="container mx-auto px-4 py-8 max-w-5xl">
        <h1 className="text-4xl font-bold mb-8 text-center">Campanhas e Jobs</h1>

        {campaigns.length === 0 ? (
          <p className="text-center text-lg bg-white p-4 rounded-lg shadow-sm">Nenhuma campanha encontrada.</p>
        ) : (
          <div className="bg-white p-4 rounded-lg shadow-sm overflow-x-auto">
            <table className="min-w-full">
              <thead>
                <tr className="bg-gray-100">
                  <th className="py-3 px-4 text-left">Nome</th>
                  <th className="py-3 px-4 text-left">Briefing</th>
                  <th className="py-3 px-4 text-left">Status</th>
                  <th className="py-3 px-4 text-left">Data de Criação</th>
                  <th className="py-3 px-4 text-left">Vídeo</th>
                </tr>
              </thead>
              <tbody>
                {campaigns.map((campaign) => (
                  <tr key={campaign.id} className="border-t border-gray-200">
                    <td className="py-3 px-4 font-medium">{campaign.name}</td>
                    <td className="py-3 px-4 max-w-xs truncate">{campaign.briefing_text.substring(0, 100)}{campaign.briefing_text.length > 100 ? '...' : ''}</td>
                    <td className="py-3 px-4">
                      {campaign.jobs.length > 0 ? (
                        <span className={`px-2 py-1 rounded-full text-xs ${
                          campaign.jobs[0].status === 'COMPLETED' ? 'bg-green-200 text-green-800' :
                          campaign.jobs[0].status === 'FAILED' || campaign.jobs[0].status === 'TIMEOUT' ? 'bg-red-200 text-red-800' :
                          campaign.jobs[0].status === 'PENDING' ? 'bg-yellow-200 text-yellow-800' :
                          'bg-blue-200 text-blue-800'
                        }`}>
                          {campaign.jobs[0].status}
                        </span>
                      ) : (
                        <span className="px-2 py-1 rounded-full text-xs bg-gray-200 text-gray-800">N/A</span>
                      )}
                    </td>
                    <td className="py-3 px-4">{campaign.jobs.length > 0 ? new Date(campaign.jobs[0].created_at).toLocaleString() : 'N/A'}</td>
                    <td className="py-3 px-4">
                      {campaign.jobs.length > 0 && campaign.jobs[0].video_url ? (
                        <a 
                          href={campaign.jobs[0].video_url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:underline"
                        >
                          Ver Vídeo
                        </a>
                      ) : campaign.jobs.length > 0 && campaign.jobs[0].status === 'COMPLETED' ? (
                        <span className="text-gray-500">Aguardando upload</span>
                      ) : (
                        <span className="text-gray-500">-</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="mt-8 text-center">
          <a 
            href="/"
            className="inline-block px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Nova Campanha
          </a>
        </div>
      </div>
      
      <footer className="mt-12 pt-8 border-t border-gray-200 text-center text-gray-600 bg-white">
        <p>© {new Date().getFullYear()} Video UGC Pipeline - Todos os direitos reservados</p>
      </footer>
    </div>
  );
}