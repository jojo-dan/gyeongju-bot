// VPS 웹 API 프록시 — 웹앱에서 포저와 대화
// VPS의 web_api.py로 요청을 중계하여 API 키와 VPS IP를 보호한다.
export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'POST만 허용' });
  }

  const VPS_API_URL = process.env.VPS_API_URL;  // e.g. http://76.13.176.32:8080
  const CHAT_SECRET = process.env.CHAT_SECRET || '';

  if (!VPS_API_URL) {
    return res.status(500).json({ error: '서버 설정 오류' });
  }

  try {
    const body = req.body || {};
    const payload = {
      message: body.message || '',
      history: body.history || [],
      secret: CHAT_SECRET,
    };

    const response = await fetch(`${VPS_API_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok) {
      return res.status(response.status).json(data);
    }

    return res.status(200).json(data);
  } catch (err) {
    console.error('VPS 프록시 에러:', err);
    return res.status(502).json({ error: '포저에게 연결할 수 없습니다. 잠시 후 다시 시도해주세요.' });
  }
}
