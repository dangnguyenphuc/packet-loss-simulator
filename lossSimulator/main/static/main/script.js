const PROXY_ENDPOINT = '/api/proxy/shape'
export const MONITORING_INTERVAL = 10000; // in ms

export async function fetchIp()
{
    const response = await fetch(`/api/ip`);

    if (!response.ok) {
      throw new Error(`[GET] Failed to fetch ip: ${response.statusText}`);
    }

    return await response.json();
}

export async function fetchJson(filename) {
    const response = await fetch(`/api/json/${filename}`);

    if (!response.ok) {
      throw new Error(`[GET] Failed to fetch ${filename}: ${response.statusText}`);
    }

    return await response.json();
}

export async function deleteShape(payload, endpoint = PROXY_ENDPOINT) {
    const response = await fetch(endpoint, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) throw new Error(`[DELETE] ${endpoint} failed: ${response.statusText}`);
    return await response;
}

export async function postShape(payload={}, endpoint = PROXY_ENDPOINT) {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) throw new Error(`[POST] ${endpoint} failed: ${response.statusText}`);
    return await response.json();
}

export async function getShape(endpoint = PROXY_ENDPOINT, ip = "") {
    const url = ip !== "" ? `${endpoint}?ip=${ip}` : endpoint;
    const response = await fetch(endpoint, {
      method: 'GET',
    });

    if (!response.ok) throw new Error(`[GET] ${endpoint} failed: ${response.statusText} with error ${response.body.error}`);
    return await response.json();
}


export async function applyConfig(payload= {}, endpoint = PROXY_ENDPOINT)
{
  // delete previous config if there's any
  try {
    deleteShape(payload, endpoint);
  }
  finally 
  {
    try {
      const res = await postShape(payload, endpoint);
      return res;
    } 
    catch (err)
    {
      throw new Error ("[POST] Cannot post shape");
    }  
  }
}

export function convertTimerToMs(h, m, s)
{
  return (h * 3600 + m * 60 + s) * 1000;
}