import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = request.nextUrl;
    const limit = searchParams.get('limit') || '20';
    const offset = searchParams.get('offset') || '0';
    const status = searchParams.get('status') || '';
    
    // Build query parameters
    const params = new URLSearchParams({
      limit,
      offset
    });
    
    if (status && status !== 'all') {
      params.set('status', status);
    }
    
    // Forward request to backend
    const backendUrl = `http://api:8000/transcriptions?${params.toString()}`;
    console.log('Fetching from backend:', backendUrl);
    
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
    console.log('Backend returned data:', JSON.stringify(data, null, 2));
    console.log('Data length:', Array.isArray(data) ? data.length : 'not array');
    return NextResponse.json(data);
    
  } catch (error) {
    console.error('Error in transcriptions API route:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}