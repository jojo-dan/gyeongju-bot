// jsonbin.io PUT 프록시 — 관리자 모드 저장용
export default async function handler(req, res) {
  if (req.method !== 'PUT') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const BIN_ID = process.env.JSONBIN_BIN_ID;
  const API_KEY = process.env.JSONBIN_API_KEY;

  if (!BIN_ID || !API_KEY) {
    return res.status(500).json({ error: '서버 환경 변수가 설정되지 않았습니다.' });
  }

  const url = `https://api.jsonbin.io/v3/b/${BIN_ID}`;

  try {
    const response = await fetch(url, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'X-Master-Key': API_KEY,
      },
      body: JSON.stringify(req.body),
    });

    if (!response.ok) {
      return res.status(response.status).json({ error: 'jsonbin 저장 실패' });
    }

    const data = await response.json();
    return res.status(200).json(data);
  } catch (err) {
    return res.status(500).json({ error: '데이터를 저장할 수 없습니다.' });
  }
}
