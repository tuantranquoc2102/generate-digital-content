import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const crawlerId = params.id;
    
    // Forward request to backend
    const backendUrl = `http://api:8000/channel/crawler/${crawlerId}`;
    console.log('Fetching channel crawler:', crawlerId);
    
    const response = await fetch(backendUrl);
    
    if (!response.ok) {
      console.error('Backend response not ok:', response.status, response.statusText);
      const errorText = await response.text();
      console.error('Backend error details:', errorText);
      return NextResponse.json(
        { error: `Backend error: ${response.status} ${response.statusText}` },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    return NextResponse.json(data);
    
  } catch (error) {
    console.error('Error in channel crawler status API route:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}