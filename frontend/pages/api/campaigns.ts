// Next.js API route for submitting campaigns
import type { NextApiRequest, NextApiResponse } from 'next';

// In a real implementation, this would connect to your backend API
// For now, we're simulating the request to the backend service

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ message: 'Method not allowed' });
  }

  const { name, briefing_text } = req.body;

  if (!name || typeof name !== 'string') {
    return res.status(400).json({ detail: 'Campaign name is required and must be a string' });
  }

  if (!briefing_text || typeof briefing_text !== 'string') {
    return res.status(400).json({ detail: 'Briefing text is required and must be a string' });
  }

  if (briefing_text.length < 50 || briefing_text.length > 2000) {
    return res.status(400).json({ detail: 'Briefing text must be between 50 and 2000 characters' });
  }

  try {
    // Forward the request to the backend API
    const backendResponse = await fetch(`${process.env.BACKEND_API_URL || 'http://localhost:8000'}/api/campaigns/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name, briefing_text }),
    });

    if (!backendResponse.ok) {
      const errorData = await backendResponse.json();
      return res.status(backendResponse.status).json(errorData);
    }

    const data = await backendResponse.json();
    res.status(201).json(data);
  } catch (error) {
    console.error('Error submitting campaign:', error);
    res.status(500).json({ detail: 'Internal server error' });
  }
}