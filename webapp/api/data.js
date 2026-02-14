// jsonbin.io 프록시 — API Key를 서버 사이드에서만 사용
export default async function handler(req, res) {
  const BIN_ID = process.env.JSONBIN_BIN_ID;
  const API_KEY = process.env.JSONBIN_API_KEY;

  if (!BIN_ID || !API_KEY) {
    return res.status(500).json({ error: '서버 환경 변수가 설정되지 않았습니다.' });
  }

  const url = `https://api.jsonbin.io/v3/b/${BIN_ID}/latest`;

  try {
    const response = await fetch(url, {
      headers: { 'X-Master-Key': API_KEY },
    });

    if (!response.ok) {
      return res.status(response.status).json({ error: 'jsonbin 요청 실패' });
    }

    const data = await response.json();
    res.setHeader('Cache-Control', 'no-store');
    return res.status(200).json(data);
  } catch (err) {
    return res.status(500).json({ error: '데이터를 가져올 수 없습니다.' });
  }
}
