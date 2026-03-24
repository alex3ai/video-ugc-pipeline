// Next.js API route for fetching campaigns list
import type { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'GET') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  try {
    // Fetch campaigns from the backend API
    const backendResponse = await fetch(`${process.env.BACKEND_API_URL || 'http://localhost:8000'}/api/campaigns/`);
    
    if (!backendResponse.ok) {
      const errorData = await backendResponse.json();
      return res.status(backendResponse.status).json(errorData);
    }

    const campaigns = await backendResponse.json();
    res.status(200).json(campaigns);
  } catch (error) {
    console.error('Error fetching campaigns:', error);
    res.status(500).json({ detail: 'Internal server error' });
  }
}