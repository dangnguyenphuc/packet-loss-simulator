const PROXY_ENDPOINT = '/api/proxy/shape'

export async function fetchIp()
{
  try {
    const response = await fetch(`/api/ip`);

    if (!response.ok) {
      throw new Error(`[GET] Failed to fetch ip: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    throw new Error(`[GET] Error loading: ${error.message}`);
  }
}

export async function fetchJson(filename) {
  try {
    const response = await fetch(`/api/json/${filename}`);

    if (!response.ok) {
      throw new Error(`[GET] Failed to fetch ${filename}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    throw new Error(`[GET] Error loading ${filename}: ${error.message}`);
  }
}

export async function deleteShape(payload, endpoint = PROXY_ENDPOINT) {
  try {
    const response = await fetch(endpoint, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload)
    });
    console.log(response)
    if (!response.ok) throw new Error(`[DELETE] ${endpoint} failed: ${response.statusText}`);
    return await response;
  } catch (error) {
    throw new Error(`[DELETE] Error deleting ${endpoint}: ${error.message}`);
  }
}

export async function postShape(payload={}, endpoint = PROXY_ENDPOINT) {
  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload)
    });

    if (!response.ok) throw new Error(`[POST] ${endpoint} failed: ${response.statusText}`);
    return await response.json();
  } catch (error) {
    throw new Error(`[POST] Error posting to ${endpoint}: ${error.message}`);
  }
}

export async function applyConfig(payload= {}, delay = -1, endpoint = PROXY_ENDPOINT)
{
  // delete previous config if there's any
  try {
    deleteShape(payload, endpoint);
  }
  finally 
  {
    try {
      const res = await postShape(payload, endpoint);
      // if post success
      if (delay <= 0)
      {
        return;
      }
      // if delay > 0 then create timer to reset config to normal
      setTimeout(async () => {
        try {
          await deleteShape(payload, endpoint);
        } catch (delErr) {
          console.error('[DELETE] ', delErr.message);
        }
      }, delay);
      return;
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