import { NextRequest, NextResponse } from 'next/server';

// Proxy requests to MinIO
export async function PUT(request: NextRequest) {
  try {
    // Get MinIO URL from x-minio-url header
    const minioUrl = request.headers.get('x-minio-url');
    
    console.log('Proxy request URL:', request.url);
    console.log('MinIO URL from header:', minioUrl);
    console.log('All headers:', Object.fromEntries(request.headers.entries()));
    
    if (!minioUrl || minioUrl === 'undefined' || minioUrl === 'null') {
      console.error('Invalid x-minio-url header:', minioUrl);
      return NextResponse.json({ error: 'Missing or invalid x-minio-url header' }, { status: 400 });
    }

    // Replace localhost with minio hostname for container network
    const containerMinioUrl = minioUrl.replace('http://localhost:9000', 'http://minio:9000');
    console.log('Container MinIO URL:', containerMinioUrl);

    // Forward the PUT request to MinIO
    const body = await request.arrayBuffer();
    console.log('Request body size:', body.byteLength);
    
    const response = await fetch(containerMinioUrl, {
      method: 'PUT',
      headers: {
        'Content-Type': request.headers.get('Content-Type') || 'application/octet-stream',
      },
      body,
    });

    console.log('MinIO response status:', response.status);

    if (response.ok) {
      return new NextResponse(null, { status: 200 });
    } else {
      const error = await response.text();
      console.error('MinIO error:', error);
      return NextResponse.json({ error }, { status: response.status });
    }
  } catch (error: any) {
    console.error('MinIO proxy error:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}